import os
import sys

__author__ = 'krrr'
__version__ = '0.04'


from .evaluator import Evaluator
from .core import SchemeError


def main_entry():
    sys.path.append(os.getcwd())  # for finding extension module
    eva = Evaluator()
    if len(sys.argv) > 1:
        try:
            eva.load_file(sys.argv[1])
        except (SchemeError, FileNotFoundError) as e:
            print('Error: %s' % e, file=sys.stderr)
            sys.exit(-1)
    else:
        eva.driver_loop()
