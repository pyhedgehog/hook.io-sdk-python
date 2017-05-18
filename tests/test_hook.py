#!/usr/bin/env python
# import warnings
import logging
import time
import random
import hookio
import json
from six import StringIO, BytesIO, b

log = logging.getLogger(__name__)
unclutter_prefix = 'eb43df31'
unclutter_prefix = '%s_%08X' % (unclutter_prefix, random.randrange(0x10000000, 0x7FFFFFFF))


def test_hook_anonymous():
    sdk0 = hookio.createClient()
    assert sdk0.hook_private_key
    sdk = hookio.createClient(None, {})
    assert not sdk.hook_private_key
    res = sdk.hook.run('marak/echo', {})
    assert res in [{},{"param1": "foo", "param2": "bar"}]
    res = sdk.hook.run('marak/echo', {}, anonymous=False)
    assert res in [{},{"param1": "foo", "param2": "bar"}]
    res = sdk.hook.run('marak/echo', {}, hook_private_key=sdk0.hook_private_key)
    assert res in [{},{"param1": "foo", "param2": "bar"}]


def test_hook_run(sdk):
    data = {"param2": "123", unclutter_prefix: "random", "a": "2"}
    res = sdk.hook.run('marak/echo', data, anonymous=True)
    if "param1" in res: # 
        data["param1"] = "foo"
    assert res == data
    datastr = "param2=123&" + unclutter_prefix + "=random&a=1&a=2"
    res = sdk.hook.run('marak/echo', datastr, anonymous=True)
    assert res == data

    def streaming(s):
        log.debug('test_hook_run.streaming(%r)', s)
        keep.append(s)
        out.write(s)

    out = StringIO()
    keep = []
    resp = sdk.hook.run('marak/echo', StringIO(), streaming=streaming, anonymous=True)
    resp.raise_for_status()
    res = out.getvalue()
    assert res
    assert res == ''.join(keep)
    res = json.loads(res)
    assert res == {"streaming": "true", "param1": "foo", "param2": "bar"}
    resp = sdk.hook.run('marak/echo', StringIO(), streaming=True, anonymous=True)
    resp.raise_for_status()
    res = resp.json()
    assert res == {"streaming": "true", "param1": "foo", "param2": "bar"}

    sdk.line_streaming = False
    out = BytesIO()
    keep = []
    resp = sdk.hook.run('marak/echo', StringIO(), streaming=streaming, anonymous=True)
    resp.raise_for_status()
    res = out.getvalue()
    assert res
    assert res == b('').join(keep)
    res = json.loads(res.decode('utf-8'))
    assert res == {"streaming": "true", "param1": "foo", "param2": "bar"}


def test_hook_info(sdk):
    res = sdk.hook.source('marak/echo')
    assert res
    source = res
    res = sdk.hook.resource('marak/echo')
    assert res['language'] == 'javascript'
    assert res['source'] == source
    assert res['owner'] == 'marak'
    assert res['name'] == 'echo'


def test_hook_admin(sdk, cache):
    name = ('test' + unclutter_prefix + 'hook').lower()
    assert len(name) <= 50
    val1 = ''.join(reversed(unclutter_prefix)) + '-1'
    val2 = ''.join(reversed(unclutter_prefix)) + '-2'
    source1 = 'print(%r)' % (val1,)
    source2 = 'print(repr(%r))' % (val2,)
    resource = {
        'language': 'python',
        'source': source1,
        'hookSource': 'code',
    }

    resource_copy = resource.copy()
    res = sdk.hook.create(name, resource)
    assert type(res) == dict
    assert res['status'] == 'created'
    assert type(res['hook']) == dict
    assert res['hook']['language'] == resource['language']
    assert res['hook']['source'] == source1
    assert res['hook']['name'] == name
    assert resource == resource_copy  # check it's not modified
    owner = res['hook']['owner']
    url = '%s/%s' % (owner, name)

    try:
        res = sdk.hook.source(url)
        assert res == resource['source']

        sdk.session.close()
        r = sdk.hook.source(url, raw=True)
        assert r.text == resource['source']

        res = sdk.hook.resource(url)
        assert res['language'] == resource['language']
        assert res['source'] == source1
        assert res['name'] == name

        res = sdk.hook.run(url, {}, raw=True, anonymous=True)
        assert res.text.rstrip('\n') == val1

        res = sdk.hook.update(url, {'source': source2, 'language': resource['language']})
        assert type(res) == dict
        assert res['status'] == 'updated'
        assert res['value']['language'] == resource['language']
        assert res['value']['source'] == source2
        assert res['value']['name'] == name

        res = sdk.hook.resource(url)
        assert res['language'] == resource['language']
        assert res['source'] == source2
        assert res['name'] == name

        res = sdk.hook.run(url, {}, raw=True, anonymous=True)
        assert res.text.rstrip('\n') == repr(val2)
    finally:
        time.sleep(5)  # wait to avoid DoS penalty
        res = sdk.hook.destroy(url)
    assert res['status'] == 'deleted'
    assert res['name'] == name
    assert res['owner'] == owner
    assert res['message'] == 'Hook "' + name + '" has been deleted!'
    res = sdk.hook.run(url, {}, raw=True, anonymous=True)
    assert res.text == '404 missing!'
