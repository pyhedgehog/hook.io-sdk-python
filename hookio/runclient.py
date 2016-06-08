import sys
import os
import hookio
import argparse
import functools
import logging.config
import json

debug = '-d' in getattr(sys, 'argv', [])
log = logging.getLogger(__name__)


def parse_argv(argv):
    if os.path.relpath(argv[0], os.path.dirname(hookio.__file__)) == '__main__.py':
        argv[0] = sys.executable + ' -m hookio'
        # argv[0] = __file__
    p = argparse.ArgumentParser(prog=argv[0], description='CLI for hook.io API')
    p.add_argument('--debug', '-d', default=debug, action='store_true',
                   help='Enable debug output')
    p.add_argument('--prod', dest='debug', action='store_false',
                   help='Disable debug output')
    p.add_argument('-k', dest='verify', default=None, action='store_false',
                   help='Skip https verification')
    p.add_argument('-s', dest='verify', action='store_true',
                   help='Force https verification')
    p.add_argument('--login', '-l', help='Login (instead of api-key) in form user:pass')
    p.set_defaults(obj=None, func=None, url=None, data=None, params=[])
    objects = p.add_subparsers(title='subcommands', dest='obj',
                               help='sub-command help')
    # This ugly hack instead of `set_defaults` is here for compatibility with old argparse
    object_parsers = {}
    supports_data = set()
    supports_streaming = {}
    map_names = {}
    hook = object_parsers['hook'] = objects.add_parser('hook', help='hook')
    hookcmds = hook.add_subparsers(title='subcommands', dest='func', help='sub-command help')
    hook_run = hookcmds.add_parser('run', help='run hook')
    hook_run.add_argument('url', help='Name of hook in form user/hook')
    hook_run.add_argument('params', nargs='*', help='Params for hook')
    supports_data.add(('hook', 'run'))
    supports_streaming['hook', 'run'] = None
    hook_create = hookcmds.add_parser('create', help='create hook')
    hook_create.add_argument('url', help='Name of hook without user prefix')
    hook_create.add_argument('params', nargs='*', help='Params for hook create')
    supports_data.add(('hook', 'create'))
    hook_update = hookcmds.add_parser('update', help='update hook')
    hook_update.add_argument('url', help='Name of hook in form user/hook')
    hook_update.add_argument('params', nargs='*', help='Params for hook create')
    supports_data.add(('hook', 'update'))
    hook_destroy = hookcmds.add_parser('destroy', help='destroy hook')
    hook_destroy.add_argument('url', help='Name of hook in form user/hook')
    hook_destroy.add_argument('params', nargs='*', help='Params for hook destroy')
    hook_source = hookcmds.add_parser('source', help='hook source')
    hook_source.add_argument('url', help='Name of hook in form user/hook')
    hook_resource = hookcmds.add_parser('resource', help='hook resource')
    hook_resource.add_argument('url', help='Name of hook in form user/hook')
    datastore = object_parsers['datastore'] = objects.add_parser('datastore', help='datastore')
    datastorecmds = datastore.add_subparsers(title='subcommands', dest='func',
                                             help='sub-command help')
    datastorecmds.add_parser('recent', help='recent datastore items')
    datastore_get = datastorecmds.add_parser('get', help='get datastore item')
    datastore_get.add_argument('url', metavar='key', help='Key in datastore')
    datastore_set = datastorecmds.add_parser('set', help='set datastore item (string map for now)')
    datastore_set.add_argument('url', metavar='key', help='Key in datastore')
    datastore_set.add_argument('params', nargs='*', metavar='name=val',
                               help='elements of value object')
    supports_data.add(('datastore', 'set'))
    datastore_del = datastorecmds.add_parser('del', help='del datastore item')
    datastore_del.add_argument('url', metavar='key', help='Key in datastore')
    map_names['datastore', 'del'] = 'datastore', 'delete'
    env = object_parsers['env'] = objects.add_parser('env', help='env')
    envcmds = env.add_subparsers(title='subcommands', dest='func', help='sub-command help')
    envcmds.add_parser('get', help='get env items')
    env_set = envcmds.add_parser('set', help='set env items')
    env_set.add_argument('params', nargs='*', metavar='name=val', help='Env data')
    supports_data.add(('env', 'set'))
    logs = object_parsers['logs'] = objects.add_parser('logs', help='logs')
    logscmds = logs.add_subparsers(title='subcommands', dest='func', help='sub-command help')
    logs_read = logscmds.add_parser('read', help='show log elements')
    logs_read.add_argument('-R', dest='raw', action='store_true', help='show raw reply')
    logs_read.add_argument('-r', dest='raw_data', action='store_true',
                           help='show raw data in elements')
    logs_read.add_argument('url', help='owner/name of hook')
    logs_stream = logscmds.add_parser('stream', help='stream log')
    logs_stream.add_argument('url', help='owner/name of hook')
    logs_stream.add_argument('-R', dest='raw', action='store_true',
                             help='show raw reply')
    logs_stream.add_argument('-r', dest='raw_data', action='store_true',
                             help='show raw data in elements')
    supports_streaming['logs', 'stream'] = True
    logs_flush = logscmds.add_parser('flush', help='flush log')
    logs_flush.add_argument('url', help='owner/name of hook')
    events = object_parsers['events'] = objects.add_parser('events', help='events')
    eventscmds = events.add_subparsers(title='subcommands', dest='func', help='sub-command help')
    events_get = eventscmds.add_parser('get', help='show events')
    events_get.add_argument('url', metavar='owner', help='owner of events')
    events_stream = eventscmds.add_parser('stream', help='stream log')
    events_stream.add_argument('url', metavar='owner', help='owner of events')
    supports_streaming['events', 'stream'] = True
    keys = object_parsers['keys'] = objects.add_parser('keys', help='keys')
    keyscmds = keys.add_subparsers(title='subcommands', dest='func', help='sub-command help')
    keys_checkAccess = keyscmds.add_parser('checkAccess', help='check if key has access to role')
    keys_checkAccess.add_argument('data_role', metavar='role', help='role to check')
    supports_data.add(('keys', 'checkAccess'))
    keys_create = keyscmds.add_parser('create', help='create key')
    keys_create.add_argument('url', metavar='name', help='key name')
    keys_create.add_argument('data_roles', nargs='*', metavar='roles', help='key roles')
    supports_data.add(('keys', 'create'))
    keys_destroy = keyscmds.add_parser('destroy', help='destroy key')
    keys_destroy.add_argument('url', metavar='name', help='key name')
    keyscmds.add_parser('all', help='all keys')
    files = object_parsers['files'] = objects.add_parser('files', help='files')
    filescmds = files.add_subparsers(title='subcommands', dest='func', help='sub-command help')
    files_readFile = filescmds.add_parser('readFile', help='read file')
    files_readFile.add_argument('url', metavar='path', help='path to file')
    files_writeFile = filescmds.add_parser('writeFile', help='write file')
    files_writeFile.add_argument('url', metavar='path', help='path to file')
    files_writeFile.add_argument('data', metavar='content', help='path to file')
    files_removeFile = filescmds.add_parser('removeFile', help='remove file')
    files_removeFile.add_argument('url', metavar='path', help='path to file')
    files_readdir = filescmds.add_parser('readdir', help='read directory')
    files_readdir.add_argument('url', metavar='path', help='path to file')
    files_stat = filescmds.add_parser('stat', help='stat path')
    files_stat.add_argument('url', metavar='path', help='path to file')
    metrics = object_parsers['metrics'] = objects.add_parser('metrics', help='metrics')
    metricscmds = metrics.add_subparsers(title='subcommands', dest='func', help='sub-command help')
    metrics_hits = metricscmds.add_parser('hits', help='hits of hook')
    metrics_hits.add_argument('url', help='Name of hook in form user/hook')
    domains = object_parsers['domains'] = objects.add_parser('domains', help='domains')
    domainscmds = domains.add_subparsers(title='subcommands', dest='func', help='sub-command help')
    domainscmds.add_parser('all', help='all domains')
    account = object_parsers['account'] = objects.add_parser('account', help='account')
    accountcmds = account.add_subparsers(title='subcommands', dest='func', help='sub-command help')
    account_services = accountcmds.add_parser('services', help='all hooks owned by this account')
    account_services.add_argument('url', nargs='?', metavar='owner', help='Name of user')
    args = p.parse_args(argv[1:])
    log.debug('args=%r', args)
    if not args.obj:
        p.error('too few arguments')
    if not args.func:
        object_parsers[args.obj].error('too few arguments')
    if not hasattr(args, 'raw'):
        args.raw = True
    if (args.obj, args.func) in map_names:
        args.obj, args.func = map_names[args.obj, args.func]
    if (args.obj, args.func) in supports_data:
        args.data = dict((s.split('=', 1) + [''])[:2] for s in args.params)
        for name in dir(args):
            if name.startswith('data_') and getattr(args, name):
                args.data[name[5:]] = getattr(args, name)
    args.streaming = supports_streaming.get((args.obj, args.func), False)
    if args.streaming is True or (args.streaming is None and not sys.stdin.isatty()):
        args.streaming = streaming_helper
        if args.streaming is None:
            args.stream_in = sys.stdin
    return args


