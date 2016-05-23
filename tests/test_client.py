#!/usr/bin/env python
import logging
import hookio

log = logging.getLogger(__name__)


def test_create_client(capsys):
    sdk = hookio.createClient()
    assert sdk.hook_private_key
    # FIXME: add tests for every createClient/Client.__init__ default-parsing branch
