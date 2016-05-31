#!/usr/bin/env python
import os
import sys
import re
import fnmatch
import argparse

default_exclude_dirs = [
    '.cvs',          # cvs aux files
    '.git',          # git repository
    '.tox',          # tox cache
    'htmlcov',       # coverage output
]
default_exclude_masks = [
    '*.zip',
    '*.pyc',
    '*.pyo',
]
todo_re = re.compile('(?:FI' + 'XME|TO' + 'DO|HA' + 'CK).*$', re.M)


def main(argv):
    p = argparse.ArgumentParser(prog=argv[0],
                                description='Find TO' + 'DO/FI' + 'XME/HA' + 'CK markers')
    p.add_argument('--exclude-dir', '-x', default=default_exclude_dirs, action='append',
                   help='Names of directories to skip')
    p.add_argument('--exclude-mask', '-X', default=default_exclude_masks, action='append',
                   help='Masks of files to skip')
    p.add_argument('--maxsize', '-S', default=1073741824, type=int,
                   help='Maximum size of file to read')
    p.add_argument('include', nargs='*', help='Where to search. Default - current directory')
    args = p.parse_args(argv[1:])
    if not args.include:
        args.include = [os.curdir]
    args.include = map(os.path.abspath, args.include)
    res = 0
    for include in args.include:
        if os.path.isfile(include):
            fn = include
            if args.maxsize and os.path.getsize(fn) > args.maxsize:
                continue
            name = os.path.basename(fn)
            if any(fnmatch.fnmatch(name, mask) or fnmatch.fnmatch(fn, mask)
                   for mask in args.exclude_mask):
                continue
            res += check_todo(fn)
        for root, dirs, files in os.walk(include):
            for name in dirs[:]:
                if name in args.exclude_dir:
                    dirs.remove(name)
            for name in files:
                fn = os.path.join(root, name)
                if args.maxsize and os.path.getsize(fn) > args.maxsize:
                    continue
                if any(fnmatch.fnmatch(name, mask) or fnmatch.fnmatch(fn, mask)
                       for mask in args.exclude_mask):
                    continue
                res += check_todo(fn)
    return int(res > 0)


def check_todo(fn):
    rfn = os.path.relpath(fn, os.curdir)
    try:
        s = open(fn, 'rt').read()
    except Exception:
        print('%s: %s' % (rfn, sys.exc_info()[1]))
        # raise
        return 0
    res = 0
    for msg in todo_re.findall(s):
        print('%s: %s' % (rfn, msg))
        res += 1
    return res

if __name__ == '__main__':
    sys.exit(main(sys.argv))
