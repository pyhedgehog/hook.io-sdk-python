#!/usr/bin/env python
import random
import hookio

unclutter_prefix = 'f8f8f5b2-b160-427c-95d6-32d48316a21b'
unclutter_prefix = '%s::%08X' % (unclutter_prefix, random.randrange(0x10000000, 0x7FFFFFFF))


def test_datastore():
    key = unclutter_prefix + '::test_key'
    val = {'i': 1, 's': 'qwerty', 'o': {'uuid': unclutter_prefix}, 'n': None}
    sdk = hookio.createClient({'max_retries': 3})

    res = sdk.datastore.recent(anonymous=True)
    assert 'error' in res
    assert res['error'] is True
    assert res['type'] == 'unauthorized-role-access'
    assert res['role'] == 'datastore::recent'
    assert 'datastore::recent' in res['message']

    assert sdk.hook_private_key
    res = sdk.datastore.set(key, val)
    assert res == "OK"
    res = sdk.datastore.get(key)
    assert res == val
    res = sdk.datastore.recent()
    assert type(res) == list
    assert len(res) >= 5 or key in res
    res = sdk.datastore.delete(key)
    assert res == 1
    res = sdk.datastore.delete(key)
    assert res == 0
    res = sdk.datastore.get(key)
    assert res is None
