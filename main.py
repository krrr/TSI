#!/usr/bin/env python3
# A toy Scheme interpreter, not more than 500 lines of Python code
import sys
from traceback import print_exc
from tsi import eval, setup_environment, parse, load_file, show_err
from tsi.expression import theNil
from tsi import __version__

DEBUG = False


def read():
    """This is similar to Scheme's read, except that all atom (such as +, 23, x)
    is string. It will also handle quote."""
    ss = [input()]
    while True:
        try:
            return parse(''.join(ss))
        except ValueError:
            ss += [' ', input()]


def driver_loop():
    """The read-eval-print loop."""
    IN_PROMPT = '>>'

    print('Toy Scheme Interpreter v%s' % __version__)
    while True:
        print(IN_PROMPT, end='')
        try:
            out = eval(read(), the_global_env)
            if out is not theNil: print(out)
        except KeyboardInterrupt:
            print()
        except EOFError:
            sys.exit(0)
        except Exception as e:
            if DEBUG: print_exc()
            else: show_err('Error: %s' % e)


if __name__ == '__main__':
    the_global_env = setup_environment()
    if len(sys.argv) > 1:
        load_file(sys.argv[1])
    else:
        driver_loop()
