from exceptions import LexingException
from lexing import Tokenizer
from parsing import Parser
from util import is_lexing_error


def lex_and_parse():
    tokenizer = Tokenizer()
    parser = Parser()
    try:
        return parser.parse(tokenizer.tokenize())
    except Exception as e:
        if is_lexing_error(e):
            raise LexingException()
        raise e
