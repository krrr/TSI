import sys
from functools import reduce
from .core import load_file, SObject, take_snapshot, ContinuationInvoked
from .environment import get_global_env
from .parser import parse_input


class SProc(SObject):
    """The base class of all procedures."""
    def apply(self, operands):
        raise NotImplementedError


class SPrimitiveProc(SProc):
    def __init__(self, implement, name=None):
        self._imp = implement
        self.name = name

    def __str__(self):
        return '<primitive-procedure %s>' % self.name

    def apply(self, operands):
        try:
            return self._imp(*operands)
        except TypeError as e:  # wrong number of args
            # a trick: use Python's error message
            msg = str(e).split()
            if not (len(msg) > 1 and msg[1] in ('takes', 'missing')): raise
            msg = tuple(filter(lambda x: x != 'positional', msg))
            raise Exception('%s %s' % (self.name, ' '.join(msg[1:])))
        except Exception as e:  # add name after message
            raise Exception('%s -- %s' % (str(e), self.name))


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

    def apply(self, operands):
        if len(self.parameters) != len(operands):
            raise Exception('Wrong number of args -- APPLY (%s)' % str(self))
        new_env = self.env.makeExtend(zip(self.parameters, operands))
        # eliminate all tail call, including tail recursion
        return EvalRequest(self.body, new_env, as_value=True)


class SContinuation(SProc):
    """Continuation is a special procedure that has zero or one argument."""

    def __init__(self):
        self.snapshot = take_snapshot()

    def __str__(self):
        return '<continuation>'

    def apply(self, operands):
        if len(operands) > 1: raise Exception('Too many argument for continuation')
        raise ContinuationInvoked(self.snapshot, operands[0] if operands else theNil)


def _prim_add(*args):
    if len(args) == 0: raise Exception('Too few arguments')
    return SNumber(sum(args))


def _prim_sub(*args):
    if len(args) == 0: raise Exception('Too few arguments')
    if len(args) == 1:
        return SNumber(-args[0])
    else:
        return SNumber(args[0] - sum(args[1:]))


def _prim_mul(*args):
    return SNumber(reduce(lambda x, y: x * y, args))


def _prim_div(*args):
    return SNumber(reduce(lambda x, y: x / y, args))


def _prim_display(obj):
    # avoid message not showing when using print(o, end='')
    sys.stdout.write(str(obj))
    sys.stdout.flush()
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

    return SPrimitiveProc(template)


def _gen_pair_dr(op):
    """Used to generate shortcuts like cadr."""
    def template(pair):
        if pair.__class__ != SPair: raise Exception('Not a pair')
        return op(pair)

    return SPrimitiveProc(template)


def _gen_pair_set(set_func):
    def template(pair, value):
        if pair.__class__ != SPair: raise Exception('Not a pair')
        set_func(pair, value)
        return theNil

    return SPrimitiveProc(template)


def _prim_list(*args):
    return SPair(args[0], _prim_list(*args[1:])) if args else theNil


def _prim_apply(proc, args):
    try:
        args = args.toPyList()
    except AttributeError:
        raise Exception('Arguments should be a list')
    try:
        return proc.apply(args)
    except AttributeError:
        raise Exception('Unknown procedure type')


def _prim_read():
    make_symbols = lambda exp: (analyze(exp) if exp.__class__ == str
                                else SPair.makeList([make_symbols(i) for i in exp]))

    return make_symbols(parse_input())


def _prim_error(*args):
    print('User Error: ' + ' '.join(map(str, args)), file=sys.stderr)
    sys.exit(-1)


def _prim_load(s):
    if not isinstance(s, SString): raise Exception('A string expected')
    load_file(s.string)
    return theNil


def _prim_load_ext(s):
    """Load a extension module written in Python."""
    if not isinstance(s, SString): raise Exception('A string expected')
    ext = __import__(str(s))
    if not hasattr(ext, 'tsi_ext_flag'): raise Exception('Wrong extension name')
    ext.setup(get_global_env())
    return theNil


# helper function used in tests like symbol?
_s_bool = lambda x: theTrue if x else theFalse

prim_proc_name_imp = (
    # arithmetic
    ('+', SPrimitiveProc(_prim_add)),
    ('-', SPrimitiveProc(_prim_sub)),
    ('*', SPrimitiveProc(_prim_mul)),
    ('/', SPrimitiveProc(_prim_div)),
    ('<', _gen_prim_cmp(lambda x, y: x < y)),
    ('<=', _gen_prim_cmp(lambda x, y: x <= y)),
    ('=', _gen_prim_cmp(lambda x, y: x == y)),
    ('>', _gen_prim_cmp(lambda x, y: x > y)),
    ('>=', _gen_prim_cmp(lambda x, y: x >= y)),
    ('modulo', SPrimitiveProc(lambda x, y: SNumber(x % y))),

    ('eq?', SPrimitiveProc(lambda x, y: _s_bool(x == y))),
    ('not', SPrimitiveProc(_prim_not)),
    # pair & list
    ('cons', SPrimitiveProc(lambda car, cdr: SPair(car, cdr))),
    ('car', _gen_pair_dr(lambda p: p.car)),
    ('cdr', _gen_pair_dr(lambda p: p.cdr)),
    ('list', SPrimitiveProc(_prim_list)),
    ('set-car!', _gen_pair_set(lambda p, v: setattr(p, 'car', v))),
    ('set-cdr!', _gen_pair_set(lambda p, v: setattr(p, 'cdr', v))),
    # is
    ('null?', SPrimitiveProc(lambda x: _s_bool(x is theNil))),
    ('boolean?', SPrimitiveProc(lambda x: _s_bool(x in [theTrue, theFalse]))),
    ('pair?', SPrimitiveProc(lambda x: _s_bool(isinstance(x, SPair)))),
    ('symbol?', SPrimitiveProc(lambda x: _s_bool(isinstance(x, SSymbol)))),
    ('string?', SPrimitiveProc(lambda x: _s_bool(isinstance(x, SString)))),
    ('number?', SPrimitiveProc(lambda x: _s_bool(isinstance(x, SNumber)))),
    ('integer?', SPrimitiveProc(lambda x: _s_bool(isinstance(x, SInteger)))),
    ('real?', SPrimitiveProc(lambda x: _s_bool(isinstance(x, SReal)))),
    # system
    ('apply', SPrimitiveProc(_prim_apply)),
    ('read', SPrimitiveProc(_prim_read)),
    ('load', SPrimitiveProc(_prim_load)),
    ('load-ext', SPrimitiveProc(_prim_load_ext)),
    ('error', SPrimitiveProc(_prim_error)),
    ('exit', SPrimitiveProc(lambda: sys.exit(0))),
    ('display', SPrimitiveProc(_prim_display)),
    ('print', SPrimitiveProc(lambda *args: print(*args) or theNil)),
    ('newline', SPrimitiveProc(lambda: print() or theNil)),
)

# register names
for _n, _p in prim_proc_name_imp: _p.name = _n


from .expression import *
