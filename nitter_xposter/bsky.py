import logging
import atproto
from typing import Optional
from atproto import Client
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
            facets=None
        )
        return True
    except Exception as e:
        # TODO: handle error
        logging.error("Error sending to bsky, aborting: " + str(e))
        return False
