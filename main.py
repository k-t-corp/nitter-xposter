import os
from nitter_xposter.xposter import xpost, XpostConfig


def env_or_bust(env: str):
    if env not in os.environ:
        raise Exception(f"Environment {env} is not set")
    return os.environ[env]

DEFAULT_CROSSPOST_LIMIT = 10


if __name__ == "__main__":
    xpost_config = XpostConfig(
        sqlite_file=env_or_bust('SQLITE_FILE'),
        nitter_host=env_or_bust('NITTER_HOST'),
        nitter_https=bool(os.environ.get('NITTER_HTTPS', 'true') == 'true'),
        twitter_handle=env_or_bust('TWITTER_HANDLE'),
        mastodon_host=os.getenv('MASTODON_HOST', None),
        mastodon_client_id=os.getenv('MASTODON_CLIENT_ID', None),
        mastodon_client_secret=os.getenv('MASTODON_CLIENT_SECRET', None),
        mastodon_access_token=os.getenv('MASTODON_ACCESS_TOKEN', None),
        mastodon_status_limit=int(os.getenv('MASTODON_STATUS_LIMIT', str(DEFAULT_CROSSPOST_LIMIT))),
        bsky_handle=os.getenv('BSKY_HANDLE', None),
        bsky_password=os.getenv('BSKY_PASSWORD', None),
        bsky_status_limit=int(os.getenv('BSKY_STATUS_LIMIT', str(DEFAULT_CROSSPOST_LIMIT))),
    )
    xpost(xpost_config)
