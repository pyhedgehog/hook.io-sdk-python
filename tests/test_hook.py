#!/usr/bin/env python
import warnings
import logging
import random
import hookio
import json
from six import StringIO

log = logging.getLogger(__name__)
unclutter_prefix = 'eb43df31'
unclutter_prefix = '%s_%08X' % (unclutter_prefix, random.randrange(0x10000000, 0x7FFFFFFF))


def setup_function(function):
    if not logging.root.handlers:
        logging.basicConfig(level=logging.DEBUG)
    log.debug('setting up %s', function)


def test_hook_run():
    sdk = hookio.createClient()
    res = sdk.hook.run('marak/echo', {"param2": "222", unclutter_prefix: "random"}, anonymous=True)
    assert res == {"param1": "foo", "param2": "222", unclutter_prefix: "random"}

    out = StringIO()
    keep = []

    def streaming(s):
        log.debug('test_hook_run.streaming(%r)', s)
        keep.append(s)
        out.write(s)

    res = sdk.hook.run('marak/echo', StringIO(), streaming=streaming, anonymous=True)
    res.raise_for_status()
    res = out.getvalue()
    assert res
    assert res == ''.join(keep)
    res = json.loads(res)
    assert res == {"streaming": "true", "param1": "foo", "param2": "bar"}


def test_hook_info():
    sdk = hookio.createClient()
    res = sdk.hook.source('marak/echo')
    assert res
    source = res
    res = sdk.hook.resource('marak/echo')
    assert res['language'] == 'javascript'
    assert res['source'] == source
    assert res['owner'] == 'marak'
    assert res['name'] == 'echo'


def test_hook_admin():
    # FIXME: https://github.com/bigcompany/hook.io/issues/237
    warnings.warn("test_hook_admin", UserWarning)
    return
    name = 'test' + unclutter_prefix + 'hook'
    assert len(name) <= 50
    val1 = ''.join(reversed(unclutter_prefix)) + '-1'
    val2 = ''.join(reversed(unclutter_prefix)) + '-2'
    source1 = 'print(%r)' % (val1,)
    source2 = 'print(repr(%r))' % (val2,)
    resource = {
        'language': 'python',
        'source': source1,
        'isPublic': True,
        'isPrivate': False,
        'hookSource': 'code',
    }
    sdk = hookio.createClient()

    assert sdk.hook_private_key
    res = sdk.hook.create(name, resource)
    assert type(res) == dict
    assert res['status'] == 'created'
    assert type(res['hook']) == dict
    assert res['hook']['language'] == resource['language']
    assert res['hook']['source'] == source1
    assert res['hook']['name'] == name
    owner = res['hook']['owner']
    url = '%s/%s' % (owner, name)
    res = sdk.hook.source(url)
    assert res == resource['source']
    res = sdk.hook.resource(url)
    assert res['language'] == resource['language']
    assert res['source'] == source1
    assert res['name'] == name
    res = sdk.hook.run(url, anonymous=True)
    assert res == val1
    res = sdk.hook.update(url, {'source': source2})
    assert res == "OK"
    res = sdk.hook.resource(url)
    assert res['language'] == resource['language']
    assert res['source'] == source2
    assert res['name'] == name
    res = sdk.hook.run(url, anonymous=True)
    assert res == val2
    res = sdk.hook.destroy(url)
    assert res['status'] == 'deleted'
    assert res['name'] == name
    assert res['owner'] == owner
    assert res['message'] == 'Hook "' + name + '" has been deleted!'
