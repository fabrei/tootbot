# TootBot

This is a fork project with some improvements.

A small python 3.x script to replicate tweets on a mastodon account.
It was tested with python 3.6.10

The script only needs a password for the first time to create credential files.

It gets the tweets from RSS available at http://twitrss.me, then does some cleanup on the content:
- twitter tracking links (t.co) are dereferenced
- twitter hosted pictures are retrieved and uploaded to mastodon

It can also toot RSS/atom feeds (see cron-example.sh).

A sqlite database is used to keep track of tweets than have been tooted.

The script is simply called by a cron job and can run on any server (does not have to be on the mastodon instance server).

## Setup

```
# clone this repo
git clone https://github.com/fabrei/tootbot.git
cd tootbot

# install required python modules
pip3 install -r requirements.txt
```

## Useage

```
usage: tootbot.py [-h] --operation {init,toot} --username USERNAME --instance
                  INSTANCE [--source SOURCE] [--days DAYS]
                  [--tags TAGS [TAGS ...]] [--delay DELAY]

optional arguments:
  -h, --help            show this help message and exit
  --operation {init,toot}
                        specify operation to do.
  --username USERNAME   username to login to mastodon.
  --instance INSTANCE   a mastodon instance where the username is hosted.
  --source SOURCE       twitter username to toot to mastodon.
  --days DAYS           process only unprocessed tweets less than days old.
  --tags TAGS [TAGS ...]
                        list of tags to append to toot.
  --delay DELAY         process only unprocessed tweets less than days old and
                        after a delay.
```

If you run it with `--operation init` it will ask you for the password of the account. Password is not displayed in the shell. After it, the script uses the created credential files from init operation.

## Examples

```
# init example
python3 tootbot.py --operation init --username my_username@mastodon --instance mastodon.social
# toot example
python3 tootbot.py --operation toot --username my_username@mastodon --instance mastodon.social --source any_twitter_account --tags #some #tags #to #append
# rss/atom feeds example
python3 tootbot.py --operation toot --username my_username@mastodon --instance mastodon.social --source https://www.data.gouv.fr/fr/datasets/recent.atom --days 2 --tags #dataset #opendata #datagouvfr
```
