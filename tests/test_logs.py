#!/usr/bin/env python
import time
import hookio
import threading
import itertools
import functools
import json
import random
import logging
from six.moves import queue

log = logging.getLogger(__name__)
unclutter_prefix = 'b834c0f0-6a9a-483e-8297-c301eb4e0112'
unclutter_prefix = '%s::%08x' % (unclutter_prefix, random.randrange(0x10000000, 0x7FFFFFFF))


def setup_function(function):
    if not logging.root.handlers:
        format = '%(asctime)s:%(threadName)s:' + logging.BASIC_FORMAT
        logging.basicConfig(level=logging.DEBUG, format=format)
    log.debug('setting up %s', function)


def test_logs():
    data_model = {"param1": "foo", "param2": "bar", unclutter_prefix: "test_logs"}
    cron_model = {"param1": "foo", "param2": "bar", "ranFromCron": "true"}
    sdk = hookio.createClient()

    res = sdk.logs.read('marak/echo')
    assert type(res) == list
    prev_hit = max(json.loads(row)['time'] for row in res)

    time.sleep(1)  # wait for time change
    res = sdk.hook.run('marak/echo', {unclutter_prefix: "test_logs"})
    assert res == data_model

    time.sleep(5)  # Wait for log events processing on server side

    res = sdk.logs.read('marak/echo', raw=False, raw_data=False)
    assert type(res) == list
    assert max(row['time'] for row in res) > prev_hit
    assert any(row['data'] in (data_model, cron_model) for row in res)

logsource_template = """\
import sys;\
sys.stdout.write('"%s"');\
sys.stderr.write('{"type":"log","payload":{"entry":"test-%s"}}\\n');\
sys.stderr.flush();\
sys.stdout.flush();\
"""


def test_logs_flush():
    name = ('log' + unclutter_prefix.replace('::', '-')).lower()
    assert len(name) <= 50
    val = ''.join(reversed(unclutter_prefix))
    resource = dict(language='python', source=logsource_template % (val, val))
    sdk = hookio.createClient()
    assert sdk.hook_private_key
    res = sdk.hook.create(name, resource)
    assert type(res) == dict
    assert res['status'] == 'created'
    assert type(res['hook']) == dict
    assert res['hook']['language'] == resource['language']
    assert res['hook']['source'] == resource['source']
    assert res['hook']['name'] == name
    owner = res['hook']['owner']
    url = '%s/%s' % (owner, name)

    res = sdk.logs.read(url, raw_data=False)
    assert type(res) == list
    assert not res

    res = sdk.hook.run(url, {}, anonymous=True)
    assert res == val

    res = sdk.logs.read(url, raw_data=False)
    assert type(res) == list
    assert len(res) == 1
    assert res[0]['data'] == 'test-' + val

    res = sdk.logs.flush(url)
    res = sdk.logs.read(url, raw_data=False)
    assert type(res) == list
    assert not res


def stream_process(q, e):
    def _stream_process(item):
        log.debug('stream_process: %r', item)
        q.put(item)
        if e.wait(0.1):
            raise SystemExit
    return _stream_process


def noop(arg):
    return arg


def data_obj(row):
    return row['data']


def data_json(row):
    return json.loads(row['data'])


def async_logs_stream_template(name, func_factory, line2obj, obj2data):
    data_model = {"param1": "foo", "param2": "bar", unclutter_prefix: name}
    sdk = hookio.createClient()
    q = queue.Queue()
    e = threading.Event()
    func = functools.partial(sdk.logs.stream, 'marak/echo', chunk_size=1)
    thread_func = func_factory(func, stream_process(q, e))
    t = threading.Thread(name="test_logs_stream_raw", target=thread_func)
    t.daemon = 1
    t.start()
    timeout = 60
    for i in itertools.count():
        assert i < 200
        try:
            line = q.get(timeout=timeout)
        except queue.Empty:
            break
        timeout = 1
        assert line
        obj = line2obj(line)
        assert 'time' in obj
    res = sdk.hook.run('marak/echo', {unclutter_prefix: name}, anonymous=True)
    assert res == data_model
    for i in itertools.count():
        assert i < 20
        try:
            line = q.get(timeout=20)
        except queue.Empty:
            break
        assert line
        obj = line2obj(line)
        assert 'time' in obj
        assert 'data' in obj
        data = obj2data(obj)
        if data == data_model:
            e.set()
            break


def stream_iter_thread(streaming, func):
    gen = func()
    try:
        for row in gen:
            log.debug('stream_iter_thread: %r', row)
            streaming(row)
    except SystemExit:
        gen.close()
        raise


def test_logs_stream_raw():
    def func_factory(func, streaming):
        return functools.partial(func, streaming=streaming)
    async_logs_stream_template("test_logs_stream_raw", func_factory, json.loads, data_json)


def test_logs_stream_obj():
    def func_factory(func, streaming):
        return functools.partial(func, streaming=streaming, raw=False)
    async_logs_stream_template("test_logs_stream_obj", func_factory, noop, data_json)


def test_logs_stream_obj_data():
    def func_factory(func, streaming):
        return functools.partial(func, streaming=streaming, raw=False, raw_data=False)
    async_logs_stream_template("test_logs_stream_obj_data", func_factory, noop, data_obj)


def test_logs_stream_iter_raw():
    def func_factory(func, streaming):
        def iter_factory():
            resp = func(streaming=True)
            for line in resp.iter_lines(chunk_size=1):
                if not isinstance(line, str):
                    line = line.decode(resp.encoding or 'utf-8', errors='replace')
                yield line
        return functools.partial(stream_iter_thread, streaming, iter_factory)
    async_logs_stream_template("test_logs_stream_iter_raw", func_factory, json.loads, data_json)


def test_logs_stream_iter():
    def func_factory(func, streaming):
        func = functools.partial(func, streaming=True, raw=False)
        return functools.partial(stream_iter_thread, streaming, func)
    async_logs_stream_template("test_logs_stream_iter", func_factory, noop, data_json)


def test_logs_stream_iter_data():
    def func_factory(func, streaming):
        func = functools.partial(func, streaming=True, raw=False, raw_data=False)
        return functools.partial(stream_iter_thread, streaming, func)
    async_logs_stream_template("test_logs_stream_iter_data", func_factory, noop, data_obj)
