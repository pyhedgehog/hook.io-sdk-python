#!/usr/bin/env python
import hookio
import random

unclutter_prefix = '2d7008ff-8faa-4511-8ef9-64d1176db093'
unclutter_prefix = '%s-%08x' % (unclutter_prefix, random.randrange(0x10000000, 0x7FFFFFFF))


def test_keys():
    sdk = hookio.createClient()

    res = sdk.keys.checkAccess({'role': 'keys::create'})
    assert res == {'hasAccess': True}

    res = sdk.keys.info()
    assert res
    assert 'roles' in res
    assert 'keys::create' in res['roles'].split(',')
    info_model = res

    res = sdk.keys.info(check_key=sdk.hook_private_key)
    assert res == info_model

    res = sdk.keys.info(hook_private_key=sdk.hook_private_key, raw=True)
    assert res == info_model


def test_keys_admin():
    name = unclutter_prefix + '-key'
    sdk = hookio.createClient()

    res = sdk.keys.create(name, {'roles': 'pythonsdktest::test'})
    assert res
    assert res['name'] == name
    assert res['roles'] == 'pythonsdktest::test'

    res = sdk.keys.destroy(name)
    assert res == {"status": "deleted"}
