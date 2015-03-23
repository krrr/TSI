import sys

__author__ = 'krrr'
__version__ = '0.02'


def load_file(path):
    """Execute a script in the global environment(problematic?)."""
    with open(path, encoding='utf-8') as f:
        comment_free = ''.join(map(lambda l: l.partition(';')[0], f))
        for i in parse(comment_free, multi_exp=True):
            eval(i, get_global_env())

# shortcuts
show_err = lambda s: print(s, file=sys.stderr)

from .core import eval
from .environment import setup_environment, get_global_env
from .parser import parse
