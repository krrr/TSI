from collections import deque


class SExp:
    """The base class of all expressions. Analyzing is done in constructor,
    and it evaluate itself when called."""
    def __call__(self, env):
        """Evaluate this expression in given environment and return result.
        This method will become a generator in almost special forms (always use
        yield in generator, ignore Py3.3's return). Yielding a EvalRequest
        object can make eval resume us with result, solving recursion limit
        problem."""
        # be sure to return or yield in this method!
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

    def __str__(self): return str(self.num)

    def __repr__(self): return 'SNumber(%d)' % self.num


class SString(SSelfEvalExp):
    def __init__(self, exp):
        self.string = exp[1:-1]

    def __str__(self): return self.string


class STrue(SNumber):
    def __init__(self):
        super(STrue, self).__init__(1)

    def __str__(self): return '#t'


class SFalse(SNumber):
    def __init__(self):
        super(SFalse, self).__init__(0)

    def __str__(self): return '#f'


class SSymbol(SExp):
    def __init__(self, exp):
        self.name = exp

    def __call__(self, env): return env.getVarValue(self.name)

    def __str__(self): return self.name


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

    @staticmethod
    def makeList(seq):
        return SPair(seq[0], SPair.makeList(seq[1:])) if seq else theNil


def is_true(exp):
    return not is_false(exp)


def is_false(exp):
    return exp is theFalse


theTrue, theFalse, theNil = STrue(), SFalse(), SNil()


# special forms

class SExpApplication(SExp):
    callStack = deque()  # only for compound procedure

    def __init__(self, exp):
        operator, *operands = exp
        self.operator = analyze(operator)
        self.operands = tuple(map(analyze, operands))

    def __call__(self, env):
        """The apply."""
        # prevent eliminating (return proc, operands) while evaluating operands
        self.callStack.append(None)
        proc = self.operator(env)
        operands = yield EvalRequest(self.operands, env)
        self.callStack.pop()

        if isinstance(proc, SPrimitiveProc):
            yield proc.apply(operands)
        elif isinstance(proc, SCompoundProc):
            if len(proc.parameters) != len(operands):
                raise Exception('%d args expected, got %d -- APPLY (%s)'
                                % (len(proc.parameters), len(operands), str(proc)))
            # only eliminate tail recursion, not all tail-call
            if self.callStack and proc is self.callStack[-1]:
                yield proc, operands
            else:
                self.callStack.append(proc)
                while True:
                    new_env = proc.env.makeExtend(zip(proc.parameters, operands))
                    last = (yield EvalRequest(proc.body, new_env))[-1]
                    if not isinstance(last, tuple): break
                    proc, operands = last
                self.callStack.pop()
                yield last
        else:
            raise Exception('Unknown procedure type -- APPLY (%s)' % str(proc))

    @classmethod
    def printStackTrace(cls):
        print('StackTrace:')
        print('  Global Environment')
        for i in filter(None, cls.callStack):
            # when evaluating operands of a procedure, we got None in stack
            print('  %s' % str(i))
        print()


class SExpIf(SExp):
    def __init__(self, exp):
        if not 3 <= len(exp) <= 4: raise Exception('ill-form if')
        pre, con, *alter = exp[1:]
        self.predicate, self.consequent = analyze(pre), analyze(con)
        self.alternative = analyze(alter[0]) if alter else theFalse

    def __call__(self, env):
        predicate = (yield EvalRequest([self.predicate], env))[0]
        if is_true(predicate):
            yield (yield EvalRequest([self.consequent], env))[0]
        else:
            yield (yield EvalRequest([self.alternative], env))[0]


class SExpBegin(SExp):
    def __init__(self, exp):
        if len(exp) < 2: raise Exception('ill-from begin')
        self.body = tuple(map(analyze, exp[1:]))

    def __call__(self, env):
        yield (yield EvalRequest(self.body, env))[-1]


class SExpAssignment(SExp):
    def __init__(self, exp):
        if len(exp) != 3: raise Exception('ill-form assignment')
        var, value = exp[1:]
        self.variable, self.value = var, analyze(value)

    def __call__(self, env):
        env.setVarValue(self.variable, (yield EvalRequest([self.value], env))[0])
        yield theNil


class SExpDefinition(SExp):
    def __init__(self, exp):
        try:
            if isinstance(exp[1], str):
                var, value = exp[1:]
                self.variable, self.value = var, analyze(value)
            else:  # define function
                if not exp[2:]: raise Exception('ill-form define')
                lambdaExp = ('lambda', exp[1][1:]) + exp[2:]
                self.variable, self.value = exp[1][0], SExpLambda(lambdaExp)
        except (IndexError, ValueError):
            raise Exception('ill-form define')

    def __call__(self, env):
        env.defVar(self.variable, (yield EvalRequest([self.value], env))[0])
        yield theNil


class SExpLambda(SExp):
    def __init__(self, exp):
        if len(exp) < 3 or not isinstance(exp[1], tuple):
            raise Exception('ill-form lambda')
        param, *body = exp[1:]
        self.parameters, self.body = param, tuple(map(analyze, body))

    def __call__(self, env):
        return SCompoundProc(self.parameters, self.body, env)


class SExpQuote(SExp):
    def __init__(self, exp):
        listMaker = lambda data: (SPair.makeList(tuple(map(listMaker, data))) if
                                  isinstance(data, tuple) else data)

        if len(exp) != 2: raise Exception('ill-form quote')
        self.datum = listMaker(exp[1])

    def __call__(self, __):
        return self.datum


class SExpOr(SExp):
    def __init__(self, exp):
        self.seq = tuple(map(analyze, exp[1:]))

    def __call__(self, env):
        value = theFalse
        for i in self.seq:
            value = (yield EvalRequest([i], env))[0]
            if is_true(value): break
        yield value


class SExpAnd(SExp):
    def __init__(self, exp):
        self.seq = tuple(map(analyze, exp[1:]))

    def __call__(self, env):
        value = theTrue
        for i in self.seq:
            value = (yield EvalRequest([i], env))[0]
            if is_false(value): break
        yield value


# derived expressions

class SExpCond(SExp):
    def __init__(self, exp):
        try:
            clauses = exp[1:]
            self.body = analyze(self._expandClauses(clauses))
        except IndexError:
            raise Exception('ill-form cond')

    def __call__(self, env):
        yield (yield EvalRequest([self.body], env))[0]

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
            raise Exception('ill-form let')

    def __call__(self, env):
        yield (yield EvalRequest([self.app], env))[0]

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

from .core import analyze, EvalRequest
from .procedure import SCompoundProc, SPrimitiveProc
