from re import RegexFlag
from typing import Dict, Union, Tuple, List, Iterable

# TODO: Change this when a new project requires a local copy of rply
from rply import LexerGenerator, Token
from rply.lexer import Lexer

LexerRule = Union[str, Tuple[str, RegexFlag]]
LexerNamedRules = Dict[str, LexerRule]
LexerUnnamedRules = List[LexerRule]


class Tokenizer:
    _lexer: Lexer

    def __init__(self, token_rules: LexerNamedRules, ignore_rules: LexerUnnamedRules):
        _lexer = self._build_rply_lexer(token_rules, ignore_rules)

    @staticmethod
    def _get_rule_params(token_rule: LexerRule) -> List[Union[str, RegexFlag]]:
        if isinstance(token_rule, str):
            return [token_rule]
        else:
            token_regex, regex_flags = token_rule
            return [token_regex, regex_flags]

    @staticmethod
    def _build_rply_lexer(token_rules: LexerNamedRules, ignore_rules: LexerUnnamedRules) -> Lexer:
        lg = LexerGenerator()
        for ignore_rule in ignore_rules:
            lg.ignore(*Tokenizer._get_rule_params(ignore_rule))

        for token_name, token_rule in token_rules.items():
            lg.add(token_name, *Tokenizer._get_rule_params(token_rule))

        return lg.build()

    def tokenize(self, text: str) -> Iterable[Token]:
        return self._lexer.lex(text)
