import weakref
from .utils import opt_json


class Files:
    def __init__(self, client):
        self.client = weakref.proxy(client)

    def readFile(self, path, raw=False, **opts):
        r = self.client.request('POST', 'files/readFile', {'path': path}, **opts)
        return opt_json(r, raw)

    def writeFile(self, path, contents, raw=False, **opts):
        data = {'path': path, 'contents': contents}
        r = self.client.request('POST', 'files/writeFile', data, **opts)
        return opt_json(r, raw)

    def removeFile(self, path, raw=False, **opts):
        r = self.client.request('POST', 'files/removeFile', {'path': path}, **opts)
        return opt_json(r, raw)

    def readdir(self, path, raw=False, **opts):
        r = self.client.request('POST', 'files/readdir', {'path': path}, **opts)
        return opt_json(r, raw)

    def stat(self, path, raw=False, **opts):
        r = self.client.request('POST', 'files/stat', {'path': path}, **opts)
        return opt_json(r, raw)
