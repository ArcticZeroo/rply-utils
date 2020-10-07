from exceptions import LexingException
from lexing import Tokenizer, LexerNamedRules, LexerUnnamedRules
from parsing import Parser, Productions
from util import is_lexing_error


class Compiler:
    _tokenizer: Tokenizer
    _parser: Parser

    def __init__(self, token_rules: LexerNamedRules, productions: Productions, ignore_rules: LexerUnnamedRules = None):
        self._tokenizer = Tokenizer(token_rules, ignore_rules)
        self._parser = Parser(self._tokenizer.possible_tokens, productions)

    def lex_and_parse(self, code: str):
        try:
            return self._parser.parse(self._tokenizer.tokenize(code))
        except Exception as e:
            if is_lexing_error(e):
                raise LexingException() from None
            raise e from None
