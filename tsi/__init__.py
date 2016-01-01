import os
import sys

__author__ = 'krrr'
__version__ = '0.04'


from .evaluator import Evaluator
from .core import SchemeError


def main_entry():
    sys.path.append(os.getcwd())  # for finding extension module
    e = Evaluator()
    if len(sys.argv) > 1:
        try:
            e.load_file(sys.argv[1])
        except SchemeError:
            print('Error: %s' % e, file=sys.stderr)
            sys.exit(-1)
    else:
        e.driver_loop()
