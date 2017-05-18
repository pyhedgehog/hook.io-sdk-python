#!/usr/bin/env python
import random
import logging
import posixpath
import pytest
from six.moves import reduce

log = logging.getLogger(__name__)
unclutter_prefix = 'ef1b6b33-d3c9-4cc6-85d8-6a8f27c57c21'
unclutter_prefix = '%s-%08X' % (unclutter_prefix, random.randrange(0x10000000, 0x7FFFFFFF))
readdir_keys_model = set(['bucket','contentType','crc32c','etag','generation','id','kind','md5Hash','mediaLink','metageneration','name','selfLink','size','storageClass','timeCreated','timeStorageClassUpdated','updated'])


def test_files(sdk):
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

    res = sdk.files.writeFile(fname, val)
    assert res == stat_model

    res = sdk.files.stat(fname)
    assert res == stat_model

    res = sdk.files.readFile(fname)
    assert res == read_model

    res = sdk.files.readdir("/")
    readdir_keys = reduce(set.union, (set(row) for row in res), set())
    assert readdir_keys == readdir_keys_model
    l = [row for row in res if row["name"].endswith(bname)]
    assert len(l) == 1

    res = sdk.files.removeFile(fname)
    assert res == "removing"

    resp = sdk.files.removeFile(fname, raw=True)
    assert resp.text == "Not Found"

    pytest.raises(ValueError, sdk.files.removeFile, fname)
