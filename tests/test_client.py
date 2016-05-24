#!/usr/bin/env python
import os
import sys
import types
import logging
import hookio

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


def test_create_hook():
    savemain = sys.modules.get('__main__', None)
    try:
        Hook = {'env': {}}
        Hook['req'] = {'host': 'hookydooky.io', 'headers': {}}
        Hook['params'] = {}
        main = sys.modules['__main__'] = types.ModuleType('__main__')
        main.Hook = Hook.copy()
        sdk = hookio.createClient()
        assert sdk.base_url == 'https://hookydooky.io:443/'
        assert not sdk.session.verify
    finally:
        sys.modules['__main__'] = savemain
