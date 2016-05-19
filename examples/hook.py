import sys
import hookio
import logging.config


def main(argv):
    logging.basicConfig(level=logging.DEBUG)
    sdk = hookio.createClient()
    args = argv[1:]
    url = args.pop(0)
    streaming = None
    if not sys.stdin.isatty():
        streaming = sys.stdout.write
        data = sys.stdin
    else:
        data = '&'.join(args)
    r = sdk.hook.run(url, data, streaming=streaming)
    if not streaming:
        print(r.text)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
