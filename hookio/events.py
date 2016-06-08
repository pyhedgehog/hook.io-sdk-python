import weakref
import json
import logging
from six import StringIO
from .utils import opt_json, Response2JSONLinesIterator

log = logging.getLogger(__name__)


class Events:
    def __init__(self, client):
        self.client = weakref.proxy(client)

    def get(self, account, raw=False, **opts):
        r = self.client.request('GET', account + '/events', {}, **opts)
        return opt_json(r, raw)

    def stream(self, account, streaming=True, raw=True, **opts):
        opts['streaming'] = streaming
        if streaming:
            opts.setdefault('stream_in', StringIO())
        if not raw and callable(streaming):
            def wrapper(line):
                return streaming(json.loads(line))
            assert self.client.line_streaming, "Inconsistent API call"
            opts['streaming'] = wrapper
        r = self.client.request('GET', account + '/events', {}, **opts)
        if not raw and streaming and not callable(streaming):
            log.debug("Will return iter_objects generator")
            chunk_size = opts.get('chunk_size', self.client.chunk_size)
            return Response2JSONLinesIterator(r, chunk_size=chunk_size)
        return r
