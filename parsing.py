from typing import Callable, List, Any, Iterable, Dict, Optional, Union, TypeVar

from rply import ParserGenerator, Token
from rply.parser import LRParser

from exceptions import ParsingTokensExhaustedException

TState = TypeVar('TState')
EmptyProduction = None
Productions = Dict[str, Union[Callable[[List[Token], Optional[TState]], Any], EmptyProduction]]
ProductionPrecedences = Dict[str, Any]
ErrorHandler = Callable[[Token], None]
END_TOKEN_NAME = '$end'


def _reverse_args_decorator(method):
    return lambda *args: method(*args[::-1])


class Parser:
    _parser = LRParser
    _productions: Productions
    _user_error_handler: ErrorHandler

    def __init__(self, tokens: Iterable[str], productions: Productions, error_handler: ErrorHandler = None,
                 precedences: Optional[ProductionPrecedences] = None):
        if len(productions) < 1:
            raise ValueError('Productions must not be empty')

        self._parser = self._build_parser(tokens, productions, error_handler, precedences)

    @staticmethod
    def _get_precedence(rule: str, precedences: Optional[ProductionPrecedences]):
        return None if precedences is None else precedences[rule]

    def _error_handler(self, token: Token):
        if token.name == END_TOKEN_NAME:
            raise ParsingTokensExhaustedException()
        self._user_error_handler(token)

    def _build_parser(self, tokens: Iterable[str], productions: Productions, error_handler: Optional[ErrorHandler],
                      precedences: Optional[ProductionPrecedences]):
        pg = ParserGenerator(tokens)

        def noop(*_):
            pass

        for production_rule, production_handler in productions.items():
            production_decorator = pg.production(production_rule, self._get_precedence(production_rule, precedences))
            if production_handler is EmptyProduction:
                production_decorator(noop)
            else:
                # if state is passed in, for some reason the dev decided to pass it in as the first param. instead,
                # I have decided to reverse the order (aka tokens, state instead of state, tokens) such that the
                # signature of all parsing functions can be shared
                production_decorator(_reverse_args_decorator(production_handler))

        if error_handler is not None:
            pg.error(error_handler)

        return pg.build()

    def parse(self, tokens: Iterable[Token], state: Optional[TState] = None) -> Any:
        return self._parser.parse(tokens, state)
