import sys
import hookio
import logging

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
