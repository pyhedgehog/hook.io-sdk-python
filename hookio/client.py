import os
import sys
import time
import json
import random
import logging
import requests
from six.moves.urllib.parse import urljoin, urlencode

log = logging.getLogger(__name__)
DEFAULT_CHUNK_SIZE = 64


class Client:
    lazy_attrs = {
        'account': ('account', 'Account'),
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
                 verify=None, line_streaming=True, chunk_size=DEFAULT_CHUNK_SIZE,
                 max_retries=None):
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

        self.base_url = '%s://%s:%d/' % (protocol, host, port)
        self.session = requests.Session()
        self.max_retries = max_retries
        self.supports_retries = None
        if max_retries:
            try:
                a = requests.adapters.HTTPAdapter(max_retries=max_retries)
            except TypeError:
                self.supports_retries = False
                log.info("Installed version of requests doesn't supports retries.")
            else:
                self.session.mount(self.base_url, a)
                self.supports_retries = True
        self.hook_private_key = hook_private_key
        self.session.verify = verify
        self.line_streaming = line_streaming
        self.chunk_size = chunk_size

    def __getattr__(self, name):
        if name in self.lazy_attrs:
            mod, cls = self.lazy_attrs[name]
            factory = getattr(__import__(mod, globals(), locals(), [cls], 1), cls)
            obj = factory(self)
            setattr(self, name, obj)
            return obj
        raise AttributeError('%s instance has no attribute %r' % (self.__class__.__name__, name))

    def request(self, method, url, params, stream_in=None, streaming=None, anonymous=False,
                hook_private_key=None, chunk_size=None, json_auth=False, json_forbid=False):
        uri = urljoin(self.base_url, url)
        log.debug('Client.request: %r+%r = %r', self.base_url, url, uri)
        headers = {'accept': 'application/json'}
        if hook_private_key is None:
            hook_private_key = self.hook_private_key
        if hook_private_key and not anonymous:
            log.debug('Client.request: not anonymous')
            headers['hookio-private-key'] = hook_private_key
        else:
            log.debug('Client.request: anonymous')
        log.debug('Client.request: Passing %r', params)
        if json_auth and hook_private_key and not anonymous:
            params['hook_private_key'] = hook_private_key
        if stream_in is not None:
            log.debug('Client.request: Streaming %r', stream_in)
            data = stream_in
        elif method == 'POST':
            if json_forbid:
                headers['content-type'] = 'application/x-www-form-urlencoded'
                params = urlencode(params)
            else:
                headers['content-type'] = 'application/json'
                params = json.dumps(params)
            data, params = params, {}
        else:
            data = None
        max_retries = self.max_retries or 1
        if self.supports_retries:
            max_retries = 1
        for retry in range(max_retries):
            try:
                if streaming:
                    params['streaming'] = 'true'
                    log.debug('Client.request: Streaming: %s %s', method, url)
                    log.debug('Client.request: %r, %r', data, params)
                    r = self.session.request(method, uri, data=data,
                                             params=params, headers=headers, stream=True)
                else:
                    log.debug('Client.request: Reading: %s %s', method, url)
                    log.debug('Client.request: %r, %r', data, params)
                    r = self.session.request(method, uri, data=data,
                                             params=params, headers=headers, stream=False)
                break
            except Exception:
                if retry >= max_retries-1:
                    raise
                sleep = random.randint(5, 60)
                log.exception("Request attempt %d/%d failed - sleeping %s seconds...",
                              retry+1, max_retries, sleep)
                time.sleep(sleep)
        r.raise_for_status()
        if callable(streaming):
            if chunk_size is None:
                chunk_size = self.chunk_size
            if self.line_streaming:
                log.debug("Streaming iter_lines to %r (%s)", streaming, r.encoding)
                for line in r.iter_lines(chunk_size=chunk_size):
                    if not isinstance(line, str):
                        line = line.decode(r.encoding or 'utf-8', errors='replace')
                    line += '\n'
                    # log.debug("%r(%r)", streaming, line)
                    streaming(line)
            else:
                log.debug("Streaming iter_content to %r", streaming)
                for chunk in r.iter_content(chunk_size=chunk_size):
                    # log.debug("%r(%r)", streaming, chunk)
                    streaming(chunk)
        elif streaming:
            log.debug("Streaming is %r - stream using resp.iter_* manually", streaming)
        return r


def createClient(opts=None, env=None, Hook=None):  # js-like interface
    if opts is None:
        opts = {}
    if env is None:
        env = os.environ
    hook_private_key = opts.get('hook_private_key', None)

    if Hook is None:
        check_hook = ('__main__' in sys.modules and
                      hasattr(sys.modules['__main__'], 'Hook') and
                      'env' in sys.modules['__main__'].Hook and
                      'req' in sys.modules['__main__'].Hook)
        if check_hook:
            Hook = sys.modules['__main__'].Hook
    if Hook:
        opts['host'] = Hook['req']['host']
        opts['verify'] = False
        if hook_private_key is None and 'hookio-private-key' in Hook['req']['headers']:
            hook_private_key = opts['hook_private_key'] = \
                Hook['req']['headers']['hookio-private-key']
        if hook_private_key is None and 'hook_private_key' in Hook['params']:
            hook_private_key = opts['hook_private_key'] = Hook['params']['hook_private_key']
        if hook_private_key is None and 'hookAccessKey' in Hook['env']:
            hook_private_key = opts['hook_private_key'] = Hook['env']['hookAccessKey']
        if hook_private_key is None and 'hookAccessKey' in Hook:
            hook_private_key = opts['hook_private_key'] = Hook['hookAccessKey']

    if hook_private_key is None and 'hook_private_key' in env:
        hook_private_key = opts['hook_private_key'] = env['hook_private_key']
    if hook_private_key is None and 'hookAccessKey' in env:
        hook_private_key = opts['hook_private_key'] = env['hookAccessKey']

    return Client(**opts)
