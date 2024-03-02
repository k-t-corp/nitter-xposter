import logging
import atproto
from typing import Optional
from atproto import Client, client_utils
from urlextract import URLExtract
from .parsed_entry import ParsedEntry


def upload_media_to_bsky(image_file: str, logged_in_client: Client) -> Optional['atproto.models.ComAtprotoRepoUploadBlob.Data']:
    logging.info("Uploading image to Bsky: " + image_file)
    try:
        with open(image_file, 'rb') as f:
            img_data = f.read()
            return logged_in_client.com.atproto.repo.upload_blob(img_data)
    except Exception as e:
        # TODO: handle error
        logging.error("Error post media to bsky, aborting: " + str(e))
        return None

UrlMaxLength = 30
UrlOverflowPlaceholder = "..."


def truncate_url(url: str) -> str:
    if len(url) < UrlMaxLength - len(UrlOverflowPlaceholder):
        return url
    return url[: UrlMaxLength - len(UrlOverflowPlaceholder)] + UrlOverflowPlaceholder


BskyTextMaxLength = 300


def post_to_bsky(parsed_entry: ParsedEntry, logged_in_client: Client):
    def blob_to_image(blob: 'atproto.models.ComAtprotoRepoUploadBlob.Response') -> 'atproto.models.AppBskyEmbedImages.Image':
        return atproto.models.AppBskyEmbedImages.Image(
            alt='',
            image=blob.blob,
        )

    status_text = ''

    if parsed_entry.text:
        status_text += parsed_entry.text

    if parsed_entry.rt:
        status_text += f"\nRT: {parsed_entry.rt}"

    tb = client_utils.TextBuilder()
    extracted_urls = URLExtract().find_urls(status_text, get_indices=True)
    prev_url_end = -1
    for extracted_url in extracted_urls:
        (url, (start, end)) = extracted_url
        tb.text(status_text[prev_url_end + 1: start])
        tb.link(truncate_url(url), url)
        prev_url_end = end
    tb.text(status_text[prev_url_end + 1:])

    status_text = tb.build_text()[: BskyTextMaxLength]
    logging.info("Sending to Bsky: " + status_text)
    try:
        logged_in_client.send_post(
            text=status_text,
            profile_identify=None,
            reply_to=None,
            embed=atproto.models.AppBskyEmbedImages.Main(
                images=[blob_to_image(blob) for blob in parsed_entry.bsky_blobs]
            ),
            # TODO: should probably add langs??
            langs=None,
            # TODO: what will happen if status_text overflowed and there are facets that are cut off?
            facets=tb.build_facets()
        )
        return True
    except Exception as e:
        # TODO: handle error
        logging.error("Error sending to bsky, aborting: " + str(e))
        return False
