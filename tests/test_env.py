#!/usr/bin/env python
import random
import hookio

unclutter_prefix = '6cb3c3de-37b4-470c-b2e7-59bcdeec081c'
unclutter_prefix = '%s::%08X' % (unclutter_prefix, random.randrange(0x10000000, 0x7FFFFFFF))


def test_env():
    key = unclutter_prefix + '::test_key'
    val = ''.join(reversed(unclutter_prefix))
    sdk = hookio.createClient({'max_retries': 3})

    res = sdk.env.get(anonymous=True)
    assert 'error' in res
    assert res['error'] is True
    assert res['type'] == 'unauthorized-role-access'
    assert res['role'] == 'env::read'
    assert 'env::read' in res['message']

    assert sdk.hook_private_key
    res = sdk.env.get()
    assert res is None or type(res) == dict
    res = sdk.env.set({key: val})
    assert type(res) == dict
    assert key in res
    assert res[key] == val
    res = sdk.env.get()
    assert type(res) == dict
    assert key in res
    assert res[key] == val
    res = sdk.env.set({key: None})
    assert type(res) == dict
    assert key not in res
    res = sdk.env.get()
    if res is not None:
        assert type(res) == dict
        assert key not in res
