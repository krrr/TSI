from sys import exit
from functools import reduce


class SPrimitiveProc:
    def __init__(self, implement):
        self._imp = implement

    def apply(self, args):
        return self._imp(args)


class SCompoundProc:
    def __init__(self, parameters, body, env):
        self.parameters = parameters
        self.body = body
        self.env = env

    def __str__(self):
        para = ','.join(self.parameters) if self.parameters else 'none'
        return '<compound-procedure (param: %s)>' % para

    def apply(self, args):
        if len(self.parameters) != len(args):
            raise Exception('Too few or too much arguments -- APPLY (%s)' % self)
        env = self.env.makeExtend(zip(self.parameters, args))
        return self.body(env)


prim_proc_name_obj_pairs = lambda: _prim_implements.items()


def _prim_add(args):
    if len(args) == 0:
        raise Exception('Too few arguments -- +')
    return SNumber(sum(map(lambda num: num.num, args)))


def _prim_sub(args):
    if len(args) == 0:
        raise Exception('Too few arguments -- -')
    elif len(args) == 1:
        return SNumber(-args[0].num)
    else:
        n = args[0].num - sum(map(lambda num: num.num, args[1:]))
        return SNumber(n)


def _prim_mul(args):
    n = reduce(lambda x, y: x * y, map(lambda num: num.num, args))
    return SNumber(n)


def _prim_div(args):
    raise NotImplementedError('not done yet')


def _prim_display(args):
    for i in args: print(i)
    return theNil


def _prim_newline(_):
    print()
    return theNil


def _prim_not(args):
    if len(args) != 1:
        raise Exception('Wrong number of arguments -- not')
    return theFalse if is_true(args[0]) else theTrue


def _gen_prim_cmp(name, cmp):
    """Used to generate primitive procedures <, <=, =, >, >="""
    def template(args):
        if len(args) < 2: raise Exception('Too few arguments -- %s', name)
        for x, y in zip(args, args[1:]):
            if not cmp(x, y): return theFalse
        return theTrue

    return template


def _gen_prim_is(name, test):
    def template(args):
        if len(args) != 1: raise Exception('1 argument expected -- %s', name)
        return theTrue if test(args[0]) else theFalse

    return template


def _prim_cons(args):
    if len(args) != 2:
        raise Exception('2 arguments expected -- cons')
    return SPair(*args)


def _gen_pair_dr(name, op):
    def template(args):
        try:
            return op(args[0])
        except (IndexError, AttributeError):
            raise Exception('a pair expected -- %s', name)

    return template


def _prim_list(args):
    return SPair(args[0], _prim_list(args[1:])) if args else theNil


def _prim_load(args):
    if len(args) != 1 or not isinstance(args[0], SString):
        raise Exception('Wrong argument. A string expected -- load')
    load_file(args[0].string)
    return theNil


_prim_implements = {
    # arithmetic
    '+': SPrimitiveProc(_prim_add),
    '-': SPrimitiveProc(_prim_sub),
    '*': SPrimitiveProc(_prim_mul),
    '/': SPrimitiveProc(_prim_div),
    '<': SPrimitiveProc(_gen_prim_cmp('<', lambda x, y: x < y)),
    '<=': SPrimitiveProc(_gen_prim_cmp('<=', lambda x, y: x <= y)),
    '=': SPrimitiveProc(_gen_prim_cmp('=', lambda x, y: x == y)),
    '>': SPrimitiveProc(_gen_prim_cmp('>', lambda x, y: x > y)),
    '>=': SPrimitiveProc(_gen_prim_cmp('>=', lambda x, y: x >= y)),

    'not': SPrimitiveProc(_prim_not),
    # pair & list
    'cons': SPrimitiveProc(_prim_cons),
    'car': SPrimitiveProc(_gen_pair_dr('car', lambda p: p.car)),
    'cdr': SPrimitiveProc(_gen_pair_dr('cdr', lambda p: p.cdr)),
    'cddr': SPrimitiveProc(_gen_pair_dr('cddr', lambda p: p.cdr.cdr)),
    'cadr': SPrimitiveProc(_gen_pair_dr('cadr', lambda p: p.cdr.car)),
    'caddr': SPrimitiveProc(_gen_pair_dr('caddr', lambda p: p.cdr.cdr.car)),
    'list': SPrimitiveProc(_prim_list),
    # is
    'null?': SPrimitiveProc(_gen_prim_is('null?', lambda x: x is theNil)),
    'pair?': SPrimitiveProc(_gen_prim_is('pair?', lambda x: isinstance(x, SPair))),
    # system
    'load': SPrimitiveProc(_prim_load),
    'exit': SPrimitiveProc(lambda __: exit(0)),
    # maybe below can be moved to scm library file
    'display': SPrimitiveProc(_prim_display),
    'newline': SPrimitiveProc(_prim_newline),
}


from . import load_file
from .expression import *
