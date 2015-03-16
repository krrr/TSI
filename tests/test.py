from tsi import eval, setup_environment

the_global_env = setup_environment()
ev = lambda exp: eval(exp, the_global_env)  # shortcut


ev(('define', 'aa', '1'))
assert ev('aa') == ev('1'), 'definition'
ev(('set!', 'aa', '2'))
assert ev('aa') == ev('2'), 'assignment'

assert ev(('if', 'true', '-2', '3')) == ev('-2'), 'if'

assert ev((('lambda', ('a', 'b'), 'b', 'a'), '33', '44')) == ev('33'), 'lambda'
ev(('define', ('func', 'a'), ('-', 'a', '2')))
assert ev(('func', '909')) == ev('907'), 'definition (function)'

ev(('set!', 'aa', '3'))
assert ev(('cond', (('=', 'aa', '0'), '1'),
                    (('=', 'aa', '1'), '2'),
                    ('else', '3'))) == ev('3'), 'cond'
assert ev(('cond', ('#t', '1'))) == ev('1'), 'cond (without else clause)'

assert ev(('begin', '1', '2', '3')) == ev('3'), 'begin'

ev(('define', ('func', 'n'),
    ('if', ('<', 'n', '5'),
     ('func', ('+', 'n', '1')),
     'n')))
assert ev(('func', '0')) == ev('5'), 'recursion'

ev(('define', ('fib', 'n'),
    ('cond', (('=', 'n', '0'), '0'),
     (('=', 'n', '1'), '1'),
     ('else', ('+', ('fib', ('-', 'n', '1')),
               ('fib', ('-', 'n', '2')))))))
assert ev(('fib', '5')) == ev('5'), 'fibonacci'
assert ev(('fib', '8')) == ev('21'), 'fibonacci'

assert ev(('car', ('cdr', ('cons', '3', ('cons', '1', '2'))))) == ev('1'), 'pair'

assert ev(('quote', ())) == ev('nil'), 'quote'

ev(('define', 'modified', '0'))
ev(('define', ('aa',), ('set!', 'modified', '1')))
ev(('or', '1', ('aa',)))
assert ev('modified') == ev('0'), 'or'
ev(('and', '1', ('aa',), '2'))
assert ev('modified') == ev('1'), 'and'

assert ev(('let', (('x', '10'), ('xx', '73')),
          ('+', 'x', 'xx'))) == ev('83'), 'let'

ev(('display', '"All tests passed, good job!"'))
