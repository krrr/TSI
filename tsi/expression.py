import re


class SExp:
    """The base class of all expressions. Analyzing is done in constructor,
    and they evaluate themselves when being called."""
    def __call__(self, env):
        """Evaluate this expression in the given environment and return result.
        If it's necessary to evaluate other expressions, a EvalRequest will
        be returned. This can make the eval resume us with result, solving
        recursion limit problem."""
        raise NotImplementedError


class SObject:
    """Something like expression(?) but never get evaluated."""


class SSelfEvalExp(SExp):
    def __call__(self, __):
        return self


class SNumber(SSelfEvalExp):
    def __new__(cls, n):
        if n.__class__ == int:
            return SInteger(n)
        elif n.__class__ == float:
            return SReal(n)
        elif n.__class__ == str:  # n is raw expression
            return SInteger(n) if _int_exp.match(n) else SReal(n)
        else:  # n is instance of SNumber
            # happens when SInt(1) % SInt(3), the value is the first SInt
            assert isinstance(n, cls)
            return n


class SInteger(int, SNumber): pass


class SReal(float, SNumber): pass


class SString(SSelfEvalExp):
    def __init__(self, exp):
        self.string = exp[1:-1]

    def __str__(self): return self.string

    def __eq__(self, other):
        return isinstance(other, SString) and self.string == other.string


class STrue(SSelfEvalExp):
    def __str__(self): return '#t'


class SFalse(SSelfEvalExp):
    def __str__(self): return '#f'


class SSymbol(SExp):
    def __init__(self, exp):
        self.name = exp

    def __call__(self, env): return env.getVarValue(self.name)

    def __str__(self): return self.name

    def __eq__(self, other):
        return isinstance(other, SSymbol) and self.name == other.name


class SNil(SObject):
    def __str__(self): return "()"


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

    def __eq__(self, other):
        return (isinstance(other, SPair) and self.car == other.car and
                self.cdr == other.cdr)

    def toPyList(self):
        return [self.car] + (self.cdr.toPyList() if self.cdr != theNil else [])

    @staticmethod
    def makeList(seq):
        return SPair(seq[0], SPair.makeList(seq[1:])) if seq else theNil


is_true = lambda exp: exp is not theFalse
is_false = lambda exp: exp is theFalse


theTrue, theFalse, theNil = STrue(), SFalse(), SNil()


# special forms

class SExpApplication(SExp):
    def __init__(self, exp):
        operator, *operands = exp
        self.operator = analyze(operator)
        self.operands = tuple(map(analyze, operands))

    def __call__(self, env, req=None):
        """The apply."""
        if req is None and self.operands:
            return EvalRequest(self.operands, env)
        else:
            proc = self.operator(env)
            operands = req.getAll() if self.operands else []

            try:
                return proc.apply(operands)
            except AttributeError:
                raise Exception('Unknown procedure type -- APPLY (%s)' % str(proc))


class SExpCallCc(SExp):
    def __init__(self, exp):
        if len(exp) != 2: raise Exception('call/cc take exactly one argument')
        self.arg = analyze(exp[1])

    def __call__(self, env):
        try:
            return self.arg(env).apply([SContinuation()])
        except AttributeError:
            raise Exception('call/cc should take a procedure')


class SExpIf(SExp):
    def __init__(self, exp):
        if not 3 <= len(exp) <= 4: raise Exception('Malformed if')
        pre, con, *alter = exp[1:]
        self.predicate, self.consequent = analyze(pre), analyze(con)
        self.alternative = analyze(alter[0]) if alter else theFalse

    def __call__(self, env, req=None):
        if req is None:
            return EvalRequest(self.predicate, env)
        else:
            return EvalRequest(self.consequent if is_true(req.get()) else self.alternative,
                               env, as_value=True)


class SExpBegin(SExp):
    def __init__(self, exp):
        if len(exp) < 2: raise Exception('Malformed begin')
        self.body = tuple(map(analyze, exp[1:]))

    def __call__(self, env):
        return EvalRequest(self.body, env, as_value=True)


class SExpAssignment(SExp):
    def __init__(self, exp):
        if len(exp) != 3 or exp[1].__class__ != str:
            raise Exception('Malformed assignment')
        self.variable, self.value = exp[1], analyze(exp[2])

    def __call__(self, env, req=None):
        if req is None:
            return EvalRequest(self.value, env)
        else:
            env.setVarValue(self.variable, req.get())
        return theNil


