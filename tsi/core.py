
is_int = lambda raw_exp: (raw_exp.isnumeric() or
                          (raw_exp.startswith('-') and raw_exp[1:].isnumeric()))
is_str = lambda raw_exp: len(raw_exp) >= 2 and raw_exp[0] == '"' and raw_exp[-1] == '"'

is_if = lambda raw_exp: raw_exp[0] == 'if'
is_definition = lambda raw_exp: raw_exp[0] == 'define'
is_assignment = lambda raw_exp: raw_exp[0] == 'set!'
is_begin = lambda raw_exp: raw_exp[0] == 'begin'
is_cond = lambda raw_exp: raw_exp[0] == 'cond'
is_let = lambda raw_exp: raw_exp[0] == 'let'
is_lambda = lambda raw_exp: raw_exp[0] == 'lambda'
is_quote = lambda raw_exp: raw_exp[0] == 'quote'
is_and = lambda raw_exp: raw_exp[0] == 'and'
is_or = lambda raw_exp: raw_exp[0] == 'or'


def eval(exp, env):
    # if exp is raw expression, analyze syntax first!
    if isinstance(exp, str) and exp:
        if is_int(exp):
            exp = SNumber(int(exp))
        elif is_str(exp):
            exp = SString(exp[1:-1])
        # expressions above are self-evaluating
        else:
            # exp can only be variable
            return env.getVarValue(exp)
    elif isinstance(exp, tuple) and exp:
        if is_if(exp):
            if not 3 <= len(exp) <= 4:
                raise Exception('ill-form if')
            alter = None if len(exp) != 4 else exp[3]
            exp = SExpIf(exp[1], exp[2], alter)
        elif is_lambda(exp):
            if not isinstance(exp[1], tuple): raise Exception('ill-form lambda')
            exp = SExpLambda(exp[1], exp[2:])
        elif is_cond(exp):
            exp = SExpCond(exp[1:])
        elif is_let(exp):
            exp = SExpLet(exp[1], exp[2:])
        elif is_and(exp):
            exp = SExpAnd(exp[1:])
        elif is_or(exp):
            exp = SExpOr(exp[1:])
        elif is_begin(exp):
            exp = SExpBegin(exp[1:])
        elif is_definition(exp):
            if isinstance(exp[1], str):
                if len(exp) != 3: raise Exception('ill-form define')
                var, value = exp[1], exp[2]
            else:  # function definition
                var, value = exp[1][0], SExpLambda(exp[1][1:], exp[2:])
            exp = SExpDefinition(var, value)
        elif is_assignment(exp):
            exp = SExpAssignment(exp[1], exp[2])
        elif is_quote(exp):
            if len(exp) != 2: raise Exception('ill-form quote')
            exp = SExpQuote(exp[1])
        else:
            # exp can only be application
            exp = SExpApplication(exp[0], exp[1:], env)

    try:
        return exp.eval(env)
    except AttributeError:
        raise Exception('Unknown expression type -- EVAL (%s)' % str(exp))


def apply(proc, args):
    try:
        return proc.apply(args)
    except AttributeError:
        raise Exception('Unknown procedure type -- APPLY (%s)' % str(proc))


eval_sequence = lambda seq, e: (tuple(map(lambda i: eval(i, e), seq))[-1]
                                if seq else theNil)

from .expression import *
