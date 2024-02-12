import os
from nitter_xposter.xposter import xpost, XpostConfig


def env_or_bust(env: str):
    if env not in os.environ:
        raise Exception(f"Environment {env} is not set")
    return os.environ[env]


if __name__ == "__main__":
    xpost_config = XpostConfig(
        sqlite_file=env_or_bust('SQLITE_FILE'),
        nitter_host=env_or_bust('NITTER_HOST'),
        nitter_https=bool(os.environ.get('NITTER_HTTPS', 'true') == 'true'),
        twitter_handle=env_or_bust('TWITTER_HANDLE'),
        mastodon_host=env_or_bust('MASTODON_HOST'),
        mastodon_client_id=env_or_bust('MASTODON_CLIENT_ID'),
        mastodon_client_secret=env_or_bust('MASTODON_CLIENT_SECRET'),
        mastodon_access_token=env_or_bust('MASTODON_ACCESS_TOKEN'),
        mastodon_status_limit=int(env_or_bust('MASTODON_STATUS_LIMIT'))
    )
    xpost(xpost_config)
