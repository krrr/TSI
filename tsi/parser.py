import re
from collections import deque
from . import SchemeError

# left parenthesis | right parenthesis | string like "www www" | quote | symbol
_tokenize = re.compile(r'''\(|\)|"[^"]*"|'|[^\(\)\s"]+''')


class IncompleteInputError(SchemeError):
    pass


def parse(src):
    """Parse a string that contains scheme expression and return a tuple of
    atoms (string or tuple of atoms). Examples:
        (define aa 1) => (('define', 'aa', '1'),)
        'a 'b => (('quote', 'a'), ('quote', 'b'))"""
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

    if not src:
        raise IncompleteInputError('Nothing to parse')
    src = ''.join(map(lambda l: l.partition(';')[0], src.split('\n')))
    src = '(%s)' % src  # add a virtual root
    tokens = deque(_tokenize.findall(src))

    try:
        ret = read_from_tokens()
    except IndexError:
        raise IncompleteInputError('Too few right parentheses')
    if tokens:
        raise SchemeError('Too many right parentheses')
    return ret


def parse_input():
    """This is similar to Scheme's read, except that all atoms (such as +, 23, x)
    are string."""
    s = input()
    while True:
        try:
            ret = parse(s)
            if len(ret) > 1:
                raise SchemeError('Multiple expressions on a line')
            return ret[0]
        except IncompleteInputError:
            s += ' ' + input()
