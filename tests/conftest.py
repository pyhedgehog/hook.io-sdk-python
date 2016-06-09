#!/usr/bin/env python
# import warnings
import logging
import hookio
import json
import py
import pprint

log = logging.getLogger(__name__)


def setup_function(function):
    if not logging.root.handlers:
        format = '%(asctime)s:%(threadName)s:' + logging.BASIC_FORMAT
        logging.basicConfig(format=format, level=logging.DEBUG)
    log.debug('setting up %s', function)


def pytest_funcarg__cache(request):
    log.debug('pytest_funcarg__cache: %s', pprint.pformat(request))
    if not hasattr(request.config, 'cache'):
        def cache_get(key):
            path = cachedir.join(*key.split('/'))
            if path.check():
                try:
                    f = path.open('r')
                    try:
                        return json.load(f)
                    finally:
                        f.close()
                except ValueError:
                    trace("cache-invalid at %s" % (path,))

        def cache_set(key, value):
            path = cachedir.join(*key.split('/'))
            try:
                path.dirpath().ensure_dir()
            except (py.error.EEXIST, py.error.EACCES):
                request.config.warn(code='I9', message='could not create cache path %s' % (path,))
                return
            try:
                f = path.open('w')
            except py.error.ENOTDIR:
                request.config.warn(code='I9', message='cache could not write path %s' % (path,))
                return
            try:
                trace("cache-write %s: %r" % (key, value,))
                json.dump(value, f, indent=2, sort_keys=True)
            finally:
                f.close()
        trace = request.config.trace.root.get("cache")
        cachedir = request.config.rootdir.join(".cache", "v")
        cache = request.config.cache = hookio.utils.Namespace()
        cache.get = cache_get
        cache.set = cache_set
    return request.config.cache
