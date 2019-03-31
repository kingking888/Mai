import hashlib

from w3lib.url import canonicalize_url

class Request:
    def __init__(self, url, headers={}, cookies={}, body="", dont_filter=False, callback=None):
        self.url = url
        self.method = 'GET'
        self.headers = headers
        self.body = body
        self.dont_filter = dont_filter
        self.callback = callback

    def __str__(self):
        return f'Request[{self.url}]'

    @property
    def fingerprint(self):
        url = bytes(canonicalize_url(self.url), 'utf-8')
        method = bytes(self.method, 'utf-8')
        body = bytes(self.body, 'utf-8')
        salt = b'salt'
        m = hashlib.sha1()
        m.update(url + method + body + salt)
        return m.hexdigest()

    def __eq__(self, other):
        if self.fingerprint == other.fingerprint:
            return True
        return False