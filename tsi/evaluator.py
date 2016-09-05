import os
import sys
from copy import copy
from collections import deque, Iterable
from . import (__version__, SEnvironment, EvalRequest, ContinuationInvoked,
               SObject, SchemeError, SExp)
from .parser import parse, parse_input
from .expression import theNil, analyze, theTrue, theFalse
from .primitives import prim_proc_name_imp


class Evaluator:
    def __init__(self):
        # interactive mode settings
        self.in_prompt = '>> '

        self._stack = None
        self._global_env = SEnvironment()
        self._setup_global_env()

    def driver_loop(self):
        """The read-eval-print loop."""
        print('Toy Scheme Interpreter v%s  (EOF to exit)' % __version__)
        while True:
            print(self.in_prompt, end='')
            try:
                out = self._eval(analyze(parse_input()), self._global_env)
                if out is not theNil:
                    print(out)
            except KeyboardInterrupt:
                print()
            except EOFError:
                sys.exit(0)
            except SchemeError as e:
                print('Error: %s' % e, file=sys.stderr)

    def eval(self, s):
        if not isinstance(s, str):
            raise TypeError('str expected')
        if not s:
            raise ValueError('non-empty str expected')

        analyzed = map(analyze, parse(s))
        return self._eval(analyzed, self._global_env)

    def _eval(self, ast, env):
        # this method should not be called recursively
        self._stack = deque(list(ast)[::-1] if isinstance(ast, Iterable) else [ast])
        call_cc_value = None  # the value of (call/cc <proc>)

        while True:
            try:
                return self._eval_iterator(ret=call_cc_value)
            except ContinuationInvoked as e:
                self.restore_snapshot(e.args[0])
                call_cc_value = e.args[1]

    def _eval_iterator(self, ret=None):
        """The eval, but only EvalRequest handled here. This part is aimed only to
        break Python's recursion limit, and method used is known as "trampoline".
        The real implementation of expressions is in SExp.__call__."""
        # apply still alive, it's hiding in SExpApplication
        # sys.setrecursionlimit wins if we can set stack limit of interpreter...
        def push_new_req(req, caller):
            nonlocal env
            req.caller = caller
            env = req.env
            stack.append(req)

        stack, env = self._stack, self._global_env
        while stack:
            e = stack.pop()  # instance of SExp or EvalReq
            if e.__class__ == EvalRequest:
                if e.idx != -1:  # retrieve evaluated exp (except the first time)
                    e.seq[e.idx] = ret

                if e.idx < len(e.seq) - 2 or (e.idx == len(e.seq) - 2 and not e.as_value):
                    e.idx += 1
                    stack.extend((e, e.seq[e.idx]))  # pushing of new EvalReq may happen here
                    env = e.env
                else:  # request finished
                    if e.idx == len(e.seq) - 2 and e.as_value:
                        # Not eval the last expression, but let it be the value of
                        # the caller. This prevent stack from growing and achieved TCO.
                        caller = e.seq[-1]
                        ret = caller(e.env, self)
                    else:  # pass result back
                        caller = e.caller
                        ret = caller(e.env, self, e)

                    if ret.__class__ == EvalRequest:
                        push_new_req(ret, caller)
            else:
                obj = e(env, self)
                if obj.__class__ == EvalRequest:
                    push_new_req(obj, e)
                else:
                    ret = obj

        assert isinstance(ret, SObject)
        return ret

    def take_snapshot(self):
        # Can't 100% sure what to copy and how deep to copy, bugs may still
        # exists. Forcing control flags of EvalReq to be immutable is a bad
        # idea.
        def copy_stack(x):
            if x.__class__ == EvalRequest:
                req = copy(x)  # shallow copy
                req.seq = copy(x.seq)
                return req
            else:
                assert isinstance(x, SExp)
                return x

        return tuple(map(copy_stack, self._stack))

    def restore_snapshot(self, snapshot):
        self._stack = deque(snapshot)

    def load_file(self, path, env=None):
        """Execute a script in the environment."""
        if not path.endswith('.scm'):
            path += '.scm'
        with open(path, encoding='utf-8') as f:
            return self._eval(map(analyze, parse(f.read())),
                              env or self._global_env)

    def _setup_global_env(self):
        self._global_env.extend(prim_proc_name_imp)
        self._global_env.extend((('true', theTrue), ('false', theFalse), ('#t', theTrue),
                                 ('#f', theFalse), ('nil', theNil)))
        # load stdlib
        self.load_file(os.path.join(os.path.dirname(__file__), 'stdlib.scm'))

    def reset(self):
        self._stack = None
        self._global_env = SEnvironment()
        self._setup_global_env()
