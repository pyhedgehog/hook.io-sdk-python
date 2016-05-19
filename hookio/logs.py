import sys
import weakref
import json
from six import StringIO
from .utils import opt_json


class Logs:
    def __init__(self, client):
        self.client = weakref.proxy(client)

    def read(self, url, raw=False, **opts):
        r = self.client.request('GET', url + '/logs', {}, **opts)
        return opt_json(r, raw)

    def stream(self, url, raw=True, streaming=True, **opts):
        opts['streaming'] = streaming
        if not raw and callable(streaming):
            def wrapper(s):
                return streaming(json.loads(s))
            opts['streaming'] = wrapper
        return self.client.request('GET', url + '/logs', StringIO(''), **opts)

    def flush(self, url, raw=False, **opts):
        r = self.client.request('GET', url + '/logs?flush=true', {}, **opts)
        return opt_json(r, raw)

    def write(self, msg):
        assert hasattr(sys.modules['__main__'], 'Hook'), \
            "Writing logs supported only inside hook processing"
        msg = {'type': 'log', 'payload': {'entry': msg}}
        sys.stderr.write(json.dumps(msg) + '\n')
