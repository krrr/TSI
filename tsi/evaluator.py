import os
import sys
from collections import deque
from traceback import print_exc
from . import __version__
from .core import SEnvironment, EvalRequest, ContinuationInvoked, SObject
from .parser import parse, parse_input
from .expression import theNil, analyze, theTrue, theFalse
from .procedure import prim_proc_name_imp


class Evaluator:
    def __init__(self):
        # settings
        self.debug = False
        # interactive mode settings
        self.in_prompt = '>>'

        self.global_env = self._create_global_env()
        self._stack = None
        self._env_stack = None

    def driver_loop(self):
        """The read-eval-print loop."""
        print('Toy Scheme Interpreter v%s' % __version__)
        while True:
            print(self.in_prompt, end='')
            try:
                out = self._eval([analyze(parse_input())], self.global_env)
                if out is not theNil:
                    print(out)
            except KeyboardInterrupt:
                print()
            except EOFError:
                sys.exit(0)
            except Exception as e:
                if self.debug:
                    print_exc()
                else:
                    print('Error: %s' % e, file=sys.stderr)

    def eval(self, s, script=False):
        if not isinstance(s, str):
            raise TypeError('str excepted')
        if not s:
            raise ValueError('non-empty str excepted')
        if script:
            return self._eval(tuple(map(analyze, parse(s, multi_exp=True))), self.global_env)
        else:
            return self._eval([analyze(parse(s))], self.global_env)

    def _eval(self, analyzed_exps, env):
        self._stack = deque(reversed(analyzed_exps))
        self._env_stack = deque([env])
        call_cc_value = None  # the value of (call/cc <proc>)

        while True:
            try:
                return self._eval_iterator(ret=call_cc_value)
            except ContinuationInvoked as e:
                self.restore_snapshot(e.args[0])
                call_cc_value = e.args[1]

    def _eval_iterator(self, ret=None):
        """The eval, but only EvalRequest handled here. This part is aimed only to
        break Python's recursion limit. The real implementation of expressions is
        in SExp.__call__."""
        # apply still alive, it's hiding in SExpApplication
        # sys.setrecursionlimit wins if we can set stack limit of interpreter...
        stack, env_stack = self._stack, self._env_stack
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
                        ret = caller(e.env, self)
                    else:  # pass result back
                        caller = e.caller
                        ret = caller(e.env, self, e)

                    if ret.__class__ == EvalRequest:
                        # if result is still EvalReq, replace current EvalReq with this
                        ret.caller = caller
                        env_stack.append(ret.env)
                        stack.append(ret)
            else:
                uo = e(env_stack[-1], self)
                if uo.__class__ == EvalRequest:
                    uo.caller = e
                    env_stack.append(uo.env)
                    stack.append(uo)
                else:
                    ret = uo
        assert len(env_stack) == 1, 'only global env remains eventually'
        assert isinstance(ret, SObject)
        return ret

    def take_snapshot(self):
        # there may be potential bugs because "real" copy is not performed
        # but it works now...
        return tuple(self._stack), tuple(self._env_stack)

    def restore_snapshot(self, snapshot):
        self._stack, self._env_stack = map(deque, snapshot)

    def load_file(self, path, env=None):
        """Execute a script in the environment."""
        with open(path, encoding='utf-8') as f:
            return self._eval(tuple(map(analyze, parse(f.read(), multi_exp=True))),
                              env or self.global_env)

    def _create_global_env(self):
        env = SEnvironment()
        env.extend(prim_proc_name_imp)
        env.extend((('true', theTrue), ('false', theFalse), ('#t', theTrue),
                    ('#f', theFalse), ('nil', theNil)))
        # load stdlib
        self.load_file(os.path.join(os.path.dirname(__file__), 'stdlib.scm'), env)
        return env

    def reset(self):
        self._stack = self._env_stack = None
        self.global_env = self._create_global_env()
