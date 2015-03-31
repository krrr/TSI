#!/usr/bin/env python3
# A toy Scheme interpreter, it's well-structured(?) and with many documents.
# I will stop before it exceed 1000 lines of code...
import sys
import os
from traceback import print_exc
from tsi import eval, setup_environment, parse, load_file, show_err, __version__
from tsi.expression import theNil

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
    sys.path.append(os.getcwd())  # for finding extension module
    the_global_env = setup_environment()
    if len(sys.argv) > 1:
        load_file(sys.argv[1])
    else:
        driver_loop()
