import sys
import weakref
import json
import logging
from .utils import opt_json, Response2JSONLinesIterator
from six import StringIO

log = logging.getLogger(__name__)


class Logs:
    def __init__(self, client):
        self.client = weakref.proxy(client)

    def read(self, url, raw=False, raw_data=True, **opts):
        r = self.client.request('GET', url + '/logs', {}, **opts)
        res = opt_json(r, raw)
        if not raw and not raw_data and type(res) == list:
            res = [json.loads(line) for line in res]
            for row in res:
                if 'data' in row:
                    row['data'] = json.loads(row['data'])
        return res

    def stream(self, url, raw=True, raw_data=True, streaming=True, **opts):
        opts['streaming'] = streaming
        if streaming:
            opts.setdefault('stream_in', StringIO())
        if not raw and callable(streaming):
            def wrapper(line):
                row = json.loads(line)
                if not raw_data and 'data' in row:
                    row['data'] = json.loads(row['data'])
                return streaming(row)
            assert self.client.line_streaming, "Inconsistent API call"
            opts['streaming'] = wrapper
            log.debug("Will stream via wrapper")
        r = self.client.request('GET', url + '/logs', {}, **opts)
        if not raw and streaming and not callable(streaming):
            log.debug("Will return iter_objects generator")
            chunk_size = opts.get('chunk_size', self.client.chunk_size)
            if raw_data:
                func = None
            else:
                func = data_converted
            return Response2JSONLinesIterator(r, converter=func, chunk_size=chunk_size)
        return r

    def flush(self, url, raw=False, **opts):
        r = self.client.request('GET', url + '/logs?flush=true', {}, **opts)
        return opt_json(r, raw)

    def write(self, msg):
        assert hasattr(sys.modules['__main__'], 'Hook'), \
            "Writing logs supported only inside hook processing"
        msg = {'type': 'log', 'payload': {'entry': msg}}
        sys.stderr.write(json.dumps(msg) + '\n')


def data_converted(obj):
    if 'data' in obj:
        obj['data'] = json.loads(obj['data'])
    return obj
