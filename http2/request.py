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