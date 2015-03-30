from sys import exit
from functools import reduce


class SProc:
    """The base class of two kinds of procedure"""


class SPrimitiveProc(SProc):
    def __init__(self, implement):
        self._imp = implement
        self.name = None

    def __str__(self):
        return '<primitive-procedure (%s)>' % self.name

    def apply(self, args):
        try:
            return self._imp(*args)
        except TypeError as e:  # wrong number of args
            # a trick: use Python's error message
            msg = str(e).split()
            assert msg[1] in ('takes', 'missing')
            msg = tuple(filter(lambda x: x != 'positional', msg))
            raise Exception('%s %s' % (self.name, ' '.join(msg[1:])))
        except Exception as e:  # add name after message
            raise Exception('%s -- %s' % (str(e), self.name))


class SCompoundProc(SProc):
    def __init__(self, parameters, body, env):
        self.parameters = parameters
        self.body = body  # body should already be analyzed
        self.env = env

    def __str__(self):
        para = ','.join(self.parameters) if self.parameters else 'none'
        return '<compound-procedure (param: %s)>' % para


def _prim_add(*args):
    if len(args) == 0: raise Exception('Too few arguments')
    return SNumber(sum(map(lambda num: num.num, args)))


def _prim_sub(*args):
    if len(args) == 0: raise Exception('Too few arguments')
    if len(args) == 1:
        return SNumber(-args[0].num)
    else:
        n = args[0].num - sum(map(lambda num: num.num, args[1:]))
        return SNumber(n)


def _prim_mul(*args):
    n = reduce(lambda x, y: x * y, map(lambda num: num.num, args))
    return SNumber(n)


def _prim_div(*args):
    raise NotImplementedError('not done yet')


def _prim_display(obj):
    print(obj, end='')
    return theNil


def _prim_newline():
    print()
    return theNil


def _prim_not(obj):
    return theFalse if is_true(obj) else theTrue


def _gen_prim_cmp(cmp):
    """Used to generate <, <=, =, >, >="""
    def template(*args):
        if len(args) < 2: raise Exception('Too few arguments')
        for x, y in zip(args, args[1:]):
            if not cmp(x, y): return theFalse
        return theTrue

    return template


def _gen_prim_is(test):
    """Used to generate is tests like symbol?"""
    return lambda x: theTrue if test(x) else theFalse


def _prim_cons(car, cdr):
    return SPair(car, cdr)


def _gen_pair_dr(op):
    """Used to generate shortcuts like cadr."""
    def template(pair):
        try:
            return op(pair)
        except AttributeError:
            raise Exception('a pair expected')

    return template


def _prim_list(*args):
    return SPair(args[0], _prim_list(*args[1:])) if args else theNil


def _prim_load(s):
    if not isinstance(s, SString): raise Exception('A string expected')
    load_file(s.string)
    return theNil


prim_proc_name_imp = (
    # arithmetic
    ('+', SPrimitiveProc(_prim_add)),
    ('-', SPrimitiveProc(_prim_sub)),
    ('*', SPrimitiveProc(_prim_mul)),
    ('/', SPrimitiveProc(_prim_div)),
    ('<', SPrimitiveProc(_gen_prim_cmp(lambda x, y: x < y))),
    ('<=', SPrimitiveProc(_gen_prim_cmp(lambda x, y: x <= y))),
    ('=', SPrimitiveProc(_gen_prim_cmp(lambda x, y: x == y))),
    ('>', SPrimitiveProc(_gen_prim_cmp(lambda x, y: x > y))),
    ('>=', SPrimitiveProc(_gen_prim_cmp(lambda x, y: x >= y))),

    ('not', SPrimitiveProc(_prim_not)),
    # pair & list
    ('cons', SPrimitiveProc(_prim_cons)),
    ('car', SPrimitiveProc(_gen_pair_dr(lambda p: p.car))),
    ('cdr', SPrimitiveProc(_gen_pair_dr(lambda p: p.cdr))),
    ('cddr', SPrimitiveProc(_gen_pair_dr(lambda p: p.cdr.cdr))),
    ('cadr', SPrimitiveProc(_gen_pair_dr(lambda p: p.cdr.car))),
    ('caddr', SPrimitiveProc(_gen_pair_dr(lambda p: p.cdr.cdr.car))),
    ('list', SPrimitiveProc(_prim_list)),
    # is
    ('null?', SPrimitiveProc(_gen_prim_is(lambda x: x is theNil))),
    ('pair?', SPrimitiveProc(_gen_prim_is(lambda x: isinstance(x, SPair)))),
    ('symbol?', SPrimitiveProc(_gen_prim_is(lambda x: isinstance(x, SSymbol)))),
    # system
    ('load', SPrimitiveProc(_prim_load)),
    ('exit', SPrimitiveProc(lambda __: exit(0))),
    # maybe below can be moved to scm library file
    ('display', SPrimitiveProc(_prim_display)),
    ('newline', SPrimitiveProc(_prim_newline)),
)

# register names
for _n, _p in prim_proc_name_imp: _p.name = _n

from . import load_file
from .expression import *
