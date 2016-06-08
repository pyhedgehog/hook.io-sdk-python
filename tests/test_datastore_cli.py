#!/usr/bin/env python
import os
import json
import logging
import random
import hookio.runclient

log = logging.getLogger(__name__)
unclutter_prefix = '7e4fe9ee-4624-47f9-8e81-0d8d3a348f13'
unclutter_prefix = '%s::%08X' % (unclutter_prefix, random.randrange(0x10000000, 0x7FFFFFFF))


def setup_function(function):
    if not logging.root.handlers:
        logging.basicConfig(level=logging.DEBUG)
    log.debug('setting up %s', function)


def test_datastore_cli_parse():
    key = unclutter_prefix + '::test_key'
    val = dict(a='1', b='2', uuid=unclutter_prefix)
    params = ['%s=%s' % item for item in val.items()]
    args = hookio.runclient.parse_argv(['-', 'datastore', 'set', key] + params)
    assert args.obj == 'datastore'
    assert args.func == 'set'
    assert args.url == key
    assert args.data == val

    args = hookio.runclient.parse_argv(['-', 'datastore', 'get', key])
    assert args.obj == 'datastore'
    assert args.func == 'get'
    assert args.url == key
    assert args.data is None
    assert args.params == []


def test_datastore_cli(capsys):
    assert 'hook_private_key' in os.environ
    key = unclutter_prefix + '::test_key'
    val = dict(a='1', b='2', uuid=unclutter_prefix)
    params = ['%s=%s' % item for item in val.items()]
    log.debug('datastore set params = %r', params)
    hookio.runclient.main(['-', 'datastore', 'set', key] + params)
    out, err = capsys.readouterr()
    assert json.loads(out) == "OK"
    assert not err
    hookio.runclient.main(['-', 'datastore', 'get', key])
    out, err = capsys.readouterr()
    assert json.loads(out) == val
    assert not err
    hookio.runclient.main(['-', 'datastore', 'recent'])
    out, err = capsys.readouterr()
    assert out
    res = json.loads(out)
    assert len(res) >= 5 or key in res
    assert not err
    hookio.runclient.main(['-', 'datastore', 'del', key])
    out, err = capsys.readouterr()
    assert json.loads(out) == 1
    assert not err
    hookio.runclient.main(['-', 'datastore', 'del', key])
    out, err = capsys.readouterr()
    assert json.loads(out) == 0
    assert not err
    hookio.runclient.main(['-', 'datastore', 'get', key])
    out, err = capsys.readouterr()
    assert json.loads(out) is None
    assert not err
