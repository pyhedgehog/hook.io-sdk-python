#!/usr/bin/env python
# import os
# import sys
import hookio
import pprint

if 'Hook' not in globals():
    Hook = {'env': {}}

Hook = hookio.init_sdk(Hook)
# print('dir() = ' + repr(dir()))
# print('osenv = ' + repr(os.environ))
print('Hook = ' + repr(Hook.keys()))
pprint.pprint(Hook)
# Hook.sdk = hookio.createClient()
print('Hook.env = ' + repr(Hook.env))
print('Hook.sdk = ' + repr(Hook.sdk))
# print('base_url = ' + repr(Hook.sdk.base_url))
# print('hook_private_key = ' + repr(Hook.sdk.hook_private_key))
print(Hook.sdk.datastore.recent())
# pprint.pprint(Hook.sdk.logs.read('pyhedgehog/gateway-python', raw=False))
# pprint.pprint(Hook.sdk.logs.read('marak/echo', raw=False))
Hook.sdk.logs.write(Hook.sdk.env.get(raw=1).text)
