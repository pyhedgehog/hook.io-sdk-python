import weakref
from .utils import opt_json


class Env:
    def __init__(self, client):
        self.client = weakref.proxy(client)

    def get(self, raw=False, **opts):
        r = self.client.request('GET', 'env', {}, **opts)
        return opt_json(r, raw, allowempty=True)

    def set(self, data, raw=False, **opts):
        keys, values = zip(*data.items())
        values = [v if v else None for v in values]
        r = self.client.request('POST', 'env', dict(key=keys, value=values), **opts)
        return opt_json(r, raw)
