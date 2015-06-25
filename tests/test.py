from unittest import TestCase, main
from tsi import eval, setup_environment, parse

the_global_env = setup_environment()
ev = lambda exp: eval(exp, the_global_env)  # shortcut


class TestEvaluator(TestCase):
    def test_lambda(self):
        self.assertEqual(ev((('lambda', ('a', 'b'), 'b', 'a'), '33', '44')), ev('33'))

    def test_define(self):
        ev(('define', 'aa', '1'))
        self.assertEqual(ev('aa'), ev('1'))
        ev(('define', ('func', 'a'), ('-', 'a', '2')))
        self.assertEqual(ev(('func', '909')), ev('907'))

    def test_set(self):
        ev(('define', 'aa', '1'))
        ev(('set!', 'aa', '2'))
        self.assertEqual(ev('aa'), ev('2'))

    def test_if(self):
        self.assertEqual(ev(('if', 'true', '-2', '3')), ev('-2'))

    def test_cond(self):
        ev(('define', 'aa', '3'))
        self.assertEqual(
            ev(('cond', (('=', 'aa', '0'), '1'),
               (('=', 'aa', '1'), '2'),
               ('else', '3'))),
            ev('3'))

        # without else clause
        self.assertEqual(ev(('cond', ('#t', '1'))), ev('1'))

    def test_begin(self):
        self.assertEqual(ev(('begin', '1', '2', '3')), ev('3'))

    def test_recursion(self):
        ev(('define', ('func', 'n'),
            ('if', ('<', 'n', '5'),
             ('func', ('+', 'n', '1')),
             'n')))
        self.assertEqual(ev(('func', '0')), ev('5'))

        # fibonacci
        ev(('define', ('fib', 'n'),
            ('cond', (('=', 'n', '0'), '0'),
             (('=', 'n', '1'), '1'),
             ('else', ('+', ('fib', ('-', 'n', '1')),
                       ('fib', ('-', 'n', '2')))))))
        self.assertEqual(ev(('fib', '5')), ev('5'))
        self.assertEqual(ev(('fib', '8')), ev('21'))

    def test_pair(self):
        self.assertEqual(ev(('car', ('cdr', ('cons', '3', ('cons', '1', '2'))))), ev('1'))

    def test_quote(self):
        self.assertEqual(ev(('quote', ())), ev('nil'))

    def test_and_or(self):
        ev(('define', 'modified', '0'))
        ev(('define', ('aa',), ('set!', 'modified', '1')))
        ev(('or', '1', ('aa',)))
        self.assertEqual(ev('modified'), ev('0'))
        ev(('and', '1', ('aa',), '2'))
        self.assertEqual(ev('modified'), ev('1'))

    def test_let(self):
        self.assertEqual(
            ev(('let', (('x', '10'), ('xx', '73')),
                       ('+', 'x', 'xx'))), ev('83'))


class TestParser(TestCase):
    def test(self):
        self.assertEqual(parse('(define aa 1)'), ('define', 'aa', '1'))
        self.assertEqual(parse('(lambda () (lambda () 1))'),
                         ('lambda', (), ('lambda', (), '1')))

    def test_quote(self):
        self.assertEqual(parse("'a"), ('quote', 'a'))
        self.assertEqual(parse("'()"), ('quote', ()))

    def test_errors(self):
        self.assertRaises(Exception, parse, '')
        self.assertRaises(Exception, parse, '())')
        self.assertRaises(Exception, parse, "'more-than-one-exp 'at-one-line")


if __name__ == '__main__':
    main()
