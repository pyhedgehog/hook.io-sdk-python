import os
import sys
import json
import requests
import logging
from six.moves.urllib.parse import urljoin

log = logging.getLogger(__name__)


class Client:
    lazy_attrs = {
        'datastore': ('datastore', 'Datastore'),
        'domains': ('domains', 'Domains'),
        'env': ('env', 'Env'),
        'events': ('events', 'Events'),
        'files': ('files', 'Files'),
        'hook': ('hook', 'Hook'),
        'keys': ('keys', 'Keys'),
        'logs': ('logs', 'Logs'),
        'metrics': ('metrics', 'Metrics'),
    }

    def __init__(self, host='hook.io', port=None, protocol=None, hook_private_key=None,
                 verify=None, line_streaming=True, decode_unicode=True,
                 chunk_size=requests.models.ITER_CHUNK_SIZE):
        # assert hook_private_key is not None
        if host is None:
            host = '127.0.0.1'
        if protocol is None and port == 443:
            protocol = 'https'
        local = host.lower() in ('0.0.0.0', '127.0.0.1', 'localhost')
        if protocol is None and local:
            protocol = 'http'
        if protocol is None and port is None:
            protocol = 'https'
        if protocol is None:
            protocol = 'http'
        if port is None and protocol == 'https':
            port = 443
        if port is None and local:
            port = 9999
        if port is None:
            port = 80
        if verify is None:
            verify = not local
        # assert protocol == 'https'

        self.session = requests.Session()
        self.hook_private_key = hook_private_key
        self.session.verify = verify
        self.base_url = '%s://%s:%d/' % (protocol, host, port)
        self.line_streaming = line_streaming
        self.decode_unicode = decode_unicode
        self.chunk_size = chunk_size

    def __getattr__(self, name):
        if name in self.lazy_attrs:
            mod, cls = self.lazy_attrs[name]
            factory = getattr(__import__(mod, globals(), locals(), [cls], 1), cls)
            obj = factory(self)
            setattr(self, name, obj)
            return obj
        raise AttributeError('%s instance has no attribute %r' % (self.__class__.__name__, name))

    def request(self, method, url, params, streaming=None, anonymous=False, hook_private_key=None,
                json_auth=False):
        uri = urljoin(self.base_url, url)
        log.debug('%s.request: %r+%r = %r', self.__class__, self.base_url, url, uri)
        headers = {'accept': 'application/json'}
        if hook_private_key is None:
            hook_private_key = self.hook_private_key
        if hook_private_key and not anonymous:
            log.debug('%s.request: not anonymous', self.__class__)
            headers['hookio-private-key'] = hook_private_key
        else:
            log.debug('%s.request: anonymous', self.__class__)
        if streaming:
            log.debug('%s.request: Streaming %r', self.__class__, params)
            r = self.session.request(method, uri, data=params,
                                     params={'streaming': 'true'}, headers=headers, stream=True)
        else:
            if json_auth:
                params['hook_private_key'] = hook_private_key
            log.debug('%s.request: Passing %r', self.__class__, params)
            # r = self.session.request(method, uri, json=params, headers=headers, stream=False)
            # Compatibility with old requests package installed on hook.io
            if method == 'POST':
                headers['content-type'] = 'application/json'
                params = json.dumps(params)
            r = self.session.request(method, uri, data=params, headers=headers, stream=False)
        r.raise_for_status()
        # streaming
        if callable(streaming):
            if self.line_streaming:
                iterator = (s + '\n' for s in r.iter_lines(chunk_size=self.chunk_size,
                                                           decode_unicode=self.decode_unicode))
            else:
                iterator = r.iter_content(chunk_size=self.chunk_size,
                                          decode_unicode=self.decode_unicode)
            map(streaming, iterator)
        return r


def createClient(opts=None):  # js-like interface
    if opts is None:
        opts = {}
    hook_private_key = opts.get('hook_private_key', None)

    Hook = ('__main__' in sys.modules and hasattr(sys.modules['__main__'], 'Hook') and
            'env' in sys.modules['__main__'].Hook and 'req' in sys.modules['__main__'].Hook)
    if Hook:
        Hook = sys.modules['__main__'].Hook
        opts['host'] = Hook['req']['host']
        opts['verify'] = False
        if hook_private_key is None and 'hook-private-key' in Hook['req']['headers']:
            hook_private_key = opts['hook_private_key'] = Hook['req']['headers']['hook-private-key']
        if hook_private_key is None and 'hook_private_key' in Hook['params']:
            hook_private_key = opts['hook_private_key'] = Hook['params']['hook_private_key']
        if hook_private_key is None and 'hookAccessKey' in Hook['env']:
            hook_private_key = opts['hook_private_key'] = Hook['env']['hookAccessKey']
        if hook_private_key is None and 'hookAccessKey' in Hook:
            hook_private_key = opts['hook_private_key'] = Hook['hookAccessKey']

    if hook_private_key is None and 'hook_private_key' in os.environ:
        hook_private_key = opts['hook_private_key'] = os.environ['hook_private_key']
    if hook_private_key is None and 'hookAccessKey' in os.environ:
        hook_private_key = opts['hook_private_key'] = os.environ['hookAccessKey']

    return Client(**opts)
