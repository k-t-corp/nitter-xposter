import os
import tempfile
import requests
import feedparser
import html
import logging
from typing import Optional, List
from dataclasses import dataclass
from bs4 import BeautifulSoup
from mastodon import Mastodon
from urllib.parse import urlparse, urlunparse
from atproto import Client
from .db import setup_database, get_last_position, set_last_position
from .mastodon import upload_media_to_mastodon, post_to_mastodon
from .bsky import upload_media_to_bsky, post_to_bsky
from .parsed_entry import ParsedEntry


@dataclass
class XpostConfig:
    sqlite_file: str
    nitter_host: str
    nitter_https: bool
    twitter_handle: str
    mastodon_host: Optional[str]
    mastodon_client_id: Optional[str]
    mastodon_client_secret: Optional[str]
    mastodon_access_token: Optional[str]
    mastodon_status_limit: int
    bsky_handle: Optional[str]
    bsky_password: Optional[str]
    bsky_status_limit: int

    def is_mastodon(self):
        return self.mastodon_host \
            and self.mastodon_client_id \
                and self.mastodon_client_secret \
                    and self.mastodon_access_token

    def is_bsky(self):
        return self.bsky_handle and self.bsky_password


def convert_description_to_text(description, nitter_host):
    # Use BeautifulSoup to parse the HTML content
    soup = BeautifulSoup(description, "html.parser")

    # Find all anchor tags and replace them with their URL
    for a in soup.find_all('a'):
        if a.has_attr('href'):
            href = a['href']
            parsed_href = urlparse(href)
            if parsed_href.netloc == nitter_host:
                # nitter replaces Twitter links such as hashtags with (http) nitter links, but we want canonical twitter links
                # so that a user can choose to use Twitter as-is,
                # or uses an alternative frontend redirecting extension that redirects to another nitter instance of their choice
                parsed_href = parsed_href._replace(netloc='twitter.com')
                parsed_href = parsed_href._replace(scheme='https')
            a.replace_with(urlunparse(parsed_href))

    # Extract text, which now includes URLs in place of anchor tags
    text = soup.get_text()

    # Convert HTML entities to normal text
    text = html.unescape(text)

    return text


def find_images_in_description(description):
    # Use BeautifulSoup to parse the HTML content
    soup = BeautifulSoup(description, "html.parser")

    # Find all image tags and return their URLs
    image_urls = []
    for img in soup.find_all('img'):
        if img.has_attr('src'):
            image_urls.append(img['src'])

    return image_urls


def download_image_to_tmp_file(url: str) -> Optional[str]:
    # TODO: assumes nitter uses jpg?
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
        logging.info("Downloading image from nitter: " + url)
        res = requests.get(url)
        if res.status_code >= 400:
            logging.error("Image downloading encountered with >= 400 status code, aborting: " + url)
            return None
        f.write(res.content)
        return f.name


def parse_feed_entry(entry, twitter_handle, nitter_host: str) -> ParsedEntry:
    parsed_entry = ParsedEntry(entry.id, None, None, [], [], [], [])
    if entry.description:
        # Parse text
        text = convert_description_to_text(entry.description, nitter_host)
        parsed_entry.text = text

        # Parse images
        parsed_entry.image_urls = find_images_in_description(entry.description)

    if entry.author and entry.author != f"@{twitter_handle}" and entry.link:
        # Parse RT
        # nitter replaces RT links with (http) nitter links, but we want canonical twitter links
        # so that a user can choose to use Twitter as-is,
        # or uses an alternative frontend redirecting extension that redirects to another nitter instance of their choice
        rt = entry.link
        parsed_rt = urlparse(rt)
        parsed_rt = parsed_rt._replace(netloc='twitter.com')
        parsed_rt = parsed_rt._replace(scheme='https')
        parsed_entry.rt = urlunparse(parsed_rt)

    return parsed_entry


def cleanup_tmp_file(image_file: str):
    print(f"Cleaning up tmp file {image_file}")
    os.remove(image_file)


