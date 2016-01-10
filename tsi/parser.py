import re
from collections import deque
from .core import SchemeError

# left parenthesis | right parenthesis | string like "www www" | quote | symbol
_tokenize = re.compile(r'''\(|\)|"[^"]*"|'|[^\(\)\s"]+''')


class IncompleteInputError(SchemeError):
    pass


def parse(s, multi_exp=False):
    """Parse a string that contains scheme expression. Result should be atom (string)
    or tuple of atoms. Multiple expressions is allowed only if multi_exp is True,
    and it always return a tuple of atoms.
    Examples:
        (define aa 1) => ('define', 'aa', '1')
        'a 'b => (('quote', 'a'), ('quote', 'b'))  # multi_exp enabled"""
    # taken from lis.py, my old solution has been completely beaten by this...
    def read_from_tokens():
        """If tokens starts with left parenthesis, return all tokens (recursively
        apply this function) in matched parenthesis. Else, return the first token."""
        token = tokens.popleft()
        if token == '(':
            lv = deque()  # tokens from current level (depth)
            while tokens[0] != ')':
                lv.append(read_from_tokens())
            assert tokens.popleft() == ')'
            return tuple(lv)
        elif token == ')':
            raise SchemeError("Parenthesis doesn't match")
        elif token == "'":
            return ('quote', read_from_tokens())
        else:
            return token

    if not multi_exp and not s:
        raise IncompleteInputError('Nothing to parse')
    s = ''.join(map(lambda l: l.partition(';')[0], s.split('\n')))
    if multi_exp:
        s = '(%s)' % s
    tokens = deque(_tokenize.findall(s))

    try:
        ret = read_from_tokens()
    except IndexError:
        raise IncompleteInputError('Too few right parentheses')
    if tokens:
        raise SchemeError('Too many right parentheses or more than one expression')
    return ret


def parse_input():
    """This is similar to Scheme's read, except that all atoms (such as +, 23, x)
    are string."""
    s = input()
    while True:
        try:
            return parse(s)
        except IncompleteInputError:
            s += ' ' + input()
