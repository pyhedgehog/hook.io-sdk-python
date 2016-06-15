#!/usr/bin/env python
def test_domains(sdk):
    res = sdk.domains.all(anonymous=True)
    assert 'error' in res
    assert res['error'] is True
    assert res['type'] == 'unauthorized-role-access'
    assert res['role'] == 'domain::find'
    assert 'domain::find' in res['message']
    res = sdk.domains.all()
    assert type(res) == list
