import weakref
import re
import cgi
from .utils import opt_json

re_hook = re.compile('<a title="Run Hook" href="/([^/"]+/[^/"]+)">')
re_field = '<input [^>]*name="%s" value="([^"]*)"[^>]*>|' + \
           '<input\s+[^>]*value="([^"]*)"\s+name="%s"[^>]*>'
account_fields = 'name email paidStatus previousName'.split()


class Account:
    def __init__(self, client):
        self.client = weakref.proxy(client)

    def login(self, name, password, raw=False, **opts):
        data = {'name': name, 'password': password}
        r = self.client.request('POST', 'login', data, **opts)
        return opt_json(r, raw)

    def info(self, raw=False, **opts):
        r = self.client.request('GET', 'account', {}, **opts)
        if raw:
            return r
        t = r.headers.get("content-type", "").split(";", 1)[0]
        if t == 'application/json':
            res = r.json()
            if res.get('status') == 'invalid':
                k = self.client.keys.info()
                res = {'name': k['owner']}
            return res
        res = {}
        for field in account_fields:
            m = re.search(re_field % (field, field), r.text)
            if not m:
                continue
            res[field] = m.group(1) or m.group(2)
        return res

    def services(self, user=None, raw=False, **opts):
        if user:
            r = self.client.request('GET', user, {}, **opts)
        else:
            r = self.client.request('GET', 'services/', {}, **opts)
        if raw:
            return r
        if cgi.parse_header(r.headers.get('content-type',''))[0] == 'application/json':
            return r.json()
        return [dict(name=n) for n in re_hook.findall(r.text)]
