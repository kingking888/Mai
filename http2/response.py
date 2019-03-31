from urllib.parse import urljoin

from .selector import Selector
from .request import Request

class Response:
    def __init__(url, request, status, text):
        self.url = url
        self.request = request
        self.status = status
        self.text = text
        self.selector = Selector(text)

    def extract(self, xpath):
        return self.selector.extract(xpath)
    
    def extract_first(self, xpath):
        return self.selector.extract_first(xpath)

    def urljoin(self, url)
        return urljoin(self.url, url)

    def follow(headers={}, *args, **kwargs):
        headers['Referer'] = self.url
        return Request(headers=headers, *args, **kwargs)