from enum import Enum
from typing import Union, Iterable, Optional, List, Tuple, Any, Callable, Set

from exceptions import IllegalStateException, ParsingTokensExhaustedException
from rply import LexerGenerator, Token, ParserGenerator
from rply.lexer import Lexer
from rply.parser import LRParser


LeftOrRight = Union['left', 'right']
ParserPrecedence = List[Tuple[LeftOrRight, List[str]]]
ErrorHandler = Callable[[Token], None]
END_TOKEN_NAME = '$end'


class _CompilerBuilderState(Enum):
    BUILDING_LEXER = 'building_lexer'
    BUILDING_PARSER = 'building_parser'
    PARSING_COMPLETE = 'parsing_complete'


class CompilerBuilder:
    _possible_tokens: Set[str] = None
    _state: _CompilerBuilderState

    # Lexing
    _lg: Optional[LexerGenerator] = None
    _tokens: Optional[Iterable[Token]] = None

    # Parsing
    _pg: Optional[ParserGenerator] = None
    _parser_result = None
    _user_error_handler = None

    def __init__(self):
        self._possible_tokens = set()
        self._state = _CompilerBuilderState.BUILDING_LEXER
        self._lg = LexerGenerator()

    def _verify_can_lex(self):
        if self._state != _CompilerBuilderState.BUILDING_LEXER:
            raise IllegalStateException('lexing state has already been passed')

    def _verify_can_parse(self):
        if self._state != _CompilerBuilderState.BUILDING_PARSER:
            if self._state == _CompilerBuilderState.BUILDING_LEXER:
                raise IllegalStateException('lex must be called before parser methods')
            raise IllegalStateException('parser state has already been passed')

    def _parser_error_handler(self, token: Token):
        if isinstance(token, Token) and token.name == END_TOKEN_NAME:
            raise ParsingTokensExhaustedException()
        self._user_error_handler(token)

    def _noop(self, *_):
        pass

    def add_ignore_pattern(self, pattern: str, flags: int = 0) -> 'CompilerBuilder':
        self._verify_can_lex()
        self._lg.ignore(pattern, flags)
        return self

    def add_pattern(self, token: Union[Enum, str], pattern: str, flags: int = 0) -> 'CompilerBuilder':
        self._verify_can_lex()
        token_name = token if not isinstance(token, Enum) else token.name
        self._possible_tokens.add(token_name)
        self._lg.add(token_name, pattern, flags)
        return self

    def add_lex(self, code: str) -> 'CompilerBuilder':
        self._verify_can_lex()
        self._tokens = self._lg.build().lex(code)
        self._lg = None
        return self

    def tokens(self) -> Iterable[Token]:
        return self._tokens

    def add_production(self, rule: str, handler) -> 'CompilerBuilder':
        self._verify_can_parse()
        self._pg.production(rule)(handler)
        self._pg = None
        return self

    def add_empty_production(self, rule: str) -> 'CompilerBuilder':
        if ' : ' not in rule:
            rule = f'{rule.strip()} : '
        return self.add_production(rule, self._noop)

    def set_error_handler(self, handler: ErrorHandler) -> 'CompilerBuilder':
        self._verify_can_parse()

        # this is the first error handler set
        if self._user_error_handler is None:
            self._pg.error_handler(self._parser_error_handler)

        self._user_error_handler = handler
        return self

    def parse(self, precedence: ParserPrecedence = None) -> Any:
        self._verify_can_parse()
        return self._pg.build().parse(self._tokens, precedence)
