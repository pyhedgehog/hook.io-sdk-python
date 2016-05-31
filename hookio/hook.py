import weakref
from six.moves.urllib.parse import parse_qs
from .utils import opt_json


class Hook:
    def __init__(self, client):
        self.client = weakref.proxy(client)

    def run(self, url, data, raw=False, streaming=False, anonymous=True, method='GET', **opts):
        if not streaming and not isinstance(data, dict):
            data = parse_qs(data)
            for k, v in data.items():
                if type(v) == list and len(v) == 1:
                    data[k] = v[0]
        r = self.client.request(method, url, data, streaming=streaming,
                                anonymous=anonymous, **opts)
        return opt_json(r, raw or streaming)

    def create(self, name, data, raw=False, **opts):
        data = data.copy()
        data['name'] = name
        r = self.client.request('POST', 'new', data, **opts)
        return opt_json(r, raw)

    def update(self, url, data, raw=False, **opts):
        owner, name = url.split('/')
        data = data.copy()
        data['owner'] = owner
        data['name'] = name
        data['save'] = 'save'
        # data['previousName'] = name
        # r = self.client.request('POST', '/admin?owner=' + owner + '&name=' + name, data, **opts)
        r = self.client.request('POST', '/admin', data, json_forbid=True, **opts)
        # r = self.client.request('POST', url + '/admin', data, json_forbid=True, **opts)
        return opt_json(r, raw)

    def destroy(self, url, raw=False, **opts):
        r = self.client.request('POST', url + '/delete', {}, **opts)
        return opt_json(r, raw)

    def source(self, url, raw=False, **opts):
        r = self.client.request('GET', url + '/source', {}, **opts)
        if raw:
            return r
        return r.text

    def resource(self, url, raw=False, **opts):
        r = self.client.request('GET', url + '/resource', {}, **opts)
        return opt_json(r, raw)
