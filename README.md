# nitter-xposter
Crosspost from Twitter to Mastodon (based on Nitter)

## ⚠️ PSA
It is increasingly [hard](https://github.com/zedeus/nitter/issues/983) to use and host a public Nitter instance.

As a result, it is probably not a good idea to use it with a public Nitter instance.

When it's ready, please check out [sekai-soft/freebird](https://github.com/sekai-soft/freebird) for a guide on how to self-host your own Nitter instance alongside `nitter-xposter`.

## Notice
* Twitter crawling is based on Nitter, so only public accounts are supported.
* Supported tweet types
- [x] Text
- [x] Retweet
- [x] Image
- [ ] Video

## Usage
The easiest way to use this program is to run it as a docker compose service on your NAS or a VPS.

### Obtain Mastodon credentials
You need to create a developer application on your Mastodon instance first

1. Go to `https://<your-mastodon-instance>/settings/applications/new`
2. On the form, put `nitter-xposter` for `Application name`
3. Under `Scopes`, uncheck `read`, `write` and `follow` checkboxes. Check `write:media` and `write:statuses` checkboxes.
4. Click `Submit`
5. Go to `https://<your-mastodon-instance>/settings/applications` and click the `nitter-xposter` application you just created
6. You will need the following
    * `Client key`
    * `Client secret`
    * `Your access token`

After obtaining the credentials, you can use the following `docker-compose.yml` to run the program
```yaml
version: '3'
services:
  app:
    image: ghcr.io/k-t-corp/nitter-xposter:latest
    volumes:
      - ./dbs:/app/dbs
#      - ./post.sh:/app/post.sh  # you can optionally mount a shell script at /app/post.sh to run after every Nitter crawl to perform tasks such as sending a heartbeat
    environment:
      SQLITE_FILE: /app/dbs/db.db
      NITTER_HOST: <ENTER YOUR NITTER HOST HERE>
      NITTER_HTTPS: <'true' OR 'false'>  # by default 'true'; set to 'false' if your Nitter instance does not support https
      TWITTER_HANDLE: <REPLACE WITH YOUR TWITTER USERNAME, WITHOUT @>
      MASTODON_HOST: <REPLACE WITH YOUR MASTODON INSTANCE, e.g. mastodon.ktachibana.party>
      MASTODON_CLIENT_ID: <REPLACE WITH YOUR MASTODON CLIENT KEY>
      MASTODON_CLIENT_SECRET: <REPLACE WITH YOUR MASTODON CLIENT SECRET>
      MASTODON_ACCESS_TOKEN: <REPLACE WITH YOUR MASTODON ACCESS TOKEN>
      MASTODON_STATUS_LIMIT: '10'  # set the maximum of statuses to be posted at once
    restart: always
```

This will crawl the Nitter RSS for your Twitter username every 5 minutes, and crosspost the tweets to your Mastodon account.

## Development
### Run unit tests
```shell
python -m unittest discover
```
