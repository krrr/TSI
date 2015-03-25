from collections import deque
from types import GeneratorType

is_int = lambda raw_exp: (raw_exp.isnumeric() or
                          (raw_exp.startswith('-') and raw_exp[1:].isnumeric()))
is_str = lambda raw_exp: len(raw_exp) >= 2 and raw_exp[0] == '"' and raw_exp[-1] == '"'


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
            return SSymbol(exp)  # treat symbol as variable
    elif isinstance(exp, tuple) and exp:
        name = exp[0]
        if name in special_forms:
            return special_forms[name](exp)
        else:
            # exp can only be application
            return SExpApplication(exp)
    raise Exception('Unknown expression type -- ANALYZE (%s)' % str(exp))


class EvalRequest:
    """Yielding instance of this class (only in some xx.__call__) to let
    eval evaluate some expressions. After done evaluation we send it back."""
    def __init__(self, seq, env):
        assert isinstance(seq, (list, tuple))  # seq can be empty
        self.seq = list(seq)
        self.env = env
        self.idx = -1
        self.caller = None


def eval_internal(exp, env):
    """The eval, but only EvalRequest handled here. This part is aimed only to
    break Python's recursion limit. And rest part is handled in Sxx.__call__."""
    # sys.setrecursionlimit wins if we can set stack limit of interpreter...
    stack, ret = deque([analyze(exp)]), None
    env_stack = deque([env])

    while stack:
        e = stack.pop()
        if isinstance(e, GeneratorType):
            try:
                while True:
                    ret = next(e)
                    if isinstance(ret, EvalRequest):
                        ret.caller = e
                        stack.extend([e, ret])
                        env_stack.append(ret.env)
                        break
            except StopIteration:
                pass
        elif isinstance(e, EvalRequest):
            # retrieve evaluated exp (except the first time)
            if e.idx != -1: e.seq[e.idx] = ret

            if e.idx < len(e.seq) - 1:
                e.idx += 1
                stack.extend([e, e.seq[e.idx]])
            else:  # request finished
                ret = e.caller.send(e.seq)  # send will invoke yield
                if isinstance(ret, EvalRequest):
                    # if result is still EvalReq, replace current EvalReq with this
                    env_stack[-1] = ret.env
                    ret.caller = e.caller
                    stack.append(ret)
                else:
                    env_stack.pop()
        else:
            gen_or_value = e(env_stack[-1])
            if isinstance(gen_or_value, GeneratorType):
                stack.append(gen_or_value)
            else:  # avoid looping again to yield, only for non-yield method like SNumber
                ret = gen_or_value
    assert len(env_stack) == 1
    return ret


def eval(exp, env):
    try:
        return eval_internal(exp, env)
    except Exception:
        SExpApplication.printStackTrace()
        raise
    finally:
        SExpApplication.callStack.clear()


# apply still alive, it's hiding in SExpApplication

from .expression import *
