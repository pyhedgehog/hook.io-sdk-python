import weakref
from .utils import opt_json


class Domains:
    def __init__(self, client):
        self.client = weakref.proxy(client)

    def all(self, raw=False, **opts):
        r = self.client.request('GET', 'domains', {}, **opts)
        return opt_json(r, raw)
