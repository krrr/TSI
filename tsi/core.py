from collections import deque
from types import GeneratorType


class EvalRequest:
    """Yielding instance of this class (only in some xx.__call__) to let
    eval evaluate some expressions. After done evaluation we send result back."""
    def __init__(self, seq, env):
        assert isinstance(seq, (list, tuple))  # seq can be empty
        self.seq = list(seq)
        self.env = env  # eval under this environment
        self.idx = -1  # index of last evaluated exp
        self.caller = None  # who made this request


def eval_internal(exp, env):
    """The eval, but only EvalRequest handled here. This part is aimed only to
    break Python's recursion limit. And rest part is handled in Sxx.__call__."""
    # sys.setrecursionlimit wins if we can set stack limit of interpreter...
    stack, ret = deque([analyze(exp)]), None
    env_stack = deque([env])

    while stack:
        e = stack.pop()
        if e.__class__ == GeneratorType:
            for ret in e:
                if ret.__class__ == EvalRequest:
                    ret.caller = e
                    stack.extend((e, ret))
                    env_stack.append(ret.env)
                    # the next time this generator will start from 'paused' position
                    break
        elif e.__class__ == EvalRequest:
            # retrieve evaluated exp (except the first time)
            if e.idx != -1: e.seq[e.idx] = ret

            if e.idx < len(e.seq) - 1:
                e.idx += 1
                stack.extend((e, e.seq[e.idx]))
            else:  # request finished
                ret = e.caller.send(e.seq)  # send will invoke yield
                if ret.__class__ == EvalRequest:
                    # if result is still EvalReq, replace current EvalReq with this
                    env_stack[-1] = ret.env
                    ret.caller = e.caller
                    stack.append(ret)
                else:
                    env_stack.pop()
        else:
            uo = e(env_stack[-1])
            if uo.__class__ == GeneratorType:
                stack.append(uo)
            else:  # avoid looping again to yield, only for non-yield method like SNumber
                ret = uo
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

from .expression import SExpApplication, analyze
