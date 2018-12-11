import csv
import logging

import requests
from requests.exceptions import RequestException


logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

PROXIES = []
try:
    with open("proxies.csv", "r") as f:
        reader = csv.DictReader(f)
        for line in reader:
            PROXIES.append(line)
except:
    logging.warning("Found no proxies to use for this scrape")


class ScrapingException(Exception):
    pass  # base exception we can catch ourselves


def make_request(url, headers=None, proxy_detection_check=None):

    proxy = get_proxy()
    if not proxy:
        raise ScrapingException("No proxies available to make request")

    try:
        r = requests.get(url, headers=headers, proxies=proxy)
    except RequestException as e:
        logging.error("Request for {} failed, trying again.".format(url))
        return make_request(url, headers=headers, proxy_detection_check=proxy_detection_check)  # try request again, recursively

    # proxy_detection_check is a function argument (above) that takes
    # the response object and returns a boolean indicating whether
    # it appears that the site has blocked this request
    if proxy_detection_check is not None:
        is_detected = proxy_detection_check(r)
        if is_detected:
            # remove the proxy we used for this request from the
            # PROXIES list so we don't try to reuse it (for now)
            PROXIES.remove(proxy["info"])
            logging.warning("Request using {} failed: {}".format(proxy["info"]["IP"], url))
            return make_request(url, headers=headers, proxy_detection_check=proxy_detection_check)

    return r


def get_proxy():
    # choose a proxy server to use for this request

    if not PROXIES or len(PROXIES) == 0:
        return None  # no proxies in list

    proxy = PROXIES.pop()  # get the last proxy in the list
    PROXIES.insert(0, proxy)  # put this proxy back at the beginning of the list

    proxy_url = "http://{user}:{pwd}@{ip}:{port}/".format(
        user=proxy["Login"],
        pwd=proxy["Password"],
        ip=proxy["IP"],
        port=proxy["HTTP port"],
    )

    # format for request library
    return {
        "http": proxy_url,
        "https": proxy_url,
        "info": proxy
    }