import logging
from mastodon import Mastodon
from typing import Optional
from .parsed_entry import ParsedEntry


def upload_media_to_mastodon(image_file: str, mastodon: Mastodon) -> Optional[str]:
    logging.info("Uploading image to Mastodon: " + image_file)
    try:
        media = mastodon.media_post(image_file)
    except Exception as e:
        # TODO: handle error
        logging.error("Error post media to Mastodon, aborting: " + str(e))
        return None
    if 'id' not in media:
        logging.error("Weird, id not found in media uploaded to Mastodon, aborting: " + image_file)
        return None
    return media['id']


def post_to_mastodon(parsed_entry: ParsedEntry, mastodon: Mastodon) -> bool:
    status_text = ''

    if parsed_entry.text:
        status_text += parsed_entry.text

    if parsed_entry.rt:
        status_text += f"\nRT: {parsed_entry.rt}"

    logging.info("Sending to Mastodon: " + status_text)
    try:
        mastodon.status_post(status=status_text, media_ids=parsed_entry.mastodon_media_ids)
        return True
    except Exception as e:
        # TODO: handle error
        logging.error("Error sending to Mastodon, aborting: " + str(e))
        return False
