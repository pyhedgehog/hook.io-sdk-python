import ast
import os
import sys
import codecs
from setuptools import setup, Command
try:
    from six import StringIO
except ImportError:
    StringIO = None

classifiers = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'License :: Public Domain',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    # 'Programming Language :: Python :: 2.5',  # ssl is broken in py2.5
    # 'Programming Language :: Python :: 2.6',  # ssl is insecure in py2.6
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Utilities'
]

packages = ['hookio']

current_dir = os.path.abspath(os.path.dirname(__file__))
with codecs.open(os.path.join(current_dir, 'README.md'), 'r', 'utf8') as readme_file:
    # with codecs.open(os.path.join(current_dir, 'CHANGES.md'), 'r', 'utf8') as changes_file:
        long_description = readme_file.read()  # + '\n' + changes_file.read()

version = None
with open(os.path.join("hookio", "__init__.py"), "rb") as init_file:
    t = ast.parse(init_file.read(), filename="__init__.py", mode="exec")
    assert isinstance(t, ast.Module)
    assignments = filter(lambda x: isinstance(x, ast.Assign), t.body)
    for a in assignments:
        if not (len(a.targets) != 1 or
                not isinstance(a.targets[0], ast.Name) or
                a.targets[0].id != "__version__" or
                not isinstance(a.value, ast.Str)):
            version = a.value.s

try:
    __file__
except:
    __file__ = os.path.abspath(sys.argv[0])


class standalone(Command):
    user_options = [('output=', 'o', 'file to write [dist/hookiocli_s.py]')]

    def initialize_options(self):
        self.output = os.path.join(os.path.dirname(__file__), 'dist', 'hookiocli_s.py')

    def finalize_options(self):
        self.output = os.path.abspath(self.output)

    def run(self):
        hookio = __import__('hookio.runclient')
        helpers = os.path.join(os.path.dirname(__file__), 'helpers')
        sys.path.insert(0, helpers)
        compilehook = __import__('compilehook')
        sys.path.remove(helpers)
        if self.dry_run:
            f = StringIO()
        else:
            if not os.path.isdir(os.path.dirname(self.output)):
                os.makedirs(os.path.dirname(self.output))
            f = open(self.output, 'wb')
        try:
            compilehook.generate(f, compilehook.get_source(hookio.runclient))
        finally:
            f.close()

setup(name='hookio',
      version=version,
      url='https://github.com/pyhedgehog/hook.io-sdk-python',
      license="UnLicense",
      description='Client/hook SDK for hook.io server',
      long_description=long_description,
      classifiers=classifiers,
      maintainer='Michael Dubner',
      maintainer_email='pyhedgehog@list.ru',
      packages=packages,
      cmdclass={'standalone': standalone},
      entry_points={
          'console_scripts': [
              'hookiocli = hookio.runclient:main',
          ],
      },
      install_requires=[
          'six',
          'requests',
      ],
      )
