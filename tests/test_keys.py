#!/usr/bin/env python
import random
import logging

log = logging.getLogger(__name__)
unclutter_prefix = '2d7008ff-8faa-4511-8ef9-64d1176db093'
unclutter_prefix = '%s-%08x' % (unclutter_prefix, random.randrange(0x10000000, 0x7FFFFFFF))


def test_keys(sdk):
    res = sdk.keys.checkAccess({'role': 'keys::create'})
    assert 'hasAccess' in res
    assert res['hasAccess'] == True

    res = sdk.keys.info()
    assert res
    assert 'roles' in res
    assert 'keys::create' in res['roles'].split(',')
    info_model = res

    res = sdk.keys.info(check_key=sdk.hook_private_key)
    assert res == info_model

    res = sdk.keys.info(hook_private_key=sdk.hook_private_key, raw=True)
    assert res == info_model

    res = sdk.keys.info(check_key=unclutter_prefix)
    assert res is None


def test_keys_admin(sdk):
    name = unclutter_prefix + '-key'
    # keys::destroy required due to https://github.com/bigcompany/hook.io/issues/243
    roles = 'pythonsdktest::test,keys::destroy'

    res = sdk.keys.create(name, {'roles': roles})
    try:
        assert res
        assert res['name'] == name
        assert res['roles'] == roles
    finally:
        res = sdk.keys.destroy(name)
    assert res == {"status": "deleted"}
