import weakref
import json
from six import StringIO
from .utils import opt_json


class Events:
    def __init__(self, client):
        self.client = weakref.proxy(client)

    def get(self, account, raw=False, **opts):
        r = self.client.request('GET', account + '/events', {}, **opts)
        return opt_json(r, raw)

    def stream(self, account, streaming=True, raw=True, **opts):
        opts['streaming'] = streaming
        if not raw and callable(streaming):
            def wrapper(s):
                return streaming(json.loads(s))
            opts['streaming'] = wrapper
        return self.client.request('GET', account + '/events', StringIO(''), **opts)
