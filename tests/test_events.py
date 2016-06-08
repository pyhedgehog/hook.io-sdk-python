#!/usr/bin/env python
import time
import hookio
import threading
import itertools
import functools
import json
import logging
from six.moves import queue

log = logging.getLogger(__name__)
get_error_model = {
    "error": True,
    "message": """\
"anonymous" does not have the role "events::read" which is required to access "/marak/events"

If you are the owner of this resource try logging in at https://hook.io/login

If any access keys have been created you can also provide \
a `hook_private_key` parameter to access the service.\
""",
    "user": "anonymous",
    "role": "events::read",
    "type": "unauthorized-role-access"
}

create_error_model = {
    "error": True,
    "message": """\
"anonymous" does not have the role "hook::create" which is required to access "/new"

If you are the owner of this resource try logging in at https://hook.io/login

If any access keys have been created you can also provide \
a `hook_private_key` parameter to access the service.\
""",
    "user": "anonymous",
    "role": "hook::create",
    "type": "unauthorized-role-access"
}


def setup_function(function):
    if not logging.root.handlers:
        format = '%(asctime)s:%(threadName)s:' + logging.BASIC_FORMAT
        logging.basicConfig(level=logging.DEBUG, format=format)
    log.debug('setting up %s', function)


def test_events():
    sdk = hookio.createClient({'max_retries': 3})

    res = sdk.events.get('marak')
    assert type(res) == list
    prev_hit = max(row['time'] for row in res)
    # counters = itertools.groupby(sorted(res, key=lambda row:row['type']), lambda row:row['type'])
    # prev_counters = dict((k,len(list(v))) for k,v in counters)

    time.sleep(1)  # wait for time change
    res = sdk.events.get('marak', anonymous=True)
    assert res == get_error_model
    res = sdk.hook.source('marak/echo')
    # source = res
    assert res.startswith("module['exports']")
    time.sleep(15)  # Wait for events processing on server side

    res = sdk.events.get('marak')
    assert type(res) == list
    # assert max(row['time'] for row in res) > prev_hit
    new_list = [row['type'] for row in res if row['time'] > prev_hit]
    # all_list = [row['type'] for row in res]
    # counters = itertools.groupby(sorted(res, key=lambda row:row['type']), lambda row:row['type'])
    # counters = dict((k,(prev_counters.get(k, 0), len(list(v)))) for k,v in counters)
    assert new_list
    # check = 'events::read', 'hook::create', 'hook::source::read'
    # assert any(e in new_list for e in check)


def stream_process(q, e):
    def _stream_process(item):
        q.put(item)
        if e.wait(0.1):
            raise SystemExit
    return _stream_process


def noop(arg):
    return arg


def async_events_stream_template(name, func_factory, line2obj):
    sdk = hookio.createClient({'max_retries': 3})
    assert sdk.hook_private_key
    q = queue.Queue()
    e = threading.Event()
    func = functools.partial(sdk.events.stream, 'marak')
    thread_func = func_factory(func, stream_process(q, e))
    t = threading.Thread(name=name, target=thread_func)
    t.daemon = 1
    t.start()
    for i in itertools.count():
        assert i < 200
        try:
            line = q.get(timeout=1)
        except queue.Empty:
            break
        assert line
        obj = line2obj(line)
        assert 'time' in obj
    res = sdk.events.get('marak', anonymous=True)
    assert res == get_error_model
    e.set()
    try:
        line = q.get(timeout=60)
    except queue.Empty:
        # warning
        return
    assert line
    obj = line2obj(line)
    assert 'time' in obj


def test_events_stream_raw():
    def func_factory(func, streaming):
        return functools.partial(func, streaming=streaming, raw=True)
    async_events_stream_template("test_events_stream_raw", func_factory, json.loads)


def test_events_stream_obj():
    def func_factory(func, streaming):
        return functools.partial(func, streaming=streaming, raw=False)
    async_events_stream_template("test_events_stream_obj", func_factory, noop)


def stream_iter_thread(streaming, func):
    gen = func()
    try:
        for row in gen:
            log.debug('stream_iter_thread: %r', row)
            streaming(row)
    except SystemExit:
        gen.close()
        raise


def test_events_stream_iter_raw():
    def func_factory(func, streaming):
        def iter_factory():
            resp = func(streaming=True, raw=True)
            for line in resp.iter_lines(chunk_size=1):
                if not isinstance(line, str):
                    line = line.decode(resp.encoding or 'utf-8', errors='replace')
                yield line
        return functools.partial(stream_iter_thread, streaming, iter_factory)
    async_events_stream_template("test_events_stream_iter_raw", func_factory, json.loads)


def test_events_stream_iter():
    def func_factory(func, streaming):
        def iter_factory():
            res = func(streaming=True, raw=False)
            assert isinstance(res, hookio.utils.Response2JSONLinesIterator)
            iterobj = iter(res)
            try:
                for row in iterobj:
                    yield row
            finally:
                res.response.close()
                iterobj.close()
        return functools.partial(stream_iter_thread, streaming, iter_factory)
    async_events_stream_template("test_events_stream_iter", func_factory, noop)
