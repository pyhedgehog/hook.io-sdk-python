import weakref
import json
import logging
from six import StringIO
from .utils import opt_json

log = logging.getLogger(__name__)


class Events:
    def __init__(self, client):
        self.client = weakref.proxy(client)

    def get(self, account, raw=False, **opts):
        r = self.client.request('GET', account + '/events', {}, **opts)
        return opt_json(r, raw)

    def stream(self, account, streaming=True, raw=True, **opts):
        opts['streaming'] = streaming
        if not raw and callable(streaming):
            def wrapper(line):
                return streaming(json.loads(line))
            assert self.client.line_streaming, "Inconsistent API call"
            opts['streaming'] = wrapper
        r = self.client.request('GET', account + '/events', StringIO(''), **opts)
        if not raw and streaming and not callable(streaming):
            def iter_objects():
                for line in r.iter_lines(chunk_size=opts.get('chunk_size', self.client.chunk_size)):
                    yield json.loads(line)
            log.debug("Will return iter_objects generator")
            return iter_objects()
        return r
