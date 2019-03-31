from urllib.parse import urljoin

from .selector import Selector
from .request import Request

class Response:
    def __init__(self, request, text, status=200):
        self.request = request
        self.status = status
        self.text = text
        self.selector = Selector(text)

    def extract(self, xpath):
        return self.selector.extract(xpath)
    
    def extract_first(self, xpath):
        return self.selector.extract_first(xpath)

    def urljoin(self, url):
        return urljoin(self.request.url, url)

    def follow(self, url, headers={}, *args, **kwargs):
        # headers['Referer'] = self.request.url
        url = self.urljoin(url)
        return Request(url, headers=headers, *args, **kwargs)