import argparse
import re
import sqlite3
import requests
import feedparser

from getpass import getpass
from mastodon import Mastodon
from datetime import datetime, timedelta


def _parseargs() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--operation',
                        help='specify operation to do.',
                        type=str,
                        choices=['init', 'toot'],
                        required=True)
    parser.add_argument('--username',
                        help='username to login to mastodon.',
                        type=str,
                        required=True)
    parser.add_argument('--instance',
                        help='a mastodon instance where the username is '
                        'hosted.',
                        type=str,
                        required=True)
    parser.add_argument('--source',
                        help='twitter username to toot to mastodon.',
                        type=str)
    parser.add_argument('--days',
                        help='process only unprocessed tweets less than days '
                        'old.',
                        type=int,
                        default=1)
    parser.add_argument('--tags',
                        help='list of tags to append to toot.',
                        nargs='+',
                        default=[])
    parser.add_argument('--delay',
                        help='process only unprocessed tweets less than days '
                        'old and after a delay.',
                        type=int,
                        default=0)
    args = parser.parse_args()
    return args


def _create_credentials(
        api_base_url: str, app_cred_file: str, username: str,
        login_cred_file: str) -> None:
    try:
        password = getpass(prompt='Mastodon password: ')
        Mastodon.create_app(
            'tootbot',
            api_base_url=api_base_url,
            to_file=app_cred_file)

        mastodon = Mastodon(
            client_id=app_cred_file,
            api_base_url=api_base_url)

        mastodon.log_in(
            username=username,
            password=password,
            to_file=login_cred_file,
            scopes=['read', 'write'])
    except Exception as e:
        print('could not create credentials: {}'.format(e))


def _init_db(name: str) -> tuple:
    # sqlite db to store processed tweets (and corresponding toots ids)
    sql = sqlite3.connect(name)
    db = sql.cursor()
    return sql, db


def _close_db(sql: sqlite3.Connection, db: sqlite3.Cursor) -> None:
    db.close()
    sql.close()


def _get_pictures(
        feed: feedparser.FeedParserDict,
        mastodon_api: Mastodon) -> list:
    toot_media = []
    for p in re.finditer(
            r"https://nitter.net/pic/[^ \xa0\"]*", feed.summary):
        media = requests.get(p.group(0))
        media_posted = mastodon_api.media_post(
            media.content,
            mime_type=media.headers.get('content-type'))
        toot_media.append(media_posted['id'])
    return toot_media


def _replace_short_links(title: str) -> str:
    # replace short links by original URL
    m = re.search(r"http[^ \xa0]*", title)
    if m is not None:
        result = m.group(0)
        r = requests.get(result, allow_redirects=False)
        if r.status_code in [301, 302]:
            title = title.replace(result, r.headers.get('Location'))
    return title


def _remove_title_trash(title: str) -> str:
    # remove pic.twitter.com links
    # TODO: maybe this check is not needed, because nitter.net already
    # removes it.
    m = re.search(r"pic.twitter.com[^ \xa0]*", title)
    if m is not None:
        result = m.group(0)
        title = title.replace(result, ' ')

    # remove ellipsis
    return title.replace('\xa0…', ' ')


def main(
        app_cred_file: str, login_cred_file: str, api_base_url: str,
        source: str, username: str, instance: str, days: int, tags: str,
        delay: int) -> None:
    try:
        mastodon_api = Mastodon(
            client_id=app_cred_file,
            access_token=login_cred_file,
            api_base_url=api_base_url)
    except Exception as e:
        print('could not login to mastodon: {}'.format(e))
        return None

    sql, db = _init_db('data/tootbot.db')
    db.execute('''CREATE TABLE IF NOT EXISTS tweets (tweet text, toot text,
               twitter text, mastodon text, instance text)''')

    if source[:4] == 'http':
        feeds = feedparser.parse(source)
        twitter = None
    else:
        feeds = feedparser.parse(
                'https://nitter.net/{}/rss'.format(source))
        twitter = source

    for feed in reversed(feeds.entries):
        # check if this tweet has been processed
        db.execute(
            'SELECT * FROM tweets WHERE tweet = ? AND twitter = ?  '
            'and mastodon = ? and instance = ?', (
                feed.id, source, username, instance))  # noqa
        last = db.fetchone()
        dt = feed.published_parsed
        age = datetime.now() - datetime(
            dt.tm_year, dt.tm_mon, dt.tm_mday,
            dt.tm_hour, dt.tm_min, dt.tm_sec)
        # process only unprocessed tweets less than 1 day old, after delay
        if last is None and age < timedelta(days=days) \
                and age > timedelta(days=delay):

            title = feed.title
            if twitter and feed.author.lower() != ('(@%s)' % twitter).lower():
                title = 'RT https://nitter.net/{}\n{}'.format(
                    feed.author, title)

            # get the pictures...
            toot_media = _get_pictures(feed, mastodon_api)

            title = _replace_short_links(title)

            title = _remove_title_trash(title)

            if twitter is None:
                title = '{}\nSource: {}\n\n{}'.format(
                    title, feed.authors[0].name, feed.link)

            # tags is empty or a string list of tags
            title = '{}{}'.format(title, tags)
            toot = mastodon_api.status_post(title, in_reply_to_id=None,
                                            media_ids=toot_media,
                                            sensitive=False,
                                            visibility='public',
                                            spoiler_text=None)
            if "id" in toot:
                db.execute(
                    "INSERT INTO tweets VALUES ( ? , ? , ? , ? , ? )",
                    (feed.id, toot["id"], source, username, instance))
                sql.commit()
    _close_db(sql, db)


if __name__ == '__main__':
    args = _parseargs()
    operation = args.operation
    username = args.username
    instance = args.instance
    source = args.source
    days = args.days
    tags = args.tags
    if tags:
        tags = '\n{}'.format(' '.join(tags))
    else:
        tags = ''
    delay = args.delay
    api_base_url = 'https://{}'.format(instance)
    app_cred_file = 'data/{}.secret'.format(instance)
    login_cred_file = 'data/{}.secret'.format(username)

    if operation == 'init':
        _create_credentials(
            api_base_url, app_cred_file, username, login_cred_file)
    elif operation == 'toot':
        main(
            app_cred_file, login_cred_file, api_base_url, source, username,
            instance, days, tags, delay)
    else:
        print('not a valid operation declared..')
