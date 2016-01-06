class SObject:
    """Anything in the Scheme world is SObject. SObject know its text
    representation either by implementing manually or using Python's."""


class SExp(SObject):
    """The base class of all expressions. Analyzing is done in constructor,
    and evaluation is done in __call__ method. SExp represents an AST."""
    def __call__(self, env, evaluator, req=None):
        """Evaluate this expression in the given environment and return result.
        If it's necessary to evaluate other expressions, an EvalRequest() will
        be returned. After eval has done, it will resume us with the result
        (by passing "exp" argument)."""
        raise NotImplementedError


class SProc(SObject):
    """The base class of all procedures."""
    def apply(self, operands, env, evaluator):
        raise NotImplementedError


class SPrimitiveProc(SProc):
    def __init__(self, implement, name=None, err_msg_name=True):
        self._imp = implement
        self.name = name
        if not err_msg_name:  # don't add procedure name after message
            self.apply = self.raw_apply

    def __str__(self):
        return '<primitive-procedure %s>' % self.name

    def apply(self, operands, env, evaluator):
        try:
            return self._imp(operands, env, evaluator)
        except SchemeError as e:
            raise SchemeError('%s -- %s' % (str(e), self.name))

    def raw_apply(self, operands, env, evaluator):
        return self._imp(operands, env, evaluator)


class SCompoundProc(SProc):
    def __init__(self, parameters, body, env):
        self.parameters = parameters
        self.body = body  # body should already be analyzed
        self.env = env
        self.name = None  # assigned once by define form

    def __str__(self):
        name = self.name + ' ' if self.name else ''
        para = '(param: %s)' % ','.join(self.parameters) if self.parameters else '(no-param)'
        return '<compound-procedure %s%s>' % (name, para)

    def apply(self, operands, *__):
        # because of static scope, env argument is ignored
        if len(self.parameters) != len(operands):
            raise SchemeError('Wrong number of args -- APPLY (%s)' % str(self))
        new_env = self.env.make_extend(zip(self.parameters, operands))
        # eliminate all tail call, including tail recursion
        return EvalRequest(self.body, new_env, as_value=True)


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
            raise SchemeError('Unbound variable (%s)' % var)
        else:
            return self.enclosing.get_var_value(var)

    def set_var_value(self, var, value):
        if var in self.vars:
            self.vars[var] = value
        elif self.enclosing is None:
            raise SchemeError('Setting unbound variable (%s)' % var)
        else:
            return self.enclosing.set_var_value(var, value)

    def def_var(self, var, value):
        """Define a variable (or set if exists) in *this* environment."""
        self.vars[var] = value


class EvalRequest:
    """Returning instance of this class (in SExp.__call__) to let the
    eval evaluate some expressions. The eval will send this instance back
    after evaluation is done. It's also called "stack frame"."""
    def __init__(self, exp, env, as_value=False, **kwargs):
        self.seq = list(exp) if isinstance(exp, (list, tuple)) else [exp]
        self.env = env  # eval under this environment
        self.idx = -1  # index of last evaluated exp
        self.caller = None  # the SExp which made this request, set by _eval_iterator
        self.as_value = as_value  # whether last exp of seq should be the caller's value
        # control flags set by caller, must be immutable
        for k, v in kwargs.items():
            setattr(self, k, v)

    def get(self, i=0):
        """Get evaluated expressions."""
        return self.seq[i]

    def get_all(self):
        return self.seq


class SchemeError(Exception):
    """Error in the language being interpreted."""
    pass


class ContinuationInvoked(Exception):
    pass
