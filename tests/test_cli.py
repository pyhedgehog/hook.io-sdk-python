#!/usr/bin/env python
import os
import sys
import pytest
import logging
import runpy
import hookio.runclient

log = logging.getLogger(__name__)


# def setup_function(function):
#     if not logging.root.handlers:
#         logging.basicConfig(level=logging.DEBUG)
#     log.debug('setting up %s', function)


def test_cli_empty(capsys):
    pytest.raises(SystemExit, hookio.runclient.main, ['-'])
    out, err = capsys.readouterr()
    assert not out
    assert 'usage:' in err
    assert 'too few arguments' in err


def test_cli_runpy(capsys):
    saved_argv = sys.argv[:]
    try:
        dirname = os.path.dirname(hookio.__file__)
        sys.argv[:] = [os.path.join(dirname, 'runclient.py')]
        pytest.raises(SystemExit, runpy.run_module, 'hookio.runclient', run_name='__main__')
        out, err = capsys.readouterr()
        assert not out
        assert 'usage:' in err
        assert 'too few arguments' in err
        modname = 'hookio'
        if sys.version_info[:2] <= (2, 6):
            modname = 'hookio.__main__'
        sys.argv[:] = [os.path.join(dirname, '__main__.py')]
        pytest.raises(SystemExit, runpy.run_module, modname, run_name='__main__')
        out, err = capsys.readouterr()
        assert not out
        assert 'usage:' in err
        assert 'too few arguments' in err
    finally:
        sys.argv[:] = saved_argv


def test_cli_help(capsys):
    pytest.raises(SystemExit, hookio.runclient.main, ['-', '-h'])
    out, err = capsys.readouterr()
    assert not err
    assert 'usage:' in out
    assert 'subcommands:' in out
    sub = out.split('subcommands:')[1]
    assert ' hook ' in sub
    assert ' datastore ' in sub


def test_cli_hook_empty(capsys):
    pytest.raises(SystemExit, hookio.runclient.main, ['-', 'hook'])
    out, err = capsys.readouterr()
    assert not out
    out = err.replace('\r', '\n')
    assert 'usage:' in out
    assert ' hook\n' in out or ' hook [-h]' in out
    assert 'too few arguments' in out


def test_cli_hook_help(capsys):
    pytest.raises(SystemExit, hookio.runclient.main, ['-', 'hook', '-h'])
    out, err = capsys.readouterr()
    assert not err
    assert 'usage:' in out
    assert 'subcommands:' in out
    sub = out.split('subcommands:')[1]
    assert ' run ' in sub
    assert ' create ' in sub
    assert ' destroy ' in sub


def test_cli_datastore_empty(capsys):
    pytest.raises(SystemExit, hookio.runclient.main, ['-', 'datastore'])
    out, err = capsys.readouterr()
    assert not out
    out = err.replace('\r', '\n')
    assert 'usage:' in out
    assert ' datastore\n' in out or ' datastore [-h]' in out
    assert 'too few arguments' in out


def test_cli_datastore_help(capsys):
    pytest.raises(SystemExit, hookio.runclient.main, ['-', 'datastore', '-h'])
    out, err = capsys.readouterr()
    assert not err
    assert 'usage:' in out
    assert 'subcommands:' in out
    sub = out.split('subcommands:')[1]
    assert ' recent ' in sub
    assert ' set ' in sub
    assert ' get ' in sub
    assert ' del ' in sub
