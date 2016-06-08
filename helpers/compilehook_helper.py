#!/usr/bin/env python
import sys
import types
import collections

sources = collections.OrderedDict()


def process_sources(sources):
    for name in sources:
        mod = sys.modules[name] = types.ModuleType(name)
        mod.__name__ = name
        if '.' in name:
            mod.__package__ = name.rsplit('.', 1)[0]
        if any(s.startswith(name + '.') for s in sources):
            mod.__package__ = name

    for name, source in sources.items():
        try:
            d = sys.modules[name].__dict__
            eval(compile(source, name, 'exec'), d, d)
        except:
            print('Exception while import-pushing ' + repr(name))
            raise
