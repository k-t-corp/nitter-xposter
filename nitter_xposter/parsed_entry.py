import atproto
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class ParsedEntry:
    id: str
    text: Optional[str]
    rt: Optional[str]
    image_urls: List[str]
    image_files: List[str]
    mastodon_media_ids: List[str]
    bsky_blobs: List["atproto.models.ComAtprotoRepoUploadBlob.Response"]
