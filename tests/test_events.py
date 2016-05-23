#!/usr/bin/env python
import time
import hookio

error_model = {
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


def test_events():
    sdk = hookio.createClient()

    res = sdk.events.get('marak')
    assert type(res) == list
    prev_hit = max(row['time'] for row in res)

    res = sdk.events.get('marak', anonymous=True)
    assert res == error_model
    time.sleep(2)

    res = sdk.events.get('marak')
    assert type(res) == list
    assert max(row['time'] for row in res) > prev_hit
