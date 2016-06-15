#!/bin/sh
cd `dirname $0`/..
py=`readlink /usr/bin/python`
rm -rf tests/__pycache__
#PY_COLORS=1 "$py"  helpers/colorlog.py -f -llogs/cygtox.html -clogs/cygtox.out -- "$py" -m tox -c cygtox.ini
PY_COLORS=1 "$py"  helpers/colorlog.py -t "cygtoxrunner log" -llogs/cygtox.html -clogs/cygtox.out -- "$py" -m tox -c cygtox.ini
#PY_COLORS=1 "$py"  helpers/colorlog.py -f -llogs/colortest.html -clogs/colortest.out -- "$py" helpers/colortest.py
