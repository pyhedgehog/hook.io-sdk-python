#!/usr/bin/env python
import requests
import htmllib
import formatter
import hookio.keys


class RolesParser(htmllib.HTMLParser):
    roles = newroles = states = None

    def start_div(self, attrs):
        if attrs and any(n.lower() == 'class' and 'availableRoles' in v.split() for n, v in attrs):
            self.newroles = []
            self.states = ['top']
            return
        if self.newroles is not None:
            self.states.append('role')
            self.save_bgn()

    def end_div(self):
        if self.states is None:
            return
        tp = self.states.pop()
        assert tp in ('role', 'top')
        if tp == 'role':
            self.newroles.append(self.save_end())
            return
        if tp == 'top':
            assert not self.states
            self.roles = self.newroles
            self.newroles = None
            self.states = None


def test_roles():
    r = requests.get('https://hook.io/roles')
    text = r.text
    # text = open('roles', 'rt').read()
    p = RolesParser(formatter.NullFormatter())
    p.feed(text)
    p.close()
    assert p.roles == hookio.keys.roles
