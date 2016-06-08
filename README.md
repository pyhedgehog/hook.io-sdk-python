# hook.io-sdk-python
python implementation of [bigcompany/hook.io-sdk](https://github.com/bigcompany/hook.io-sdk)

## Status
Misc status: [![TravisCI](https://travis-ci.org/pyhedgehog/hook.io-sdk-python.svg)](https://travis-ci.org/pyhedgehog/hook.io-sdk-python)
[![codecov](https://codecov.io/gh/pyhedgehog/hook.io-sdk-python/branch/master/graph/badge.svg)](https://codecov.io/gh/pyhedgehog/hook.io-sdk-python)
[![Issues](https://img.shields.io/github/issues/pyhedgehog/hook.io-sdk-python.svg)](https://github/pyhedgehog/hook.io-sdk-python/issues)

### Actual WIP
 - Writing tests:
   - tests for CLI subcommands (second target - coverage 98% for every file)
 - Stoppers:
   - [hook.io#240](https://github.com/bigcompany/hook.io/issues/240)
   - [hook.io#245](https://github.com/bigcompany/hook.io/issues/245)
   - [hook.io#251](https://github.com/bigcompany/hook.io/issues/251)

Misc status: [![TravisCI](https://travis-ci.org/pyhedgehog/hook.io-sdk-python.svg)](https://travis-ci.org/pyhedgehog/hook.io-sdk-python)
[![codecov](https://codecov.io/gh/pyhedgehog/hook.io-sdk-python/branch/master/graph/badge.svg)](https://codecov.io/gh/pyhedgehog/hook.io-sdk-python)
[![Issues](https://img.shields.io/github/issues/pyhedgehog/hook.io-sdk-python.svg)](https://github/pyhedgehog/hook.io-sdk-python/issues)

### Roadmap
 - 0.0.* - implement hook.io-sdk replacement + (debug) additions (like `account.login`) + CLI + tests
 - 0.1.* - implement `Hook` replacement (python-style layer) + compilehook
 - 0.2.* - python-style layer on client
 - 0.* - attempt to implement all [plans](#Current plans)
 - 0.9.* - documentation (at least auto-documentation) must be ready before 1.0

### Available Endpoints

- [x] Hook
  - [x] run
  - [x] create
  - [x] update
  - [x] destroy
  - [x] resource
  - [x] source
  - [ ] package
  - [ ] fork
  - [ ] view
  - [ ] presenter
  - [ ] refresh
  - [ ] all (`/<user>` or `/services`) blocked by [bigcompany/hook.io#251](https://github.com/bigcompany/hook.io/issues/251)
- [x] Datastore
  - [x] get
  - [x] set
  - [x] del
  - [x] recent
- [x] Logs
  - [x] read
  - [x] stream
  - [x] flush
  - [x] write inside hook (=`sys.stderr.write`)
  - [ ] ~~write outside hook~~
- [x] Events
  - [x] get
  - [x] stream
  - [ ] ~~write~~
- [x] Keys
  - [x] checkAccess
  - [x] create
  - [x] destroy
  - [x] all
- [x] Files
  - [x] readFile
  - [x] writeFile
  - [x] removeFile
  - [x] readdir
  - [x] stat
  - [ ] createReadStream
  - [ ] createWriteStream
  - [ ] download
  - [ ] upload
- [x] Env
  - [x] get
  - [x] set
- [x] Metrics
  - [x] hits
- [ ] Domains - won't be added?
  - [x] all
  - [ ] create
  - [ ] destroy
  - [ ] find
  - [ ] get
  - [ ] update
- [x] Account
  - [ ] name blocked by [#251 (comment)](https://github.com/bigcompany/hook.io/issues/251#issuecomment-224590890)
    - Can be implemented by:
      - listing keys (needs `keys::read`)
      - creating temporary hook (needs `hook::create` and `hook::destroy`)
      - creating temporary file (`readdir` shows owner) (needs `files::writeFile`, `files::readdir` and `files::removeFile`)
      - Using `Hook` variable if we are inside hook.io server
  - [ ] signup
  - [x] login (user/password session instead of API key)
  - [x] services (list hooks - maybe should go to hook.all) see https://github.com/bigcompany/hook.io/issues/251
- [ ] server
  - [ ] languages
  - [ ] package managers for language (https://hook.io/packages)
  - [ ] installed packages for PM (package manager)
  - [ ] queued packages for PM
  - [ ] failed packages for PM
  - [ ] list available themes

### Endpoints not existing in original SDK
 - hook.resource
 - hook.source
 - logs.flush
 - logs.write
 - keys.info
 - metrics.hits
 - files.createReadStream
 - files.createWriteStream
 - files.download
 - files.upload
 - accounts.login
 - accounts.services

### Points in question

- In original SDK [TO-DO section](https://github.com/bigcompany/hook.io-sdk#todo) there are "Better ENV exports configuration" entry. Maybe "support" or "import"?
- In original SDK [TO-DO section](https://github.com/bigcompany/hook.io-sdk#todo) there are "Add all hook.io API Methods" entry. Where one can get list of _all_ methods?

### Current plans

- [ ] Implement current state/plans of js hook.io-sdk:
  - [x] Basic client creation and configuration
  - [x] Minimal pipeable CLI tool
  - [x] Most hook.io API Methods
  - [x] Ability to pass command line arguments
  - [ ] Ability to pipe arbitrary code snippets
  - [ ] Add ws:// protocol for Websockets API (https://hook.io/websockets)
  - [ ] More error-waiting tests (like in hook.io-test)
- [ ] Test automation
  - [ ] Misc tests
    - [x] List `hookio.keys.roles` up to date with https://hook.io/roles
    - [x] Test server-side operation
    - [ ] Import https://github.com/bigcompany/hook.io-test/tree/master/tests/client
    - [ ] Add tests for rich unicode support
  - [x] Tests for basic API
    - [x] Client object creation
    - [x] Server-side object creation
    - [x] Hook run+metadata+creation
    - [ ] ~~Hook modification~~
    - [x] Metrics
    - [x] Datastore
    - [x] Logs
    - [x] Events
    - [x] Keys
    - [x] Files
    - [x] Env
    - [ ] Domains
  - [ ] Tests for CLI
    - [x] Basic parsing (test_cli.py)
    - [ ] Hook run
    - [ ] Hook modification
    - [ ] Metrics
    - [x] Datastore
    - [ ] Logs
    - [ ] Events
    - [ ] Keys
    - [ ] Files
    - [ ] Env
    - [ ] Domains
  - [x] Test env matrix (tox)
  - [x] Code beauty (flake8)
  - [x] Coverage
  - [ ] Setup test CI
    - [x] travis
    - [ ] appveyor
- [x] Auto-test available changes in hook.io-sdk since last sync (helpers/jssdksyncmon.py)
- [ ] Auto-generate docs
- [ ] CLI improvements:
  - [ ] Hook download with creation repository `package.json` and so on
  - [ ] Hook creation from `hooks` repository `package.json`
    - [ ] Add `hookio` package bundle to top of hook source (`helpers/compilehook.py`)
    - [ ] Add package bundle to account files and some loader to top of hook source
    - [ ] Rely on availability of `hookio` package on server (sometime it will happens)
  - [ ] Hook running via `gateway-*`s (https://hook.io/gateways)
  - [ ] Parse `logging.LogRecord` dict-style entries in `hookio logs` subcommands
  - [ ] Mass operations (i.e. mass `hookio hook destroy`)
- [ ] Server-side operations (use sdk inside hook):
  - [ ] Hook `logging` to write `hookio.logs.write` (maybe as a separate code in run-hook-python - see bigcompany/hook.io#236)
  - [ ] All `payload` mentioned in https://github.com/bigcompany/hook.io/blob/master/bin/run-hook
    - [ ] addTrailers
    - [ ] removeHeader
    - [ ] setHeader
    - [ ] setTimeout
    - [ ] sendDate
    - [ ] statusMessage
    - [ ] statusCode
    - [ ] writeContinue
    - [ ] writeHead
    - [ ] error
    - [ ] log
  - [ ] Implement WSGI
- [ ] Rethink support for async operations (depends on async support for requests)
- [ ] Second-layer over API with more python-friendly interfaces:
  - [ ] Interface to fork a thread/threads to join `sdk.logs.stream` to `logging`
    - [ ] Converter to make `logging.LogRecord` from parsed log `dict`
    - [ ] async access for `logs.stream` with ability to add joined streams (depends on async feature)
  - [ ] Wrapper interface to `sdk.files` API (`Hook.os` maybe?)
  - [ ] `__call__` interface to `sdk.hook.run`(`hookio.any.<owner>.<name>()` for anonymous calls?)
  - [ ] `sdk.environ`: Cache?

### Decisions

 - `def createClient` has js-like interface (gets dict as only argument - you can pass config to it).
 - `def createClient` reads environment variables for absent parameters (i.e. `$hookAccessKey`).
 - `class Client` has some sane defaults, but don't reads any config.
 - CLI argument parsing is separated from library API. I.e. `argparse` specifics should be kept in `runclient.py`.
 - `helpers/compilehook.py` can concat library with hook that uses it.

## Documentation Status

There are no documentation yet - it's just several lists (plans, implemented parts, decisions).
If someone want to add important documentation parts here - help will be appreciated.
Also you are free to play in project wiki.
