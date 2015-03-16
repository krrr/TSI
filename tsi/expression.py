
class SExp:
    """The base class of all expression"""
    def __call__(self, env):
        """Evaluate this expression in given environment."""
        # be sure to return in this method!
        raise NotImplementedError


class SObject:
    """Something like expression(?) but never get evaluated."""


class SSelfEvalExp(SExp):
    def __call__(self, __):
        return self


class SNumber(SSelfEvalExp):
    def __init__(self, exp):
        self.num = int(exp)

    def __eq__(self, other):
        return isinstance(other, SNumber) and self.num == other.num

    def __ne__(self, other):
        return not isinstance(other, SNumber) or self.num != other.num

    def __lt__(self, other):
        if not isinstance(other, SNumber):
            raise NotImplementedError
        return self.num < other.num

    def __str__(self):
        return str(self.num)


class SString(SSelfEvalExp):
    def __init__(self, exp):
        self.string = exp[1:-1]

    def __str__(self):
        return self.string


class STrue(SNumber):
    def __init__(self):
        super(STrue, self).__init__(1)

    def __str__(self):
        return '#t'


class SFalse(SNumber):
    def __init__(self):
        super(SFalse, self).__init__(0)

    def __str__(self):
        return '#f'


class SNil(SObject):
    def __str__(self):
        return "()"


class SPair(SObject):
    def __init__(self, car=None, cdr=None):
        self.car, self.cdr = car, cdr

    def __str__(self):
        def walker(curt):
            """If it's a list, return all of its elements."""
            if isinstance(curt.cdr, SPair):
                return [curt.car] + walker(curt.cdr)
            elif curt.cdr is theNil:
                return [curt.car]
            else:
                return [curt.car, '.', curt.cdr]  # pair or not well-formed list

        return '(%s)' % ' '.join(map(str, walker(self)))

    @staticmethod
    def makeList(seq):
        return SPair(seq[0], SPair.makeList(seq[1:])) if seq else theNil


def is_true(exp):
    return not is_false(exp)


def is_false(exp):
    return exp is theFalse


theTrue, theFalse, theNil = STrue(), SFalse(), SNil()


# special forms

class SExpVariable(SExp):
    def __init__(self, exp):
        self.name = exp

    def __call__(self, env):
        return env.getVarValue(self.name)


class SExpApplication(SExp):
    def __init__(self, exp):
        operator, *operands = exp
        self.operator = analyze(operator)
        self.operands = tuple(map(analyze, operands))

    def __call__(self, env):
        return apply(self.operator(env),
                     tuple(map(lambda i: i(env), self.operands)))


class SExpIf(SExp):
    def __init__(self, exp):
        if not 3 <= len(exp) <= 4: raise Exception('ill-form if')
        __, pre, con, *alter = exp
        self.predicate, self.consequent = analyze(pre), analyze(con)
        self.alternative = analyze(alter[0]) if alter else theFalse

    def __call__(self, env):
        if is_true(self.predicate(env)):
            return self.consequent(env)
        else:
            return self.alternative(env)


class SExpBegin(SExp):
    def __init__(self, exp):
        if len(exp) < 2: raise Exception('ill-from begin')
        self.body = analyze_seq(exp[1:])

    def __call__(self, env):
        return self.body(env)


class SExpAssignment(SExp):
    def __init__(self, exp):
        if len(exp) != 3: raise Exception('ill-form assignment')
        __, var, value = exp
        self.variable, self.value = var, analyze(value)

    def __call__(self, env):
        env.setVarValue(self.variable, self.value(env))
        return theNil


class SExpDefinition(SExp):
    def __init__(self, exp):
        try:
            if isinstance(exp[1], str):
                __, var, value = exp
                self.variable, self.value = var, analyze(value)
            else:  # define function
                if not exp[2:]: raise Exception('ill-form define')
                lambdaExp = ('lambda', exp[1][1:]) + exp[2:]
                self.variable, self.value = exp[1][0], SExpLambda(lambdaExp)
        except (IndexError, ValueError):
            raise Exception('ill-form define')

    def __call__(self, env):
        env.defVar(self.variable, self.value(env))
        return theNil


class SExpLambda(SExp):
    def __init__(self, exp):
        if len(exp) < 3 or not isinstance(exp[1], tuple):
            raise Exception('ill-form lambda')
        __, param, *body = exp
        self.parameters, self.body = param, analyze_seq(body)

    def __call__(self, env):
        return SCompoundProc(self.parameters, self.body, env)


class SExpQuote(SExp):
    def __init__(self, exp):
        listMaker = lambda data: (SPair.makeList(tuple(map(listMaker, data))) if
                                  isinstance(data, tuple) else data)

        if len(exp) != 2: raise Exception('ill-form quote')
        __, quoted = exp
        self.datum = listMaker(quoted)

    def __call__(self, __):
        return self.datum


class SExpOr(SExp):
    def __init__(self, exp):
        self.seq = tuple(map(analyze, exp[1:]))

    def __call__(self, env):
        for i in self.seq:
            value = i(env)
            if is_true(value): return value
        return theFalse


class SExpAnd(SExp):
    def __init__(self, exp):
        self.seq = tuple(map(analyze, exp[1:]))

    def __call__(self, env):
        value = theFalse
        for i in self.seq:
            value = i(env)
            if is_false(value): break
        return value


# derived expressions

class SExpCond(SExp):
    def __init__(self, exp):
        try:
            clauses = exp[1:]
            self.body = analyze(self._expandClauses(clauses))
        except IndexError:
            raise Exception('ill-form cond')

    def __call__(self, env):
        return self.body(env)

    @staticmethod
    def _expandClauses(clauses):
        """Convert COND into IF closure(?). clauses should be raw expression, and
        return value is also raw."""
        def seq_to_exp(seq):  # make single expression
            if len(seq) == 0: return '#t'
            elif len(seq) == 1: return seq[0]
            else: return ('begin',) + seq

        if not clauses: return '#f'
        first, rest = clauses[0], clauses[1:]
        first_predicate, first_acts = first[0], first[1:]

        if first_predicate == 'else':
            if rest: raise Exception('ELSE clause is not last -- COND->IF')
            return seq_to_exp(first_acts)
        else:
            return ('if', first_predicate,
                    seq_to_exp(first_acts),
                    SExpCond._expandClauses(rest))


class SExpLet(SExp):
    def __init__(self, exp):
        __, bounds, *body = exp
        self.app = analyze(self._toCombination(bounds, tuple(body)))

    def __call__(self, env):
        return self.app(env)

    @staticmethod
    def _toCombination(bounds, body):
        lambda_exp = ('lambda', tuple(map(lambda x: x[0], bounds))) + body
        app_exp = (lambda_exp,) + tuple(map(lambda x: x[1], bounds))
        return app_exp


special_forms = {
    'if': SExpIf,
    'define': SExpDefinition,
    'set!': SExpAssignment,
    'begin': SExpBegin,
    'cond': SExpCond,
    'let': SExpLet,
    'lambda': SExpLambda,
    'quote': SExpQuote,
    'and': SExpAnd,
    'or': SExpOr
}

from .core import apply, analyze, analyze_seq
from .procedure import SCompoundProc
