#!/usr/bin/env python
import re
import sys
import time
import requests
import logging
import hookio.keys
from six.moves.html_parser import HTMLParser
from six.moves.html_entities import name2codepoint
from six import unichr

log = logging.getLogger(__name__)
max_retries = 3


class RolesParser(HTMLParser):
    roles = newroles = states = savedata = None

    def handle_starttag(self, tag, attrs):
        if tag.lower() != 'div':
            return
        if attrs and any(n.lower() == 'class' and 'availableRoles' in v.split() for n, v in attrs):
            log.debug('Start processing roles')
            self.newroles = []
            self.states = ['top']
            return
        if self.newroles is not None:
            log.debug('Pushing div for role %d', len(self.newroles))
            self.states.append('role')
            self.save_bgn()

    def handle_endtag(self, tag):
        if tag.lower() != 'div':
            return
        if self.states is None:
            return
        tp = self.states.pop()
        assert tp in ('role', 'top')
        if tp == 'role':
            role = self.save_end()
            log.debug('Found role %r', role)
            self.newroles.append(role)
            return
        if tp == 'top':
            assert not self.states
            self.roles = self.newroles
            log.debug('Processed roles: %r', self.roles)
            self.newroles = None
            self.states = None

    def handle_data(self, data):
        if self.savedata is None:
            return
        self.savedata = self.savedata + data

    def handle_entityref(self, name):
        if self.savedata is None:
            return
        c = unichr(name2codepoint[name])
        log.debug("Named ent: &%s; = %r", name, c)
        self.handle_data(c)

    def handle_charref(self, name):
        if self.savedata is None:
            return
        if name[:1].lower() in ('x', 'u'):
            c = unichr(int(name[1:], 16))
        else:
            c = unichr(int(name))
        log.debug("Num ent: &%s; = %r", name, c)
        self.handle_data(c)

    def save_bgn(self):
        """Begins saving character data in a buffer.

        Retrieve the stored data via the save_end() method.  Use of the
        save_bgn() / save_end() pair may not be nested.

        """
        self.savedata = ''

    def save_end(self):
        """Ends buffering character data and returns all data saved since
        the preceding call to the save_bgn() method.
        """
        data = self.savedata
        self.savedata = None
        return data


def test_roles(cache):
    roles = cache.get('hook.io/roles', None)
    if roles is not None:
        t, roles = roles
        if time.time() - t > 86400:
            roles = None
    if roles is None:
        for i in range(max_retries):
            try:
                roles = request_roles()
            except Exception:
                if i == max_retries-1:
                    raise
                continue
            cache.set('hook.io/roles', [time.time(), roles])
            break
    assert roles == sorted(hookio.keys.roles)


def request_roles():
    r = requests.get('https://hook.io/roles')
    r.raise_for_status()
    text = r.text
    if False:
        p = RolesParser()
        p.feed(text)
        p.close()
        roles = sorted(p.roles)
    else:
        roles = sorted(set(re.findall('>\\s*(\\w+(?:::\\w+)+)\\s*<', text)))
    assert roles
    return roles


if __name__=='__main__':
    roles = request_roles()
    print('\n'.join(roles))
    sys.stderr.write('%s\n' % (hookio.keys.roles == roles,))
