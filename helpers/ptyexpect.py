#!/usr/bin/env python
import sys
import pexpect


def main(argv):
    args = argv[1:]
    print(repr(args))
    p = pexpect.spawn(args[0], args[1:])
    p.interact(escape_character=None)
    p.sendeof()
    return p.wait()

if __name__ == '__main__':
    sys.exit(main(sys.argv))
