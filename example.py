import re
import time
import random
from datetime import datetime

from queue import enqueue_item, dequeue_item
from utils import make_request, logging
from models import db_session, NoResultFound, Item, Keyword

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36",
    "Accept-Language": "en-us",
    "Accept-Encoding": "gzip, deflate",
}

KEYWORD_QUEUE = "keywords"


def search(keyword):

    logging.info(u"Searching for keyword: {}".format(keyword))

    try:
        kw = db_session.query(Keyword).filter_by(keyword=keyword).one()
    except NoResultFound:
        kw = Keyword(keyword=keyword).save()

    page = make_request("https://scrapethissite.com/pages/forms/?q={}".format(keyword), headers=HEADERS)

    for row in page.find_all("tr", "team"):
        i = Item()
        i.year = row.find("td", "name").text.strip()
        i.wins = row.find("td", "wins").text.strip()
        i.losses = row.find("td", "losses").text.strip()
        i.save()

        print i.to_dict()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-k", "--keyword", help="Manually specify a one-off keyword to search for.", type=str)
    parser.add_argument("-f", "--file", help="File path to a newline-deliniated list of keywords. ex: 'input/keywords.csv'", type=str)
    parser.add_argument("-w", "--worker", help="Create a worker that takes keywords off the queue", action='store_true')
    args = parser.parse_args()

    if args.keyword:
        search(args.keyword)

    elif args.file:
        with open(args.file, "r") as f:
            for line in f:
                enqueue_item(KEYWORD_QUEUE, line.strip())

    elif args.worker:
        while True:
            keyword = dequeue_item(KEYWORD_QUEUE)

            if not keyword:
                logging.info("Nothing left in queue")
                time.sleep(60)
                continue

            try:
                search(keyword)
            except Exception as e:
                logging.info("Encountered exception, placing keyword back into the queue: {}".format(keyword))
                enqueue_item(KEYWORD_QUEUE, keyword)
                raise e


