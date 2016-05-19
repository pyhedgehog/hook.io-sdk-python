import py
import time


def main():
    tw = py.io.TerminalWriter()
    tw.line('bold line', bold=True)
    time.sleep(.5)
    tw.line('normal line')
    time.sleep(.5)
    tw.line('green line', green=True)
    time.sleep(.5)
    tw.line('red line', red=True)
    time.sleep(.5)
    tw.line('normal line')

if __name__ == '__main__':
    main()
