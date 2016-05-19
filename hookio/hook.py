import weakref
from six.moves.urllib.parse import parse_qs
from .utils import opt_json


class Hook:
    def __init__(self, client):
        self.client = weakref.proxy(client)

    def run(self, url, data, raw=False, streaming=False, anonymous=True, **opts):
        if not streaming and not isinstance(data, dict):
            data = parse_qs(data)
            for k, v in data.items():
                if type(v) == list and len(v) == 1:
                    data[k] = v[0]
        r = self.client.request('GET', url, data, streaming=streaming,
                                anonymous=anonymous, **opts)
        return opt_json(r, raw or streaming)

    def create(self, name, data, raw=False, **opts):
        data = data.copy()
        data['name'] = name
        r = self.client.request('POST', 'new', data, **opts)
        return opt_json(r, raw)

    def update(self, url, data, raw=False, **opts):
        r = self.client.request('POST', url + '/admin', data, **opts)
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