def streaming_helper(s):
    sys.stdout.write(s)
    sys.stdout.flush()


def do_logs_read(sdk, args):
    r = sdk.logs.read(args.url, raw=args.raw)
    if args.raw:
        print(r.text)
        return
    for row in r:
        process_log_row(json.loads(row), args.raw_data)


def do_logs_stream(sdk, args):
    streaming = args.streaming
    if not args.raw:
        streaming = functools.partial(process_log_row, raw_data=args.raw_data)
    sdk.logs.stream(args.url, streaming=streaming, raw=args.raw)


def process_log_row(row, raw_data):
    ts = row.pop('time')
    ip = row.pop('ip')
    data = row.pop('data')
    if not raw_data:
        data = str(json.loads(data))
    assert not row
    print('[%s] %s %s' % (ts, ip, data))
    sys.stdout.flush()


def do_account_services(sdk, args):
    for hook in sdk.account.services(args.url):
        print(hook)


def debug2logging(debug):
    logging.root.setLevel([logging.DEBUG, logging.INFO][not debug])
    logging.getLogger('requests').setLevel([logging.INFO, logging.WARN][not debug])
    # logging.getLogger('requests').setLevel(logging.DEBUG)
    # print(logging.getLevelName(logging.root.level))


def main(argv=None):
    if argv is None:
        argv = sys.argv
    if not logging.root.handlers:
        if hasattr(logging, 'captureWarnings'):
            logging.captureWarnings(True)
        logging.basicConfig(level=logging.DEBUG)
    debug2logging(debug)
    args = parse_argv(argv)
    debug2logging(args.debug)
    log.debug('args=%r', args)
    sdk = hookio.createClient(dict(verify=args.verify))
    if args.login:
        res = sdk.account.login(*args.login.split(':', 1))
        assert res == {"result": "valid", "redirect": "/services"}
    fn = 'do_%s_%s' % (args.obj, args.func)
    if fn in globals():
        globals()[fn](sdk, args)
        return 0
    func = getattr(getattr(sdk, args.obj), args.func)
    targs = []
    kwargs = {}
    if args.raw is not None:
        kwargs['raw'] = args.raw
    if hasattr(args, 'raw_data'):
        kwargs['raw_data'] = args.raw
    if args.url is not None:
        targs.append(args.url)
    if args.data is not None:
        targs.append(args.data)
    if args.streaming:
        kwargs['streaming'] = args.streaming
    log.debug('targs = %r', targs)
    log.debug('kwargs = %r', kwargs)
    r = func(*tuple(targs), **kwargs)
    if not args.streaming:
        print(r.text)
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
