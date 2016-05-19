import sys
import hookio


def opt_json(r, raw, allowempty=False):
    if raw:
        return r
    if allowempty and not r.content:
        return None
    return r.json()


class Namespace(dict):
    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, value):
        self[name] = value
        return value


def init_sdk(Hook):
    Hook = Namespace(Hook)
    if '__main__' in sys.modules and getattr(sys.modules['__main__'], 'Hook') is Hook:
        sys.modules['__main__'].Hook = Hook
    Hook.sdk = hookio.createClient()
    return Hook
