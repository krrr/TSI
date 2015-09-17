from collections import deque
from .parser import parse
from .environment import get_global_env


class SObject:
    """Anything in the Scheme world is SObject. SObject know its text
    representation either by implementing manually or using Python's."""


class EvalRequest:
    """Returning instance of this class (in SExp.__call__) to let the
    eval evaluate some expressions. The eval will send this instance back
    after done evaluation."""
    def __init__(self, exp, env, as_value=False, **kwargs):
        self.seq = list(exp) if isinstance(exp, (list, tuple)) else [exp]
        self.env = env  # eval under this environment
        self.idx = -1  # index of last evaluated exp
        self.caller = None  # the SExp which made this request, set by _eval_iterator
        self.as_value = as_value  # whether last exp of seq should be the caller's value
        # control flags set by caller
        for k, v in kwargs.items():
            setattr(self, k, v)

    def get(self, i=0):
        """Get evaluated expressions."""
        return self.seq[i]

    def get_all(self):
        return self.seq


class ContinuationInvoked(Exception):
    pass


def _eval_iterator(stack, env_stack, ret=None):
    """The eval, but only EvalRequest handled here. This part is aimed only to
    break Python's recursion limit. The real implementation of expressions is
    in SExp.__call__."""
    # sys.setrecursionlimit wins if we can set stack limit of interpreter...
    while stack:
        e = stack.pop()  # e should be instance of SExp or EvalReq
        if e.__class__ == EvalRequest:
            if e.idx != -1:  # retrieve evaluated exp (except the first time)
                e.seq[e.idx] = ret

            if e.idx < len(e.seq) - 2 or (e.idx == len(e.seq) - 2 and not e.as_value):
                e.idx += 1
                stack.extend((e, e.seq[e.idx]))
            else:  # request finished
                env_stack.pop()  # Continuation.Invoke may happen, so pop first
                if e.idx == len(e.seq) - 2 and e.as_value:
                    # Not eval the last expression, but let it be the value of
                    # the caller. This prevent stack from growing and achieved TCO.
                    caller = e.seq[-1]
                    ret = caller(e.env)
                else:  # pass result back
                    caller = e.caller
                    ret = caller(e.env, e)

                if ret.__class__ == EvalRequest:
                    # if result is still EvalReq, replace current EvalReq with this
                    ret.caller = caller
                    env_stack.append(ret.env)
                    stack.append(ret)
        else:
            uo = e(env_stack[-1])
            if uo.__class__ == EvalRequest:
                uo.caller = e
                env_stack.append(uo.env)
                stack.append(uo)
            else:
                ret = uo
    assert len(env_stack) == 1, 'only global env remains eventually'
    assert isinstance(ret, SObject)
    return ret


def eval(exp, env):
    eval.stack = deque([analyze(exp)])
    eval.env_stack = deque([env])
    call_cc_value = None  # the value of (call/cc proc)

    # recover the stack from snapshot on continuation invoked
    while True:
        try:
            return _eval_iterator(eval.stack, eval.env_stack, ret=call_cc_value)
        except ContinuationInvoked as e:
            restore_snapshot(e.args[0])
            call_cc_value = e.args[1]


# apply still alive, it's hiding in SExpApplication


def take_snapshot():
    # there may be potential bugs because "real" copy is not performed
    # but it works now...
    return tuple(eval.stack), tuple(eval.env_stack)


def restore_snapshot(ss):
    eval.stack, eval.env_stack = tuple(map(deque, ss))


def load_file(path):
    """Execute a script in the global environment(problematic?)."""
    env = get_global_env()
    with open(path, encoding='utf-8') as f:
        comment_free = ''.join(map(lambda l: l.partition(';')[0], f))
        for i in parse(comment_free, multi_exp=True):
            eval(i, env)


from .expression import analyze
