#!/usr/bin/env python
import os
import sys
import types
import logging
import hookio
import copy
import json
import pytest

log = logging.getLogger(__name__)


def test_create_client():
    sdk = hookio.createClient()
    assert sdk.hook_private_key
    assert sdk.base_url == 'https://hook.io:443/'
    foosdk = hookio.createClient({'host': None}, os.environ)
    assert foosdk.base_url == 'http://127.0.0.1:9999/'
    assert not foosdk.session.verify
    foosdk = hookio.createClient({'protocol': 'http'})
    assert foosdk.base_url == 'http://hook.io:80/'
    foosdk = hookio.createClient({'port': 8080})
    assert foosdk.base_url == 'http://hook.io:8080/'
    foosdk = hookio.createClient({'port': 443, 'verify': True})
    assert foosdk.base_url == 'https://hook.io:443/'
    assert foosdk.session.verify
    assert not hasattr(sdk, 'noncence')
    foosdk = hookio.createClient(None, {'hookAccessKey': sdk.hook_private_key})
    assert foosdk.base_url == 'https://hook.io:443/'
    assert foosdk.session.verify
    assert foosdk.hook_private_key == sdk.hook_private_key


def check_HookNS(HookNS, HookOrig, HookCopy, model_url):
    assert HookNS is not HookCopy
    assert HookNS.env is HookCopy['env']
    assert HookNS.env is not HookOrig['env']
    assert HookNS.env == HookOrig['env']
    assert HookNS.req is HookCopy['req']
    assert HookNS.req is not HookOrig['req']
    assert HookNS.req == HookOrig['req']
    assert isinstance(HookNS.sdk, hookio.Client)
    assert HookNS.sdk.base_url == 'https://hookydooky.io:443/'
    assert not HookNS.sdk.session.verify


def test_install_hook():
    savemain = sys.modules.get('__main__', None)
    try:
        HookOrig = {'env': {}}
        HookOrig['req'] = {'host': 'hookydooky.io', 'headers': {}}
        HookOrig['params'] = {}
        main = sys.modules['__main__'] = types.ModuleType('__main__')
        HookCopy = copy.deepcopy(HookOrig)
        HookNS = hookio.install_hook_sdk(HookCopy)
        assert HookCopy == HookOrig
        assert not hasattr(main, 'Hook')
        check_HookNS(HookNS, HookOrig, HookCopy, 'https://hookydooky.io:443/')
        main.Hook = HookCopy
        sdk = hookio.createClient()
        assert sdk.base_url == 'https://hookydooky.io:443/'
        assert not sdk.session.verify
        HookOrig['req']['headers']['hookio-private-key'] = sdk.hook_private_key
        main.Hook = HookCopy = copy.deepcopy(HookOrig)
        HookNS = hookio.install_hook_sdk(main.Hook)
        assert main.Hook is HookNS
        check_HookNS(HookNS, HookOrig, HookCopy, 'https://hookydooky.io:443/')
        del HookOrig['req']['headers']['hookio-private-key']
        HookOrig['params']['hook_private_key'] = sdk.hook_private_key
        main.Hook = HookCopy = copy.deepcopy(HookOrig)
        HookNS = hookio.install_hook_sdk(main.Hook)
        assert main.Hook is HookNS
        check_HookNS(HookNS, HookOrig, HookCopy, 'https://hookydooky.io:443/')
        del HookOrig['params']['hook_private_key']
        HookOrig['env']['hookAccessKey'] = sdk.hook_private_key
        main.Hook = HookCopy = copy.deepcopy(HookOrig)
        HookNS = hookio.install_hook_sdk(main.Hook)
        assert main.Hook is HookNS
        check_HookNS(HookNS, HookOrig, HookCopy, 'https://hookydooky.io:443/')
        del HookOrig['env']['hookAccessKey']
        HookOrig['hookAccessKey'] = sdk.hook_private_key
        main.Hook = HookCopy = copy.deepcopy(HookOrig)
        HookNS = hookio.install_hook_sdk(main.Hook)
        assert main.Hook is HookNS
        check_HookNS(HookNS, HookOrig, HookCopy, 'https://hookydooky.io:443/')
    finally:
        sys.modules['__main__'] = savemain


def test_misc_utils():
    assert hookio.utils.opt_json(hookio.utils.Namespace(content=''), False, True) is None
    r = hookio.utils.Namespace(content='', json=lambda: json.loads(r.content))
    pytest.raises(ValueError, hookio.utils.opt_json, r, False)
    r = hookio.utils.Namespace(content='{"a":1,"b":"2"}', json=lambda: json.loads(r.content))
    assert hookio.utils.opt_json(r, True) is r
    assert hookio.utils.opt_json(r, False) == dict(a=1, b="2")


def test_client_logs(capsys):
    log_model = {'type': 'log', 'payload': {'entry': 'test_client_logs'}}
    savemain = sys.modules.get('__main__', None)
    try:
        main = sys.modules['__main__'] = types.ModuleType('__main__')
        main.Hook = Hook = {'env': {}}
        Hook['req'] = {'host': 'hook.io', 'headers': {}}
        Hook['params'] = {}
        sdk = hookio.createClient(None, Hook['env'], Hook)
        out, err = capsys.readouterr()  # ignore all previous output
        sdk.logs.write('test_client_logs')
        out, err = capsys.readouterr()
        assert not out
        assert json.loads(err.strip('\n')) == log_model
    finally:
        sys.modules['__main__'] = savemain
