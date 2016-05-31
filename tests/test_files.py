#!/usr/bin/env python
import random
import hookio
import logging
import pytest

log = logging.getLogger(__name__)
unclutter_prefix = 'ef1b6b33-d3c9-4cc6-85d8-6a8f27c57c21'
unclutter_prefix = '%s-%08X' % (unclutter_prefix, random.randrange(0x10000000, 0x7FFFFFFF))


def setup_function(function):
    if not logging.root.handlers:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s:' + logging.BASIC_FORMAT)
    log.debug('setting up %s', function)


def test_files():
    name = unclutter_prefix
    ext = ".txt"
    bname = name + ext
    fname = "/" + bname
    val = ''.join(reversed(unclutter_prefix))
    stat_model = {
        "basename": bname,
        "contents": None,
        "dirname": "/",
        "extname": ext,
        "path": fname,
        "relative": bname,
        "stem": name
        }
    read_model = stat_model.copy()
    read_model["contents"] = val
    sdk = hookio.createClient()

    res = sdk.files.writeFile(fname, val)
    assert res == stat_model

    res = sdk.files.stat(fname)
    assert res == stat_model

    res = sdk.files.readFile(fname)
    assert res == read_model

    res = sdk.files.readdir("/")
    l = [row for row in res if row["basename"] == bname]
    assert len(l) == 1

    res = sdk.files.removeFile(fname)
    assert res == "removing"

    resp = sdk.files.removeFile(fname, raw=True)
    assert resp.text == "Not Found"

    pytest.raises(ValueError, sdk.files.removeFile, fname)
