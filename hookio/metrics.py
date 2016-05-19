import weakref
from .utils import opt_json


class Metrics:
    def __init__(self, client):
        self.client = weakref.proxy(client)

    def hits(self, url, raw=False, **opts):
        r = self.client.request('GET', 'metrics/' + url + '/hits', {}, **opts)
        return opt_json(r, raw)
