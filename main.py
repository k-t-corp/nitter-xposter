from nitter_xposter.xposter import xpost, XpostConfig

if __name__ == "__main__":
    xpost_config = XpostConfig(
        sqlite_file="db.db",
        nitter_host="nitter.ktachibana.party",
        twitter_handle="KTachibana_M",
        mastodon_host="mastodon.ktachibana.party",
        mastodon_client_id="1Y6t60OVD_uvnBqbLwKJjA3fdSUO340hW1owyBHx_x4",
        mastodon_client_secret="rB7ZxLQvicr7W9P_ulPNbI7AbujmH3bb8uDqqJntKVE",
        mastodon_access_token="2BJENwferxJlfvt2czEz7zPyn6sdohwB-jP42Kkb7sE",
        mastodon_status_limit=10
    )
    xpost(xpost_config)
