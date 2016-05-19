import weakref
from .utils import opt_json


class Datastore:
    def __init__(self, client):
        self.client = weakref.proxy(client)

    def get(self, key, raw=False, **opts):
        r = self.client.request('GET', 'datastore/get?key=%s' % (key,), {}, **opts)
        return opt_json(r, raw)

    def set(self, key, value, raw=False, **opts):
        r = self.client.request('POST', 'datastore/set', {'key': key, 'value': value}, **opts)
        return opt_json(r, raw)

    def delete(self, key, raw=False, **opts):
        r = self.client.request('POST', 'datastore/del', {'key': key}, **opts)
        return opt_json(r, raw)

    def recent(self, raw=False, **opts):
        r = self.client.request('GET', 'datastore/recent', {}, **opts)
        return opt_json(r, raw)
