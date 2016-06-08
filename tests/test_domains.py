#!/usr/bin/env python
import hookio


def test_domains():
    sdk = hookio.createClient({'max_retries': 3})
    assert sdk.hook_private_key
    res = sdk.domains.all(anonymous=True)
    assert 'error' in res
    assert res['error'] is True
    assert res['type'] == 'unauthorized-role-access'
    assert res['role'] == 'domain::find'
    assert 'domain::find' in res['message']
    res = sdk.domains.all()
    assert type(res) == list
