#!/usr/bin/env python
import hookio


def test_metrics():
    sdk = hookio.createClient({'max_retries': 3})

    res = sdk.metrics.hits('marak/echo', anonymous=True)
    assert type(res) == int
    prev_hits = res

    res = sdk.hook.run('marak/echo', {}, anonymous=True)
    assert res == {"param1": "foo", "param2": "bar"}

    res = sdk.metrics.hits('marak/echo')
    assert type(res) == int
    assert res > prev_hits
