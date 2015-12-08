import re
from collections import deque

# left parenthesis | right parenthesis | string like "www www" | quote | symbol
_tokenize = re.compile(r'''\(|\)|"[^"]*"|'|[^\(\)\s"]+''')


class IncompleteInputError(ValueError):
    pass


def parse(s, multi_exp=False):
    """Parse a string that contains scheme expression. Multiple expressions
    is allowed only if multi_exp is True. Result should be a "cell", which
    is string or tuple of cells. If multi_exp is True, result should be a
    tuple of cells.
    Examples:
        (define aa 1) => ('define', 'aa', '1')
        'a 'b => (('quote', 'a'), ('quote', 'b'))  # multi_exp enabled"""
    # taken from lis.py, my old solution has been completely beaten by this...
    def read_from_tokens():
        """If tokens starts with left parenthesis, return all tokens (recursively
        apply this function) in matched parenthesis. Else, return the first token."""
        token = tokens.popleft()
        if token == '(':
            level_lst = []  # tokens from current level (depth)
            while tokens[0] != ')':
                level_lst.append(read_from_tokens())
            assert tokens.popleft() == ')'
            return tuple(level_lst)
        elif token == ')':
            raise ValueError("Parenthesis doesn't match")
        elif token == "'":
            return ('quote', read_from_tokens())
        else:
            return token

    if not multi_exp and not s:
        raise IncompleteInputError('Nothing to parse')
    s = ''.join(map(lambda l: l.partition(';')[0], s.split('\n')))
    tokens = deque(_tokenize.findall('(%s)' % s if multi_exp else s))
    try:
        ret = read_from_tokens()
    except IndexError:
        raise IncompleteInputError('Too few right parentheses')
    if tokens:
        raise ValueError('Too many right parentheses or more than one expression')
    return ret


def parse_input():
    """This is similar to Scheme's read, except that all atom (such as +, 23, x)
    is string."""
    s = input()
    while True:
        try:
            return parse(s)
        except IncompleteInputError:
            s += ' ' + input()
