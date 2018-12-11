import os
import json
from urlparse import urlparse

import redis

from utils import logging

u = urlparse(os.environ["REDIS_URL"])
redis = redis.StrictRedis(host=u.hostname, port=u.port, password=u.password, db=0)

# note that the default implementation is to use the
# redis 'set' as the datatype, so that duplicate work
# isn't added to the queue: https://redis.io/topics/data-types#sets


def enqueue_item(queue_name, item):
    if type(item) != str:
        item = json.dumps(item)
    logging.debug("Enqueuing item in {}:\t{}".format(queue_name, item))
    return redis.sadd(queue_name, item)

def dequeue_item(queue_name):
    item = redis.spop(queue_name)
    if item:
        item = item.decode('utf-8')
        if item.startswith("{") and item.endswith("}"):
            item = json.loads(item)
    logging.debug("Dequeuing item from {}:\t{}".format(queue_name, item))
    return item

def queue_size(queue_name):
    return redis.scard(queue_name)

def empty_queue(queue_name):
    return redis.delete(queue_name)