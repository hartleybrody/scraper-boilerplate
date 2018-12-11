import os
import csv
import logging

import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException


logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')
PROXIES_REQUIRED = os.environ["PROXIES_REQUIRED"].lower() == "true"
PROXIES = []


class ScrapingException(Exception):
    pass  # base exception we can catch ourselves


def make_request(url, headers=None, proxy_check=None, return_type="page"):

    proxy = get_proxy()
    if not proxy:
        no_proxies("No proxies available for this request")

    try:
        r = requests.get(url, headers=headers, proxies=proxy)
    except RequestException as e:
        logging.warning("Request for {} failed, trying again.".format(url))
        return make_request(url, headers=headers, proxy_check=proxy_check, return_type=return_type)  # try request again, recursively

    # proxy_check is a function argument that takes the `requests`
    # response object and returns a boolean indicating whether it
    # appears that the site has blocked this request
    if proxy_check is not None:
        is_detected = proxy_check(r)
        if is_detected:
            # remove the proxy we used for this request from the
            # PROXIES list so we don't try to reuse it (for now)
            PROXIES.remove(proxy["dict"])
            logging.warning("Request using {} failed: {}".format(proxy["dict"]["IP"], url))
            return make_request(url, headers=headers, proxy_check=proxy_check, return_type=return_type)  # try request again, recursively

    if return_type == "page":
        return BeautifulSoup(r.text, "html.parser")
    if return_type == "text":
        return r.text
    if return_type == "response":
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
        "dict": proxy
    }


def no_proxies(msg):
    if PROXIES_REQUIRED:
        ScrapingException(msg)
    else:
        logging.warning(msg)

try:
    with open("proxies.csv", "r") as f:
        reader = csv.DictReader(f)
        for line in reader:
            PROXIES.append(line)
except:
    no_proxies("No proxies available for this scrape")