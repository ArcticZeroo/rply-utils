from enum import Enum
from re import RegexFlag
from typing import Dict, Union, Tuple, List, Iterable, Set

# TODO: Change this when a new project requires a local copy of rply
from rply import LexerGenerator, Token
from rply.lexer import Lexer

LexerRule = Union[str, Tuple[str, RegexFlag]]
LexerNamedRules = Dict[str, LexerRule]
LexerUnnamedRules = List[LexerRule]


class Tokenizer:
    TOKEN_IGNORE = '__rply_utils_token_ignore'

    _lexer: Lexer
    _ignore_index: int = 0
    possible_tokens: Set[str]

    def __init__(self, token_rules: LexerNamedRules = None, ignore_rules: LexerUnnamedRules = None):
        self._lexer = self._build_rply_lexer(token_rules or {}, ignore_rules or [])

    @staticmethod
    def _get_rule_params(token_rule: LexerRule) -> List[Union[str, RegexFlag]]:
        if isinstance(token_rule, str):
            return [token_rule]
        else:
            token_regex, regex_flags = token_rule
            return [token_regex, regex_flags]

    @staticmethod
    def _get_token_name(token):
        if isinstance(token, Enum):
            return token.name
        return token

    def _build_rply_lexer(self, token_rules: LexerNamedRules, ignore_rules: LexerUnnamedRules) -> Lexer:
        lg = LexerGenerator()
        for ignore_rule in ignore_rules:
            lg.ignore(*Tokenizer._get_rule_params(ignore_rule))

        for token, token_rule in token_rules.items():
            token_name = self._get_token_name(token)

            if token_name == self.TOKEN_IGNORE:
                token_name = f'{self.TOKEN_IGNORE}_{self._ignore_index}'
                self._ignore_index += 1
            else:
                self.possible_tokens.add(token_name)

            lg.add(token_name, *Tokenizer._get_rule_params(token_rule))

        return lg.build()

    def tokenize(self, text: str) -> Iterable[Token]:
        if self._ignore_index == 0:
            return self._lexer.lex(text)
        return filter(lambda token: self.TOKEN_IGNORE not in token.name,
                      self._lexer.lex(text))
