from enum import Enum
from typing import Union, Set, Iterable

from rply import LexerGenerator, Token


class Lexer:
    _lg: LexerGenerator
    _possible_tokens: Set[str]

    def __init__(self):
        self._lg = LexerGenerator()
        self._possible_tokens = set()

    @property
    def possible_tokens(self) -> Iterable[str]:
        return self._possible_tokens.copy()

    def add(self, token_name: Union[Enum, str], pattern: str, regex_flags: int = 0) -> 'Lexer':
        if isinstance(token_name, Enum):
            token_name = token_name.name
        self._possible_tokens.add(token_name)
        self._lg.add(token_name, pattern, regex_flags)
        return self

    def ignore(self, pattern: str, regex_flags: int = 0) -> 'Lexer':
        self._lg.ignore(pattern, regex_flags)
        return self

    def lex(self, code: str) -> Iterable[Token]:
        lexer = self._lg.build()
        return lexer.lex(code)

    def build(self) -> 'Lexer':
        """
        This is so that Dr. Rupp can call "build" and it mimics the LexerGenerator interface (build, then lex on Lexer)
        :return: self
        """
        return self
