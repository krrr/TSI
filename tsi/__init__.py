import os
import sys

__author__ = 'krrr'
__version__ = '0.04'


from .evaluator import Evaluator


def main_entry():
    sys.path.append(os.getcwd())  # for finding extension module
    e = Evaluator()
    if len(sys.argv) > 1:
        e.load_file(sys.argv[1])
    else:
        e.driver_loop()
