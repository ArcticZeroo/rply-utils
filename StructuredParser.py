import warnings
from abc import ABC
from typing import Callable, List, Tuple, Any

from rply import ParserGenerator
from rply.parser import LRParser

ATTRIBUTE_PRODUCTION = '_structured_parser_production'
ATTRIBUTE_ERROR = '_structured_parser_error'


class StructuredParserBase(ABC):
    parser: LRParser


def append_to_attribute_list(items: List[Tuple[Callable, Tuple]], attribute, method):
    if hasattr(method, attribute):
        items.append(getattr(method, attribute))


class _ConsumeParser:
    _structuredParser: StructuredParserBase
    _pg: ParserGenerator

    def __init__(self, parser: StructuredParserBase, tokens: List[str]):
        self._structuredParser = parser
        self._pg = ParserGenerator(tokens)
        self._build_parser()

    @staticmethod
    def _is_production(method: Callable):
        return hasattr(method, ATTRIBUTE_PRODUCTION)

    @staticmethod
    def _is_error(method: Callable):
        return hasattr(method, ATTRIBUTE_ERROR)

    @staticmethod
    def _unwrap_production(method: Callable) -> Tuple[str, Any]:
        args = getattr(method, ATTRIBUTE_PRODUCTION)
        if len(args) == 1:
            return args[0], None
        return args

    def _register_magic_decorator(self, method_name: str, decorator: Callable, *decorator_args):
        @decorator(*decorator_args)
        def magic_decorator(*pass_through_args):
            self._structuredParser.__dict__[method_name](*pass_through_args)

    def _register_production(self, method_name: str, method: Callable):
        rule, precedence = self._unwrap_production(method)
        self._register_magic_decorator(method_name, self._pg.production, rule, precedence)

    def _register_error(self, method_name: str):
        self._register_magic_decorator(method_name, self._pg.error_handler)

    def _register_decorators(self):
        for method_name, method in self._structuredParser.__dict__.items():
            if self._is_production(method):
                self._register_production(method_name, method)
            elif self._is_error(method):
                self._register_error(method_name)

    def _build_parser(self):
        self._register_decorators()
        self._structuredParser.parser = self._pg.build()


def consume_parser(*args):
    return _ConsumeParser(*args)


def _parser_marked_decorator(attribute: str):
    def decorator(method, *args):
        setattr(method, attribute, args)
        return method

    return decorator


production = _parser_marked_decorator(ATTRIBUTE_PRODUCTION)
error = _parser_marked_decorator(ATTRIBUTE_ERROR)


class StructuredParser(StructuredParserBase):
    def __init__(self):
        pass
