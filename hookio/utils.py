import sys
import json
import hookio
import logging
import threading

log = logging.getLogger(__name__)


def opt_json(r, raw, allowempty=False):
    if raw:
        return r
    if allowempty and not r.content:
        return None
    try:
        res = r.json()
    except Exception:
        log.exception("Failed to parse JSON from %r", r.content)
        raise
    return res


class Response2JSONLinesIterator(object):
    def __init__(self, response, converter=None, chunk_size=1, encoding=None):
        self.response = response
        self.converter = converter
        self.chunk_size = chunk_size
        self.encoding = encoding or response.encoding or 'utf-8'
        self.started = threading.Lock()

    def __iter__(self):
        if not self.started.acquire(0):  # it should be never released
            log.debug("Failed to start Response2JSONLinesIterator for %r", self.response)
            raise ValueError("Iterator already executing")
        log.debug("Starting Response2JSONLinesIterator for %r", self.response)
        try:
            for line in self.response.iter_lines(chunk_size=self.chunk_size):
                if not isinstance(line, str):
                    line = line.decode(self.encoding, errors='replace')
                obj = json.loads(line)
                if self.converter is not None:
                    obj = self.converter(obj)
                yield obj
        except Exception:
            log.debug("Exception in Response2JSONLinesIterator for %r:", self.response, exc_info=1)
            raise


class Namespace(dict):
    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, value):
        self[name] = value
        return value


def install_hook_sdk(Hook):
    HookNS = Namespace(Hook)
    if '__main__' in sys.modules and getattr(sys.modules['__main__'], 'Hook', None) is Hook:
        sys.modules['__main__'].Hook = HookNS
    HookNS.sdk = hookio.createClient(Hook=HookNS)
    return HookNS
