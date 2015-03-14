
class SExp:
    """The base class of all expression"""
    def eval(self, env):
        """Be sure to return in this method!"""
        raise NotImplementedError


class SObject:
    """Something like expression(?) but never get evaluated."""


class SSelfEvalExp(SExp):
    def eval(self, _):
        return self


class SNumber(SSelfEvalExp):
    def __init__(self, num=0):
        self.num = num

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
    def __init__(self, string=''):
        self.string = string

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


def _seq_to_exp(seq):
    """Make a sequence into a expression. If seq just has one exp, return it.
    If seq is empty, return it."""
    return seq and (seq[0] if len(seq) == 1 else SExpBegin(seq))


theTrue, theFalse, theNil = STrue(), SFalse(), SNil()


# special forms

class SExpApplication(SExp):
    def __init__(self, operator=None, operands=None, env=None):
        self.operator, self.operands, self.env = operator, operands, env

    def eval(self, env):
        return apply(
            eval(self.operator, env),
            tuple(map(lambda e: eval(e, env), self.operands)))

        # def analyze(self, rawExp):


class SExpIf(SExp):
    def __init__(self, predicate=None, consequent=None, alternative=None):
        self.predicate, self.consequent, self.alternative = (
            predicate, consequent, alternative)

    def eval(self, env):
        if is_true(eval(self.predicate, env)):
            return eval(self.consequent, env)
        elif self.alternative is not None:
            return eval(self.alternative, env)
        else:
            return theFalse


class SExpBegin(SExp):
    def __init__(self, seq):
        self.seq = seq

    def eval(self, env):
        return eval_sequence(self.seq, env)


class SExpAssignment(SExp):
    def __init__(self, var=None, value=None):
        self.var, self.value = var, value

    def eval(self, env):
        env.setVarValue(self.var, eval(self.value, env))
        return theNil


class SExpDefinition(SExp):
    def __init__(self, var=None, value=None):
        self.var, self.value = var, value

    def eval(self, env):
        env.defVar(self.var, eval(self.value, env))
        return theNil


class SExpLambda(SExp):
    def __init__(self, parameters=None, body=None):
        self.parameters, self.body = parameters, body

    def eval(self, env):
        return SCompoundProc(self.parameters, self.body, env)


class SExpQuote(SExp):
    def __init__(self, datum=None):
        self.datum = datum

    def eval(self, env):
        listMaker = lambda data: (SPair.makeList(tuple(map(listMaker, data))) if
                                  isinstance(data, tuple) else data)
        return listMaker(self.datum)


class SExpOr(SExp):
    def __init__(self, seq=None):
        self.seq = seq

    def eval(self, env):
        for i in self.seq:
            value = eval(i, env)
            if is_true(value): return value
        return theFalse


class SExpAnd(SExp):
    def __init__(self, seq=None):
        self.seq = seq

    def eval(self, env):
        value = theFalse
        for i in self.seq:
            value = eval(i, env)
            if is_false(value): break
        return value


# derived expressions

class SExpCond(SExp):
    def __init__(self, clauses):
        self.clauses = clauses

    def eval(self, env):
        return eval(SExpCond._expandClauses(self.clauses), env)

    @staticmethod
    def _expandClauses(clauses):
        """Convert COND into IF closure(?)"""
        predicate, actions = lambda c: c[0], lambda c: c[1:]

        if not clauses: return theFalse
        first, rest = clauses[0], clauses[1:]

        if predicate(first) == 'else':
            if rest: raise Exception('ELSE clause is not last -- COND->IF')
            return _seq_to_exp(actions(first)) or theTrue
        else:
            return SExpIf(predicate(first), _seq_to_exp(actions(first)) or theTrue,
                          SExpCond._expandClauses(rest))


class SExpLet(SExp):
    def __init__(self, bounds=None, body=None):
        self.bounds, self.body = bounds, body

    def eval(self, env):
        return eval(self._toCombination(env), env)

    def _toCombination(self, env):
        lam = SExpLambda(tuple(map(lambda x: x[0], self.bounds)), self.body)
        return SExpApplication(
            lam, tuple(map(lambda x: x[1], self.bounds)), env)


from .core import eval, apply, eval_sequence
from .procedure import SCompoundProc
