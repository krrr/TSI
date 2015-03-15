
def parse(s, multi_exp=False):
    """Parse the string that contains scheme expression. Multiple expressions
    is allowed if multi_exp is True, and they should be separated by newline
    or spaces. Result should be a tuple of strings or tuples.
    Examples:
        (define aa 1) => ('define', 'aa', '1')
        'a 'b => (('quote', 'a'), ('quote', 'b'))  # multi_exp enabled"""
    # taken from lis.py, my old solution has been completely beaten by this...
    def read_from_tokens(tokens):
        """If tokens starts with left bracket, return all tokens (recursively
        apply this function) in matched brackets. Else, return the first token."""
        token = tokens.pop(0)
        if token == '(':
            L = []
            while tokens[0] != ')':
                L.append(read_from_tokens(tokens))
            del tokens[0]  # remove ')'
            return tuple(L)
        elif token == ')':
            raise Exception("Bracket doesn't match")
        elif token == "'":  # quote before left bracket
            return 'quote', read_from_tokens(tokens)
        else:  # atom may starts with "'"
            return ('quote', token[1:]) if token.startswith("'") else token
    tokenize = lambda s: s.replace('(', ' ( ').replace(')', ' ) ').split()

    if not multi_exp and not s:
        raise ValueError('Nothing to parse')
    tokens = tokenize('(%s)' % s if multi_exp else s)
    try:
        ret = read_from_tokens(tokens)
    except IndexError:
        raise ValueError('Too few right brackets')
    if tokens: raise Exception('Too many right brackets')
    return ret
