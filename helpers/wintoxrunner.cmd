@echo off
cd %~dp0\..
set PY_COLORS=1
rd /s /q tests\__pycache__ 2>nul
py -2 helpers/uncygwin.py py -2 helpers/colorlog.py -t "wintoxrunner log" -f -llogs/tox.html -clogs/tox.out -- py -2 -m tox
rem py -2 helpers/uncygwin.py py -2 helpers/colorlog.py -f -llogs/colortest.html -clogs/colortest.out -- py -2 helpers/colortest.py
