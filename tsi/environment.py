from os import path


class SEnvironment:
    def __init__(self, enclosing=None, vars=None):
        self.enclosing = enclosing
        self.vars = vars if vars else {}

    def makeExtend(self, varValPairs):
        """Make a new environment whose enclosing is this one. This equals
        extend-environment in SICP."""
        return SEnvironment(self, dict(varValPairs))

    def extend(self, varValPairs):
        """Extend this environment."""
        self.vars.update(dict(varValPairs))

    def getVarValue(self, var):
        if var in self.vars:
            return self.vars[var]
        elif self.enclosing is None:
            raise Exception('Unbound variable (%s)' % var)
        else:
            return self.enclosing.getVarValue(var)

    def setVarValue(self, var, value):
        if var in self.vars:
            self.vars[var] = value
        elif self.enclosing is None:
            raise Exception('Setting unbound variable (%s)' % var)
        else:
            return self.enclosing.setVarValue(var, value)

    def defVar(self, var, value):
        """Define a variable (or set if exists) in *this* environment."""
        self.vars[var] = value


def setup_environment():
    """Setup a global environment"""
    global _global_env
    env = _global_env = SEnvironment()
    env.extend(prim_proc_name_imp)
    env.extend((('true', theTrue), ('false', theFalse), ('#t', theTrue),
               ('#f', theFalse), ('nil', theNil)))
    # load stdlib
    load_file(path.join(path.dirname(__file__), 'stdlib.scm'))
    return env


get_global_env = lambda: _global_env
_global_env = None

from . import load_file
from .expression import theTrue, theFalse, theNil
from .procedure import prim_proc_name_imp
