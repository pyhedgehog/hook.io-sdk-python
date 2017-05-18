#!/usr/bin/env python
import random

unclutter_prefix = '460d3206-5670-4ea5-ac98-c9fb03493dec'
unclutter_prefix = '%s-%08x' % (unclutter_prefix, random.randrange(0x10000000, 0x7FFFFFFF))


def test_metrics(sdk):
    data = {"param2": "123", unclutter_prefix: "random", "a": "2"}

    res = sdk.metrics.hits('examples/echo', anonymous=True)
    assert type(res) == int
    prev_hits = res

    res = sdk.hook.run('examples/echo', data, anonymous=True)
    assert res == data

    res = sdk.metrics.hits('examples/echo')
    assert type(res) == int
    assert res > prev_hits
