
is_int = lambda raw_exp: (raw_exp.isnumeric() or
                          (raw_exp.startswith('-') and raw_exp[1:].isnumeric()))
is_str = lambda raw_exp: len(raw_exp) >= 2 and raw_exp[0] == '"' and raw_exp[-1] == '"'


def analyze_seq(seq):
    """Turn a sequence of expressions into an object that is callable (just
    like any Sxx object). This is analyze-sequence in SICP."""
    assert seq
    if len(seq) == 1:
        return analyze(seq[0])
    else:
        analyzed = tuple(map(analyze, seq))  # must done analyzing first
        sequential = lambda env: [i(env) for i in analyzed][-1]
        return sequential


def analyze(exp):
    """This procedure make syntax analyzing and turn raw expression into
    Sxx object which will then called by EVAL. Every Sxx object knows how to
    check its own syntax and to evaluate itself."""
    if isinstance(exp, str) and exp:
        if is_int(exp):
            return SNumber(exp)
        elif is_str(exp):
            return SString(exp)
        else:
            return SExpVariable(exp)
    elif isinstance(exp, tuple) and exp:
        name = exp[0]
        if name in special_forms:
            return special_forms[name](exp)
        else:
            # exp can only be application
            return SExpApplication(exp)
    raise Exception('Unknown expression type -- ANALYZE (%s)' % str(exp))


def eval(exp, env):
    """Call analyzed object (instance of Sxx class) to evaluate it."""
    return analyze(exp)(env)


def apply(proc, args):
    """Apply the procedure with arguments. This is execute-application
    in 4.1.7."""
    if not isinstance(proc, SProc):
        raise Exception('Unknown procedure type -- APPLY (%s)' % str(proc))
    return proc(args)


from .expression import *
from .procedure import SProc