class SExpDefinition(SExp):
    def __init__(self, exp):
        try:
            if isinstance(exp[1], str):
                var, value = exp[1:]
                self.variable, self.value = var, analyze(value)
            else:  # define function
                if not exp[2:]: raise Exception('Malformed define')
                lambdaExp = ('lambda', exp[1][1:]) + exp[2:]
                self.variable, self.value = exp[1][0], SExpLambda(lambdaExp)
        except (IndexError, ValueError):
            raise Exception('Malformed define')

    def __call__(self, env, req=None):
        if req is None:
            return EvalRequest(self.value, env)
        else:
            value = req.get()
            if value.__class__ == SCompoundProc and value.name is None:
                value.name = self.variable
            env.defVar(self.variable, value)
        return theNil


class SExpLambda(SExp):
    def __init__(self, exp):
        if len(exp) < 3 or not isinstance(exp[1], tuple):
            raise Exception('Malformed lambda')
        param, *body = exp[1:]
        self.parameters, self.body = param, tuple(map(analyze, body))

    def __call__(self, env):
        return SCompoundProc(self.parameters, self.body, env)


class SExpQuote(SExp):
    def __init__(self, exp):
        if len(exp) != 2: raise Exception('Malformed quote')
        self.datum = self.walker(exp[1])

    def __call__(self, __): return self.datum

    @staticmethod
    def walker(data):
        # return a list that contains list or self-eval expressions
        return (SPair.makeList(tuple(map(SExpQuote.walker, data)))
                if isinstance(data, tuple) else analyze(data))


class SExpOr(SExp):
    def __init__(self, exp):
        self.seq = tuple(map(analyze, exp[1:]))

    def __call__(self, env, req=None):
        if req is None:
            return EvalRequest(self.seq[0], env, our_idx=0) if self.seq else theFalse
        else:
            value, next_idx = req.get(), req.our_idx + 1
            if is_true(value):
                return value
            elif next_idx < len(self.seq):
                return EvalRequest(self.seq[next_idx], env, our_idx=next_idx)
            else:  # all exp are false, return the value of the last
                return value


class SExpAnd(SExp):
    def __init__(self, exp):
        self.seq = tuple(map(analyze, exp[1:]))

    def __call__(self, env, req=None):
        if req is None:
            return EvalRequest(self.seq[0], env, our_idx=0) if self.seq else theTrue
        else:
            value, next_idx = req.get(), req.our_idx + 1
            if is_false(value):
                return value
            elif next_idx < len(self.seq):
                return EvalRequest(self.seq[next_idx], env, our_idx=next_idx)
            else:  # all exp are true, return the value of the last
                return value


# derived expressions
# And and Or can be derived (using If)

class SExpCond(SExp):
    def __init__(self, exp):
        try:
            clauses = exp[1:]
            self.body = analyze(self._expandClauses(clauses))
        except IndexError:
            raise Exception('Malformed cond')

    def __call__(self, env):
        return EvalRequest(self.body, env, as_value=True)

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
        try:
            bounds, *body = exp[1:]
            self.app = analyze(self._toCombination(bounds, tuple(body)))
        except (IndexError, ValueError):
            raise Exception('Malformed let')

    def __call__(self, env):
        return EvalRequest(self.app, env, as_value=True)

    @staticmethod
    def _toCombination(bounds, body):
        lambda_exp = ('lambda', tuple(map(lambda x: x[0], bounds))) + body
        app_exp = (lambda_exp,) + tuple(map(lambda x: x[1], bounds))
        return app_exp


special_forms = {
    'call/cc': SExpCallCc,
    'call-with-current-continuation': SExpCallCc,
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

# analyzing

_int_exp = re.compile(r'^[-+]?[0-9]*$')
_str_exp = re.compile(r'^".*"$')


def analyze(exp):
    """This procedure make syntax analyzing and turn raw expression into
    Sxx object which will then called by EVAL. Every Sxx object knows how to
    check its own syntax and to evaluate itself."""
    if isinstance(exp, str) and exp:
        try:
            return SNumber(exp)
        except ValueError:
            pass
        if _str_exp.match(exp):
            return SString(exp)
        else:
            return SSymbol(exp)  # treat symbol as variable
    elif isinstance(exp, tuple) and exp:
        name = exp[0]
        if name in special_forms:
            return special_forms[name](exp)
        else:
            # exp can only be application
            return SExpApplication(exp)
    raise Exception('Unknown expression type -- ANALYZE (%s)' % str(exp))


from .core import EvalRequest
from .procedure import SCompoundProc, SPrimitiveProc, SContinuation
