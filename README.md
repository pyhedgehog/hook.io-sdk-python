# hook.io-sdk-python
python implementation of [bigcompany/hook.io-sdk](https://github.com/bigcompany/hook.io-sdk)

## Status
**WIP:**
 - Writing tests (first target coverage - 95%) [![codecov](https://codecov.io/gh/pyhedgehog/hook.io-sdk-python/branch/master/graph/badge.svg)](https://codecov.io/gh/pyhedgehog/hook.io-sdk-python)
 - Stopper - [bug#240](https://github.com/bigcompany/hook.io/issues/

 - [![TravisCI](https://travis-ci.org/pyhedgehog/hook.io-sdk-python.svg)](https://travis-ci.org/pyhedgehog/hook.io-sdk-python)
 - [![Issues](https://img.shields.io/github/issues/pyhedgehog/hook.io-sdk-python.svg)](https://github/pyhedgehog/hook.io-sdk-python/issues)

### Available Endpoints

- [x] Hook
  - [x] run
  - [x] create
  - [x] update
  - [x] destroy
  - [x] resource
  - [x] source
- [x] Datastore
  - [x] get
  - [x] set
  - [x] del
  - [x] recent
- [ ] Logs
  - [x] read
  - [x] stream
  - [x] flush
  - [x] write inside hook (=`sys.stderr.write`)
  - [ ] write outside hook
- [ ] Events
  - [x] get
  - [x] stream
  - [ ] write
- [x] Keys
  - [x] checkAccess
  - [x] create
  - [x] destroy
  - [x] all
- [ ] Files
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

### Checklist (from js hook.io-sdk)

- [x] Basic client creation and configuration
- [x] Minimal pipeable CLI tool
- [x] Most hook.io API Methods
- [ ] Better ENV exports configuration
- [ ] Add all hook.io API Methods
- [x] Ability to pass command line arguments
- [ ] Ability to pipe arbitrary code snippets
- [ ] Add ws:// protocol for Websockets API

### TODO

- [ ] Implement current state of js hook.io-sdk
- [ ] Test automation
  - [ ] Misc tests
    - [x] List `hookio.keys.roles` up to date with https://hook.io/roles
    - [x] Basic CLI tests - usage and help
    - [ ] Import https://github.com/bigcompany/hook.io-test/tree/master/tests/client
  - [ ] Tests for basic API
    - [x] Hook run
    - [x] Hook metadata
    - [ ] Hook modification
    - [x] Metrics
    - [x] Datastore
    - [ ] Logs
    - [x] Events
    - [ ] Keys
    - [ ] Files
    - [x] Env
    - [x] Domains
 - [ ] Tests for CLI
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
    - [ ] travis
    - [ ] appveyor
- [ ] Auto-test available changes in hook.io-sdk since last sync
- [ ] Auto-generate docs
- [ ] CLI improvements:
  - [ ] Hook creation from `hooks` repository `package.json`
  - [ ] Hook running via `gateway-*`s
- [ ] Server-side operations (use sdk inside hook):
  - [ ] All `payload` mentioned in https://github.com/bigcompany/hook.io/blob/master/bin/run-hook
  - [ ] Hook `logging` to write `hookio.logs.write` (maybe as a separate code in run-hook-python - see bigcompany/hook.io#236)
  - [ ] Implement WSGI

### Decisions

 - `def createClient` has js-like interface (gets dict as only argument - you can pass config to it).
 - `def createClient` reads environment variables for absent parameters (i.e. `$hookAccessKey`).
 - `class Client` has some sane defaults, but don't reads any config.
 - CLI argument parsing is separated from library API. I.e. `argparse` specifics should be kept in `runclient.py`.
 - `helpers/compilehook.py` can concat library with hook that uses it.

## Documentation Status

This is not a documentation yet - it's just several TODO lists.
If someone want to add important documentation parts here - help will be appreciated.
