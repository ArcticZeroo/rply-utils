class IllegalStateException(Exception):
    pass


class LexingException(Exception):
    pass


class IllegalArgumentException(Exception):
    pass


class ParsingException(Exception):
    def __init__(self, token_or_message):
        if isinstance(token_or_message, str):
            super().__init__(token_or_message)
        else:
            super().__init__(f'Exception during parsing due to token {token_or_message}')


class ParsingTokensExhaustedException(ParsingException):
    def __init__(self):
        super().__init__(
            f'Tokens were unexpectedly exhausted before reaching the end of the string.\n'
            f'This usually means that your production rules didn\'t match the full string.\n'
            f'It may also indicate that you exhausted the tokens iterator before parsing.'
        )
