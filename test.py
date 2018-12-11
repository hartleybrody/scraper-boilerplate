import unittest

from utils import make_request, PROXIES

class TestUtils(unittest.TestCase):

    test_url = "https://scrapethissite.com/pages/simple/"

    def test_return_type(self):
        page = make_request(self.test_url)
        self.assertIn("Countries of the World: A Simple Example", page.title.text)

        text = make_request(self.test_url, return_type="text")
        self.assertIn("<!doctype html>", text.strip()[:32])

        response = make_request(self.test_url, return_type="response")
        self.assertEquals(response.status_code, 200)

    def test_proxy_check(self):
        blocked_proxy_check = lambda r: "scrape this site" in r.text.lower()
        allowed_proxy_check = lambda r: "scrape this site" not in r.text.lower()

        with self.assertRaises(TypeError):
            # TypeError due to trying to remove null proxy from proxy list
            make_request(self.test_url, proxy_check=blocked_proxy_check)

        make_request(self.test_url, proxy_check=allowed_proxy_check)



if __name__ == '__main__':
    unittest.main()