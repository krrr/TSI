import os
import sys
from traceback import print_exc

__author__ = 'krrr'
__version__ = '0.04'


def driver_loop():
    """The read-eval-print loop."""
    from .expression import theNil
    the_global_env = get_global_env()
    IN_PROMPT = '>>'
    DEBUG = False

    print('Toy Scheme Interpreter v%s' % __version__)
    while True:
        print(IN_PROMPT, end='')
        try:
            out = eval(parse_input(), the_global_env)
            if out is not theNil: print(out)
        except KeyboardInterrupt:
            print()
        except EOFError:
            sys.exit(0)
        except Exception as e:
            if DEBUG: print_exc()
            else: print('Error: %s' % e, file=sys.stderr)


def main_entry():
    sys.path.append(os.getcwd())  # for finding extension module
    setup_environment()
    if len(sys.argv) > 1:
        load_file(sys.argv[1])
    else:
        driver_loop()


from .parser import parse, parse_input
from .core import eval, load_file
from .environment import setup_environment, get_global_env
