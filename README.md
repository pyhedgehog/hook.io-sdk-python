# hook.io-sdk-python
python implementation of [bigcompany/hook.io-sdk](https://github.com/bigcompany/hook.io-sdk)

## Status
**WIP:**
 - Writing tests:
   - [x] tests for almost all API endpoints (first target - coverage 90% for each library file)
   - [ ] tests for CLI subcommands (second target - coverage 98% for every file)
 - Stoppers: [hook.io#240](https://github.com/bigcompany/hook.io/issues/240)

Misc status: [![TravisCI](https://travis-ci.org/pyhedgehog/hook.io-sdk-python.svg)](https://travis-ci.org/pyhedgehog/hook.io-sdk-python)
[![codecov](https://codecov.io/gh/pyhedgehog/hook.io-sdk-python/branch/master/graph/badge.svg)](https://codecov.io/gh/pyhedgehog/hook.io-sdk-python)
[![Issues](https://img.shields.io/github/issues/pyhedgehog/hook.io-sdk-python.svg)](https://github/pyhedgehog/hook.io-sdk-python/issues)

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
- [ ] Account
  - [ ] signup
  - [ ] login (user/password session instead of API key)
  - [ ] list hooks (maybe should go to hook.all)
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
- [ ] Test automation
  - [ ] Misc tests
    - [x] List `hookio.keys.roles` up to date with https://hook.io/roles
    - [x] Test server-side operation
    - [ ] Import https://github.com/bigcompany/hook.io-test/tree/master/tests/client
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
    - [x] Domains
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
  - [ ] More error-waiting tests (like in hook.io-test)
  - [x] Test env matrix (tox)
  - [x] Code beauty (flake8)
  - [x] Coverage
  - [ ] Setup test CI
    - [x] travis
    - [ ] appveyor
- [ ] Additional endpoints:
  - [x] hook.resource
  - [x] hook.source
  - [ ] hook.all (`/<user>` and `/services`) blocked by
  - [x] logs.flush
  - [x] logs.write
  - [x] keys.info
  - [x] metrics.hits
- [x] Auto-test available changes in hook.io-sdk since last sync (helpers/jssdksyncmon.py)
- [ ] Auto-generate docs
- [ ] CLI improvements:
  - [ ] Hook download with creation repository `package.json` and so on
  - [ ] Hook creation from `hooks` repository `package.json`
    - [ ] Add `hookio` package bundle to top of hook source (`helpers/compilehook.py`)
    - [ ] Add package bundle to account files and some loader to top of hook source
    - [ ] Rely on availability of `hookio` package on server (sometime it will happens)
  - [ ] Hook running via `gateway-*`s (https://hook.io/gateways)
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
