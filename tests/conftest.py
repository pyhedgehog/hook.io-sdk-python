#!/usr/bin/env python
# import warnings
import os
import json
import pprint
import logging
import hookio
import py

log = logging.getLogger(__name__)


def setup_function(function):
    if not logging.root.handlers:
        format = '%(asctime)s:%(threadName)s:' + logging.BASIC_FORMAT
        logging.basicConfig(format=format, level=logging.DEBUG)
    log.debug('setting up %s', function)


def pytest_funcarg__cache(request):
    log.debug('pytest_funcarg__cache: %s', pprint.pformat(request))
    if not hasattr(request.config, 'cache'):
        def ensure_dir(path):
            dp = os.path.dirname(path)
            if not os.path.isdir(dp):
                os.makedirs(dp)

        def cache_get(key):
            path = os.path.join(cachedir, *key.split('/'))
            if path.check():
                try:
                    f = open(path, 'r')
                    try:
                        return json.load(f)
                    finally:
                        f.close()
                except ValueError:
                    trace("cache-invalid at %s" % (path,))

        def cache_set(key, value):
            path = os.path.join(cachedir, *key.split('/'))
            try:
                ensure_dir(path)
            except (py.error.EEXIST, py.error.EACCES):
                request.config.warn(code='I9', message='could not create cache path %s' % (path,))
                return
            try:
                f = open(path, 'w')
            except py.error.ENOTDIR:
                request.config.warn(code='I9', message='cache could not write path %s' % (path,))
                return
            try:
                trace("cache-write %s: %r" % (key, value,))
                json.dump(value, f, indent=2, sort_keys=True)
            finally:
                f.close()
        trace = request.config.trace.root.get("cache")
        cachedir = os.path.join(str(request.config.inicfg.config.path), os.pardir, ".cache", "v")
        trace("pytest_funcarg__cache: cachedir=%r", cachedir)
        request.config.warn(code='I9', message='pytest_funcarg__cache: cachedir=%s' % (cachedir,))
        cache = request.config.cache = hookio.utils.Namespace()
        cache.get = cache_get
        cache.set = cache_set
    return request.config.cache
