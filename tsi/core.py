from collections import deque
from types import GeneratorType


class EvalRequest:
    """Yielding instance of this class (only in some xx.__call__) to let
    eval evaluate some expressions. After done evaluation we send result back."""
    def __init__(self, exp, env, as_value=False, **kwargs):
        self.seq = list(exp) if isinstance(exp, (list, tuple)) else [exp]
        self.env = env  # eval under this environment
        self.idx = -1  # index of last evaluated exp
        self.caller = None  # the SExp which made this request, set by eval_internal
        self.as_value = as_value  # whether last exp of seq should be the caller's value
        # control flags set by caller
        for k, v in kwargs.items(): setattr(self, k, v)

    def get(self, i=0):
        """Get evaluated expressions."""
        return self.seq[i]


def eval_internal(stack, env_stack):
    """The eval, but only EvalRequest handled here. This part is aimed only to
    break Python's recursion limit. And rest part is handled in Sxx.__call__."""
    # sys.setrecursionlimit wins if we can set stack limit of interpreter...
    ret = None

    while stack:
        e = stack.pop()  # e should be instance of SExp or EvalReq
        if e.__class__ == EvalRequest:
            if e.idx != -1:  # retrieve evaluated exp (except the first time)
                e.seq[e.idx] = ret

            if e.idx < len(e.seq) - 2 or (e.idx == len(e.seq) - 2 and not e.as_value):
                e.idx += 1
                stack.extend((e, e.seq[e.idx]))
            else:  # request finished, pass result back
                if e.idx == len(e.seq) - 2 and e.as_value:
                    # Not eval the last expression, but let it be the value of
                    # the caller. This prevent stack from growing and achieved TCO.
                    caller = e.seq[-1]
                    ret = caller(e.env)
                else:
                    caller = e.caller
                    ret = caller(e.env, e)

                if ret.__class__ == EvalRequest:
                    # if result is still EvalReq, replace current EvalReq with this
                    env_stack[-1] = ret.env
                    ret.caller = caller
                    stack.append(ret)
                else:
                    env_stack.pop()
        else:
            uo = e(env_stack[-1])
            if uo.__class__ == EvalRequest:
                uo.caller = e
                env_stack.append(uo.env)
                stack.append(uo)
            else:
                ret = uo
    assert len(env_stack) == 1, 'only global env remains eventually'
    return ret


def eval(exp, env):
    eval.stack = deque([analyze(exp)])
    eval.env_stack = deque([env])
    return eval_internal(eval.stack, eval.env_stack)


# apply still alive, it's hiding in SExpApplication

from .expression import SExpApplication, analyze
