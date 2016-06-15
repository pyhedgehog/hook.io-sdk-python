#!/bin/bash
function check() {
  if ! eval "$@" ; then
    echo "Command '$@' failed."
    exit 1
  fi
}
if [[ $TRAVIS_PIP_UPDATE == true ]] ; then
  pip_install_opts="$pip_install_opts -U"
fi
check pip install .
check pip install $pip_install_opts -r requirements-ci.txt
if [[ $TRAVIS_PYTHON_VERSION == pypy ]] ; then
  check pip install $pip_install_opts -r requirements-pypy2.txt
fi
if [[ $TRAVIS_PYTHON_VERSION == 2.6 ]] ; then
  check pip install $pip_install_opts -r requirements-py26.txt
fi
exit 0
