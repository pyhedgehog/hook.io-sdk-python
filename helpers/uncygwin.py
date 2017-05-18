#!/usr/bin/env python
import os
import sys
import glob
import difflib
import py
import subprocess


def main(argv):
    path = os.environ['PATH'].split(os.pathsep)
    path0 = path[:]
    for dn in path[:]:
        if glob.glob(os.path.join(dn, 'python?.?')) or glob.glob(os.path.join(dn, 'python?.?.exe')):
            path.remove(dn)
    if argv[1:] == '-p':
        tw = py.io.TerminalWriter()
        for line in difflib.unified_diff(path0, path, 'old', 'new', lineterm=''):
            if line[:1] == '+':
                tw.line(line, green=1)
            elif line[:1] == '-':
                tw.line(line, red=1)
            elif line[:1] == '@':
                tw.line(line, purple=1)
            else:
                tw.line(line)
        return
    os.environ['PATH'] = os.pathsep.join(path)
    return subprocess.call(argv[1:])

if __name__ == '__main__':
    sys.exit(main(sys.argv))
