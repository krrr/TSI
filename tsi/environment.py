from os import path


class SEnvironment:
    def __init__(self, enclosing=None, vars_=None):
        self.enclosing = enclosing
        self.vars = vars_ or {}

    def __repr__(self):
        return 'SEnv(%s)' % 'global' if self.enclosing is None else ''

    def make_extend(self, var_val_pairs):
        """Make a new environment whose enclosing is this one. This equals
        extend-environment in SICP."""
        return SEnvironment(self, dict(var_val_pairs))

    def extend(self, var_val_pairs):
        """Extend this environment."""
        self.vars.update(dict(var_val_pairs))

    def get_var_value(self, var):
        if var in self.vars:
            return self.vars[var]
        elif self.enclosing is None:
            raise Exception('Unbound variable (%s)' % var)
        else:
            return self.enclosing.get_var_value(var)

    def set_var_value(self, var, value):
        if var in self.vars:
            self.vars[var] = value
        elif self.enclosing is None:
            raise Exception('Setting unbound variable (%s)' % var)
        else:
            return self.enclosing.set_var_value(var, value)

    def def_var(self, var, value):
        """Define a variable (or set if exists) in *this* environment."""
        self.vars[var] = value


def setup_environment():
    """Setup a global environment"""
    from .procedure import prim_proc_name_imp
    from .expression import theTrue, theFalse, theNil
    from .core import load_file

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
