from enum import Enum
from typing import Union, Set, Iterable

from rply import LexerGenerator, Token


class Lexer:
    _lg: LexerGenerator
    _possible_tokens: Set[str]

    def __init__(self):
        self._lg = LexerGenerator()
        self._possible_tokens = set()

    @staticmethod
    def _enum_name_or_str(enum_or_str: Union[Enum, str]) -> str:
        return enum_or_str.name if isinstance(enum_or_str, Enum) else enum_or_str

    @property
    def possible_tokens(self) -> Iterable[str]:
        return self._possible_tokens.copy()

    def add(self, token_name: Union[Enum, str], pattern: str, regex_flags: int = 0) -> 'Lexer':
        token_name = self._enum_name_or_str(token_name)
        self._possible_tokens.add(token_name)
        self._lg.add(token_name, pattern, regex_flags)
        return self

    def add_identity(self, token_name: Union[Enum, str]):
        token_name = self._enum_name_or_str(token_name)
        return self.add(token_name, token_name)

    def ignore(self, pattern: str, regex_flags: int = 0) -> 'Lexer':
        self._lg.ignore(pattern, regex_flags)
        return self

    def lex(self, code: str) -> Iterable[Token]:
        lexer = self._lg.build()
        return lexer.lex(code)

    def build(self) -> 'Lexer':
        """
        This method exists so that Lexer can match the general interface of both LexerGenerator and Lexer from rply
        :return: self
        """
        return self
