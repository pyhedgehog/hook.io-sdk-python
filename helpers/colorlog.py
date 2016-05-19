#!/usr/bin/env python
import sys
import argparse
import subprocess
import ansi2html
import six
try:
    import pexpect
except ImportError:
    pexpect = None


class TeeFile:
    def __init__(self, source, target, slow=True):
        self.source = source
        self.target = target
        self.slow = slow

    def __getattr__(self, name):
        return getattr(self.source, name)

    def read(self, bufsize=None):
        if bufsize:
            return self._read(bufsize)
        if not self.slow:
            return self._read()
        s = six.b('')
        while True:
            t = self._read(1)
            if not t and not s:
                return t
            if not t:
                return s
            s += t
        return s

    def _read(self, *args):
        s = self.source.read(*args)
        if s:
            self.target.write(s)
            self.target.flush()
        return s


def main(argv):
    p = argparse.ArgumentParser(prog=argv[0], description='pty wrapper')
    p.add_argument('--fork', '-f', default=not pexpect, action='store_true',
                   help='Skip pexpect - simply fork')
    p.add_argument('--fast-fork', '-F', dest='fastfork', action='store_true',
                   help='Read fork output at once')
    p.add_argument('--wrapper', '-w', default=None,
                   help='Wrapper program (usually winpty "console")')
    p.add_argument('--log', '-l', default='colorlog.html',
                   help='File to write HTML log (default - "colorlog.html")')
    p.add_argument('--clog', '-c', default=None,
                   help='File to write ANSI log (default - not write)')
    p.add_argument('args', nargs='*', help='What to run')
    args = p.parse_args(argv[1:])
    args.slow = True
    if args.fastfork:
        args.fork = True
        args.slow = False
    # print(repr(args))
    if args.wrapper:
        args.args.insert(0, args.wrapper)
    prog, prog_args = args.args[0], args.args[1:]
    if args.fork:
        p = subprocess.Popen([prog] + prog_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout = sys.stdout
        if hasattr(stdout, 'buffer') and hasattr(stdout.buffer, 'read'):
            stdout = stdout.buffer
        p.stdout = TeeFile(p.stdout, stdout, slow=args.slow)
        out, err = p.communicate()
        res = p.wait()
        assert out
        assert not err
    else:
        p = pexpect.spawn(prog, prog_args)
        p.logfile = logfile = six.BytesIO()
        p.interact(escape_character=None)
        p.sendeof()
        res = p.wait()
        out = logfile.getvalue()
    if args.clog:
        f = open(args.clog, 'wb')
        try:
            f.write(out)
        finally:
            f.close()
    if args.log:
        c = ansi2html.Ansi2HTMLConverter(dark_bg=False, scheme='xterm', output_encoding='utf-8')
        html = c.convert(out.decode('utf-8'))
        html = six.b(html)
        f = open(args.log, 'wb')
        try:
            f.write(html)
        finally:
            f.close()
    return res

if __name__ == '__main__':
    sys.exit(main(sys.argv))
