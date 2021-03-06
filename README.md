# TootBot

This is a fork project with some improvements.

A small python 3.x script to replicate tweets on a mastodon account.
It was tested with python 3.6.10

The script only needs a password for the first time to create credential files.

It gets the tweets from RSS available at https://nitter.net/<username>/rss, then does some cleanup on the content:
- twitter tracking links (t.co) are dereferenced
- twitter hosted pictures are retrieved and uploaded to mastodon

The service http://twitrss.me , which was used before, has some problems to create rss feeds from tweets.

It can also toot RSS/atom feeds, just pass RSS/atom url as source.

A sqlite database is used to keep track of tweets than have been tooted.

The script is simply called by a cron job and can run on any server (does not have to be on the mastodon instance server).

## Setup Python

```
# clone this repo
git clone https://github.com/fabrei/tootbot.git
cd tootbot

# install required python modules
pip3 install -r requirements.txt
```

## Setup Podman/Dockker
Clone the repo and do some changes in `build.sh`, `create.sh` and `systemd.sh`. It was tested with rootless podman 1.9.1.

To run the container as a systemd service with podman, call systemd.sh after previous changes and systemd dir exists. It copies a service file under systemd/ with the option User and Group of the user you logged in as. After it you have to do the following to enable the unit.

```
sudo cp systemd/container-<container-name>.service /etc/systemd/system/
sudo systemctl enable container-<container-name>.service
sudo systemctl start container-<container-name>.service
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
  --rootpath ROOTPATH   rootpath to tootbot.py
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

Db file and credential files are stored into data/ . Be sure it exists.

## Examples

```
# init example
python3 tootbot.py --operation init --rootpath /opt/tootbot --username my_username@mastodon --instance mastodon.social
# toot example
python3 tootbot.py --operation toot --rootpath /opt/tootbot --username my_username@mastodon --instance mastodon.social --source any_twitter_account --tags #some #tags #to #append
# rss/atom feeds example
python3 tootbot.py --operation --rootpath /opt/tootbot toot --username my_username@mastodon --instance mastodon.social --source https://www.data.gouv.fr/fr/datasets/recent.atom --days 2 --tags #dataset #opendata #datagouvfr
```
