import hashlib

from w3lib.url import canonicalize_url

def request_fingerprint(request):
    url = bytes(canonicalize_url(request.url), 'utf-8')
    method = bytes(request.method, 'utf-8')
    body = bytes(request.body, 'utf-8')
    salt = b'salt'
    m = hashlib.sha1()
    m.update(url + method + body + salt)
    return m.hexdigest()

