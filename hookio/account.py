import weakref
import re
from .utils import opt_json

re_hook = re.compile('<a title="Run Hook" href="/([^/"]+/[^/"]+)">')


class Account:
    def __init__(self, client):
        self.client = weakref.proxy(client)

    def login(self, name, password, raw=False, **opts):
        data = {'name': name, 'password': password}
        r = self.client.request('POST', 'login', data, **opts)
        return opt_json(r, raw)

    def services(self, user=None, raw=False, **opts):
        if user:
            r = self.client.request('GET', user, {}, **opts)
        else:
            r = self.client.request('GET', 'services', {}, **opts)
        if raw:
            return r
        return re_hook.findall(r.text)
