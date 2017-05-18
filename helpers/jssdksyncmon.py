#!/usr/bin/env python
import os
import sys
import requests
try:
    import pushnotify
except ImportError:
    pushnotify = None

maxdesc = 1024


def main():
    pushtype = os.environ.get('pushtype', '')
    pushkey = os.environ.get('pushkey', '')
    repos = 'bigcompany/hook.io-sdk'
    compare = 'pyhedgehog:master...dev'
    url = 'https://api.github.com/repos/%s/compare/%s' % (repos, compare)
    html_url = 'https://github.com/%s/compare/%s' % (repos, compare)
    r = requests.get(url)
    r.raise_for_status()
    o = r.json()
    if not o['files']:
        return 0
    # html_url = o['permalink_url']
    html_url = o['html_url']
    desc1, desc2, desc3 = [], [], dict(files=0, additions=0, deletions=0)
    for f in o['files']:
        if f['status'] == 'modified':
            desc1.append('{filename} (+{additions}, -{deletions})'.format(**f))
        else:
            desc1.append('{filename} ({status})'.format(**f))
        desc2.append('{filename} ({status})'.format(**f))
        desc3['files'] += 1
        desc3['additions'] += f['additions']
        desc3['deletions'] += f['deletions']
    desc = ', '.join(desc1)
    if len(desc) > maxdesc:
        desc = '+{additions}, -{deletions}: '.format(**desc3) + (', '.join(desc2))
    if len(desc) > maxdesc:
        desc = '{files}: +{additions}, -{deletions}'.format(**desc3)
    if r.text and pushnotify and pushtype and pushkey:
        client = pushnotify.get_client(pushtype, 'hookiosdksyncmon')
        client.add_key(pushkey)
        client.notify(desc, repos + ' update', False, dict(url=html_url))
    else:
        print('\n'.join('diff --git {filename}\n{patch}\n'.format(**f)
                        .replace('\n\\ No newline at end of file', '')
                        for f in o['files'] if 'patch' in f))
        print(desc)
        print(html_url)
    return 1

if __name__ == '__main__':
    sys.exit(main())