def xpost(config: XpostConfig):
    logging.info("Started crosspost")
    setup_database(config.sqlite_file)

    # Determine target social network to crosspost to
    if config.is_mastodon() and not config.is_bsky():
        mastodon = Mastodon(
            client_id=config.mastodon_client_id,
            client_secret=config.mastodon_client_secret,
            access_token=config.mastodon_access_token,
            api_base_url=f"https://{config.mastodon_host}"
        )
    elif config.is_bsky() and not config.is_mastodon():
        bsky = Client()
        bsky.login(config.bsky_handle, config.bsky_password)
    else:
        raise Exception("Must specify either Mastodon or bsky credentials. Cannot specify both or neither.")

    # Parsing the RSS feed
    if config.nitter_https:
        rss_url = f"https://{config.nitter_host}/{config.twitter_handle}/rss"
    else:
        rss_url = f"http://{config.nitter_host}/{config.twitter_handle}/rss"
    try:
        res = requests.get(rss_url)
    except Exception as e:
        # TODO: handle error
        logging.error("Error retrieving tweets, aborting: " + str(e))
        return 
    feed = feedparser.parse(res.text)

    parsed_entries = []  # type: List[ParsedEntry]
    if feed.bozo == 0:
        for entry in feed.entries:
            parsed_entry = parse_feed_entry(entry, config.twitter_handle, config.nitter_host)
            parsed_entries.append(parsed_entry)
    else:
        raise feed.bozo_exception
    
    if not parsed_entries:
        # TODO: handle case. might be locked account? might be nitter down?
        logging.info("No RSS entries found in feed")
        return

    # Go over parsed entries and figure out if there is an entry that matches last position
    last_position = get_last_position(config.sqlite_file, rss_url)
    last_position_index = -1
    for index, parsed_entry in enumerate(parsed_entries):
        if last_position == parsed_entry.id:
            last_position_index = index
            break

    # If last position is already lastest or cannot be found in the feed (assume just started tracking), set last position to the newest entry and quit
    if last_position_index in (0, -1):
        logging.info("Finished crosspost. Last position is already latest or cannot be found in the feed")
        set_last_position(config.sqlite_file, rss_url, parsed_entries[0].id)
        return

    new_position_index = last_position_index - 1
    for i in range(new_position_index, max(-1, new_position_index - config.mastodon_status_limit), -1):
        parsed_entry = parsed_entries[i]
        
        # Download image files for entry
        failed_to_download_any = False
        for image_url in parsed_entry.image_urls:
            image_file = download_image_to_tmp_file(image_url)
            if not image_file:
                failed_to_download_any = True
                break
            parsed_entries[i].image_files.append(image_file)

        if failed_to_download_any:
            break
        
        if config.is_mastodon():
            # Upload image files for mastodon
            failed_to_upload_any = False
            for image_file in parsed_entry.image_files:
                media_id = upload_media_to_mastodon(image_file, mastodon)
                if not media_id:
                    failed_to_upload_any = True
                    break
                parsed_entries[i].mastodon_media_ids.append(media_id)
            
            if failed_to_upload_any:
                break

            # Send mastodon statuses
            if not post_to_mastodon(parsed_entry, mastodon):
                break

        elif config.is_bsky():
            # Upload image files for bsky
            failed_to_upload_any = False
            for image_file in parsed_entry.image_files:
                blob = upload_media_to_bsky(image_file, bsky)
                if not blob:
                    failed_to_upload_any = True
                    break
                parsed_entries[i].bsky_blobs.append(blob)
            
            if failed_to_upload_any:
                break

            # Send bsky statuses
            if not post_to_bsky(parsed_entry, bsky):
                break

        new_position_index = i

    # Set last position to the newest entry
    set_last_position(config.sqlite_file, rss_url, parsed_entries[new_position_index].id)

    # Clean up image files
    for parsed_entry in parsed_entries:
        for image_file in parsed_entry.image_files:
            cleanup_tmp_file(image_file)
    logging.info("Finished crosspost")
