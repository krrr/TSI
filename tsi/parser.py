import re

# first two match parentheses, the third match string like "www www", the last
# match the rest (symbol)
_tokenize = re.compile(r'\(|\)|"[^"]*"|[^\(\)\s"]+')


def parse(s, multi_exp=False):
    """Parse a string that contains scheme expression. Multiple expressions
    is allowed only if multi_exp is True. Result should be a "cell", which
    is string or tuple of cells. If multi_exp is True, result should be a
    tuple of cells.
    Examples:
        (define aa 1) => ('define', 'aa', '1')
        'a 'b => (('quote', 'a'), ('quote', 'b'))  # multi_exp enabled"""
    # taken from lis.py, my old solution has been completely beaten by this...
    def read_from_tokens(tokens):
        """If tokens starts with left parenthesis, return all tokens (recursively
        apply this function) in matched parenthesis. Else, return the first token."""
        token = tokens.pop(0)
        if token == '(':
            L = []
            while tokens[0] != ')':
                L.append(read_from_tokens(tokens))
            del tokens[0]  # remove ')'
            return tuple(L)
        elif token == ')':
            raise Exception("Parenthesis doesn't match")
        elif token == "'":  # quote before left parenthesis
            return 'quote', read_from_tokens(tokens)
        else:  # atom may starts with "'"
            return ('quote', token[1:]) if token.startswith("'") else token

    if not multi_exp and not s:
        raise ValueError('Nothing to parse')
    tokens = _tokenize.findall('(%s)' % s if multi_exp else s)
    try:
        ret = read_from_tokens(tokens)
    except IndexError:
        raise ValueError('Too few right parentheses')
    if tokens:
        raise Exception('Too many right parentheses or more than one expression')
    return ret


def parse_input():
    """This is similar to Scheme's read, except that all atom (such as +, 23, x)
    is string."""
    s = [input()]
    while True:
        try:
            return parse(''.join(s))
        except ValueError:
            s += [' ', input()]
