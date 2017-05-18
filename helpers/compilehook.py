#!/usr/bin/env python
import os
import sys
import glob
import hookio.runclient


def add_module(f, name, mod):
    f.write("sources[%r] = '''\\\n%s'''\n\n" %
            (name, open(mod, 'r').read().replace('\\', '\\\\').replace("'''", "'\\''")))


def get_source(module):
    fn = module.__file__
    name = module.__name__
    bname = name.rsplit('.', 1)[-1]
    if os.path.splitext(fn)[1] in ('.pyc', '.pyo'):
        if '__pycache__' in fn:
            dn, bfn = os.path.split(fn)
            assert os.path.basename(dn) == '__pycache__'
            fn = os.path.join(os.path.dirname(dn), bname + '.py')
        else:
            fn = fn[:-1]
    return fn


def push(names, name, index=0):
    if name in names:
        names.remove(name)
        if index is None:
            names.append(name)
        else:
            names.insert(index, name)


def generate(f, fn):
    f.write(open(os.path.join(__file__, os.pardir, 'compilehook_helper.py'), 'r').read())
    base = os.path.join(hookio.__file__, os.pardir)
    names = glob.glob(os.path.join(base, '*.py'))
    names = [os.path.splitext(os.path.basename(mod))[0] for mod in names]
    push(names, 'utils')
    push(names, 'client', None)
    push(names, '__init__', None)
    for name in names:
        if name == 'runclient':
            continue
        mod = os.path.join(base, name + '.py')
        if name == '__init__':
            name = hookio.__name__
        else:
            name = '%s.%s' % (hookio.__name__, name)
        add_module(f, name, mod)
    f.write('\nprocess_sources(sources)\n\n')
    f.write(open(fn, 'r').read())


def main(argv):
    if len(argv) == 2:
        fn = argv[1]
    else:
        fn = get_source(hookio.runclient)
    return generate(sys.stdout, fn)

if __name__ == '__main__':
    if '__file__' not in globals():
        __file__ = os.path.abspath(sys.argv[0])
    sys.exit(main(sys.argv))
