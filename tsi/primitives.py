"""Implementation of primitive procedures."""
import sys
from functools import reduce
from . import SPrimitiveProc, EvalRequest, SchemeError
from .expression import *
from .parser import parse, parse_input


def check_len_eq(operands, num):
    if len(operands) != num:
        raise SchemeError('take exactly %d argument' % num)


def check_len_gt(operands, num):
    if len(operands) <= num:
        raise SchemeError('Too few arguments')


def extract_instance(operands, t):
    if len(operands) != 1 or not isinstance(operands[0], t):
        raise SchemeError('Expected a %s' % t.__name__[1:])
    return operands[0]


def _prim_add(operands, *__):
    check_len_gt(operands, 0)
    return SNumber(sum(operands))


def _prim_sub(operands, *__):
    check_len_gt(operands, 0)
    if len(operands) == 1:
        return SNumber(-operands[0])
    else:
        return SNumber(operands[0] - sum(operands[1:]))


def _prim_mul(operands, *__):
    check_len_gt(operands, 1)
    return SNumber(reduce(lambda x, y: x * y, operands))


def _prim_div(operands, *__):
    check_len_gt(operands, 1)
    return SNumber(reduce(lambda x, y: x / y, operands))


def _prim_min(operands, *__):
    check_len_gt(operands, 1)
    return SNumber(min(operands))


def _prim_max(operands, *__):
    check_len_gt(operands, 1)
    return SNumber(max(operands))


def _prim_modulo(operands, *__):
    check_len_eq(operands, 2)
    return SNumber(operands[0] % operands[1])


def _prim_display(operands, *__):
    check_len_eq(operands, 1)
    # avoid message not showing when using print(o, end='')
    sys.stdout.write(str(operands[0]))
    sys.stdout.flush()
    return theNil


def _prim_not(operands, *__):
    check_len_eq(operands, 1)
    return theFalse if is_true(operands[0]) else theTrue


def _gen_prim_cmp(cmp):
    """Used to generate <, <=, =, >, >="""
    def template(operands, *__):
        check_len_gt(operands, 1)
        for x, y in zip(operands, operands[1:]):
            if not cmp(x, y):
                return theFalse
        return theTrue

    return SPrimitiveProc(template)


def _prim_eq(operands, *__):
    check_len_eq(operands, 2)
    return theTrue if operands[0] == operands[1] else theFalse


def _prim_cons(operands, *__):
    check_len_eq(operands, 2)
    return SPair(*operands)


def _gen_pair_dr(part):
    """Used to generate shortcuts like cadr."""
    def template(operands, *__):
        pair = extract_instance(operands, SPair)
        return getattr(pair, part)

    return SPrimitiveProc(template)


def _gen_pair_set(part):
    def template(operands, *__):
        check_len_eq(operands, 2)
        pair, value = operands
        if pair.__class__ != SPair:
            raise SchemeError('Not a pair')
        setattr(pair, part, value)
        return theNil

    return SPrimitiveProc(template)


def _gen_isinstance(t):
    def template(operands, *__):
        check_len_eq(operands, 1)
        return theTrue if isinstance(operands[0], t) else theFalse

    return SPrimitiveProc(template)


def _prim_list(operands, *__):
    return SPair(operands[0], _prim_list(operands[1:])) if operands else theNil


def _prim_apply(operands, env, evaluator):
    check_len_eq(operands, 2)
    proc, args = operands
    if not isinstance(proc, SProc):
        raise SchemeError('Unknown procedure type')
    try:
        args = args.to_py_list()
    except AttributeError:
        raise SchemeError('Arguments should be a list')
    return proc.apply(args, env, evaluator)


def _prim_read(operands, *__):
    check_len_eq(operands, 0)
    make_symbols = lambda exp: (analyze(exp) if exp.__class__ == str
                                else SPair.make_list([make_symbols(i) for i in exp]))
    return make_symbols(parse_input())


def _prim_error(operands, *__):
    raise SchemeError(' '.join(map(str, operands)))


def _prim_load(operands, env, evaluator):
    path = extract_instance(operands, SString)
    if not path.endswith('.scm'):
        path += '.scm'
    with open(path, encoding='utf-8') as f:
        return EvalRequest(map(analyze, parse(f.read())), env, as_value=True)


def _prim_load_ext(operands, env, __):
    """Load a extension module written in Python."""
    module_name = extract_instance(operands, SString)
    ext = __import__(str(module_name))
    if not hasattr(ext, 'tsi_ext_flag'):
        raise SchemeError('Wrong extension name')
    ext.setup(env)
    return theNil


prim_proc_name_imp = (
    # arithmetic
    ('+', SPrimitiveProc(_prim_add)),
    ('-', SPrimitiveProc(_prim_sub)),
    ('*', SPrimitiveProc(_prim_mul)),
    ('/', SPrimitiveProc(_prim_div)),
    ('min', SPrimitiveProc(_prim_min)),
    ('max', SPrimitiveProc(_prim_max)),
    ('modulo', SPrimitiveProc(_prim_modulo)),
    ('<', _gen_prim_cmp(lambda x, y: x < y)),
    ('<=', _gen_prim_cmp(lambda x, y: x <= y)),
    ('=', _gen_prim_cmp(lambda x, y: x == y)),
    ('>', _gen_prim_cmp(lambda x, y: x > y)),
    ('>=', _gen_prim_cmp(lambda x, y: x >= y)),

    ('eq?', SPrimitiveProc(_prim_eq)),
    ('not', SPrimitiveProc(_prim_not)),
    # pair & list
    ('cons', SPrimitiveProc(_prim_cons)),
    ('car', _gen_pair_dr('car')),
    ('cdr', _gen_pair_dr('cdr')),
    ('list', SPrimitiveProc(_prim_list)),
    ('set-car!', _gen_pair_set('car')),
    ('set-cdr!', _gen_pair_set('cdr')),
    # isinstance
    ('null?', _gen_isinstance(SNil)),
    ('boolean?', _gen_isinstance(SBool)),
    ('pair?', _gen_isinstance(SPair)),
    ('symbol?', _gen_isinstance(SSymbol)),
    ('string?', _gen_isinstance(SString)),
    ('number?', _gen_isinstance(SNumber)),
    ('integer?', _gen_isinstance(SInteger)),
    ('real?', _gen_isinstance(SReal)),
    # system
    ('apply', SPrimitiveProc(_prim_apply)),
    ('read', SPrimitiveProc(_prim_read)),
    ('load', SPrimitiveProc(_prim_load)),
    ('load-ext', SPrimitiveProc(_prim_load_ext)),
    ('error', SPrimitiveProc(_prim_error, err_msg_name=False)),
    ('exit', SPrimitiveProc(lambda *__: sys.exit(0))),
    ('display', SPrimitiveProc(_prim_display)),
    ('print', SPrimitiveProc(lambda operands, *__: print(*operands) or theNil)),
    ('newline', SPrimitiveProc(lambda *__: print() or theNil)),
)

# register names
for _n, _p in prim_proc_name_imp:
    _p.name = _n
