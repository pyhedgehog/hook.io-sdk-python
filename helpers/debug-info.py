import platform
import sys


info = {
    "impl": platform.python_implementation(),
    "version": platform.python_version(),
    "revision": platform.python_revision(),
    "maxunicode": sys.maxunicode,
    "maxsize": sys.maxsize
}

search_modules = ["ssl", "OpenSSL", "certifi", "requests", "six", "argparse", "pip"]
found_modules = []

for m in search_modules:
    try:
        mod = __import__(m)
    except ImportError:
        continue
    if hasattr(mod, '__version__'):
        m += '==' + str(mod.__version__)
    found_modules.append(m)

info["modules"] = ", ".join(found_modules)


print("""hook.io-sdk-python debug info:

Python %(version)s (revision: %(revision)s)
Implementation: %(impl)s

sys.maxunicode: %(maxunicode)X
sys.maxsize: %(maxsize)X

Installed modules: %(modules)s""" % info)
