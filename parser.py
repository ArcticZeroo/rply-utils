from typing import Union, List, Tuple, Callable, Optional, Iterable

from rply import Token, ParserGenerator

from .exceptions import ParsingTokensExhaustedException, ParsingException, IllegalArgumentException, LexingException
from .lexer import Lexer
from .util import is_lexing_error

LeftOrRight = Union['left', 'right']
ParserPrecedence = List[Tuple[LeftOrRight, List[str]]]
ErrorHandler = Callable[[Token], None]
END_TOKEN_NAME = '$end'
PRODUCTION_NAME_SEPARATOR = ' : '


def _noop(*_, **__):
    pass


class Parser:
    _pg: ParserGenerator
    _user_error_handler: Optional[ErrorHandler] = None

    def __init__(self, lexer_or_tokens: Union[Lexer, Iterable[str]], precedence: Optional[ParserPrecedence] = None):
        self._pg = ParserGenerator(
            lexer_or_tokens.possible_tokens if isinstance(lexer_or_tokens, Lexer) else lexer_or_tokens,
            precedence or []
        )
        self._pg.error(self._handle_error)

    def _handle_error(self, token: Token):
        if isinstance(token, Token) and token.name == END_TOKEN_NAME:
            raise ParsingTokensExhaustedException()
        if self._user_error_handler:
            self._user_error_handler(token)
        # if user error handler doesn't raise, rply is going to raise a really unhelpful exception instead.
        raise ParsingException(token)

    def error(self, method):
        self._user_error_handler = method

    def production(self, rule: str):
        if PRODUCTION_NAME_SEPARATOR not in rule:
            raise IllegalArgumentException(f'Rule must contain "{rule}"')

        def wrap_method(method):
            self._pg.production(rule)(method)
            return method

        return wrap_method

    def empty_production(self, name_or_rule: str):
        if PRODUCTION_NAME_SEPARATOR not in name_or_rule:
            name_or_rule = name_or_rule.strip() + PRODUCTION_NAME_SEPARATOR
        self._pg.production(name_or_rule)(_noop)
        return _noop

    def build(self) -> 'Parser':
        """
        This method allows Parser to match the general interface of ParserGenerator and LRParser from rply
        :return: self
        """
        return self

    def parse(self, tokens: Iterable[Token]):
        try:
            return self._pg.build().parse(tokens)
        except Exception as e:
            if is_lexing_error(e):
                raise LexingException(f'Unexpected token encountered in lexer: {str(e)}') from e
            raise e
