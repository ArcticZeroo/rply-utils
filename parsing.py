import inspect
from abc import ABC
from dataclasses import dataclass
from enum import Enum
from typing import Callable, List, Tuple, Any, Iterable, Dict, Optional, Union, TypeVar

from rply import ParserGenerator, Token
from rply.parser import LRParser

_ATTRIBUTE_REGISTRATIONS = '_structured_parser_registrations'
_REGISTRATION_TYPE_PRODUCTION = '_structured_parser_production'
_REGISTRATION_TYPE_EMPTY_PRODUCTION = '_structured_parser_empty_production'
_REGISTRATION_TYPE_ERROR = '_structured_parser_error'

END_TOKEN = '$end'

ParserListener = Callable[[List[Token]], Any]


class _StatefulParserBase(ABC):
    parser: LRParser


class _ParserConsumer:
    _statefulParser: _StatefulParserBase
    _pg: ParserGenerator

    def __init__(self, parser: _StatefulParserBase, tokens: List[str]):
        self._statefulParser = parser
        self._pg = ParserGenerator(tokens)

    @staticmethod
    def _is_production(method: Any) -> bool:
        return hasattr(method, _REGISTRATION_TYPE_PRODUCTION)

    @staticmethod
    def _is_empty_production(method: Any) -> bool:
        return hasattr(method, _REGISTRATION_TYPE_EMPTY_PRODUCTION)

    @staticmethod
    def _is_error(method: Any) -> bool:
        return hasattr(method, _REGISTRATION_TYPE_ERROR)

    @staticmethod
    def _unwrap_production_value(value: Tuple) -> Tuple[str, Any]:
        if len(value) == 1:
            return value[0], None
        return value

    @staticmethod
    def _unwrap_productions(method: ParserListener, attribute: str) -> List[Tuple[str, Any]]:
        return [_ParserConsumer._unwrap_production_value(v)
                for v in getattr(method, attribute)]

    def _register_production(self, method: ParserListener):
        requested_productions = self._unwrap_productions(method, _REGISTRATION_TYPE_PRODUCTION)
        for rule, precedence in requested_productions:
            self._pg.production(rule, precedence)(method)

    def _register_empty_production(self, method: ParserListener):
        attribute_value = getattr(method, _REGISTRATION_TYPE_EMPTY_PRODUCTION)
        empty_productions = attribute_value if isinstance(attribute_value, list) else [attribute_value]
        for value in empty_productions:
            rule, precedence = self._unwrap_production_value(value)

            @self._pg.production(rule, precedence)
            def noop(*_):
                pass

    def _register_error(self, method):
        self._pg.error(method)

    def _register_decorators(self):
        methods = inspect.getmembers(self._statefulParser, inspect.ismethod)
        for method_name, method in methods:
            if self._is_production(method):
                self._register_production(method)
            elif self._is_empty_production(method):
                self._register_empty_production(method)
            elif self._is_error(method):
                self._register_error(method)

    def build_parser(self):
        self._register_decorators()
        return self._pg.build()


def _add_decorator(method: Callable, attribute: str, value: Tuple[Any]):
    if hasattr(method, attribute):
        items: List[Tuple[Any]] = getattr(method, attribute)
        items.append(value)
    else:
        setattr(method, attribute, [value])


def _ensure_registration_list_exists(method: ParserListener):
    if not hasattr(method, _ATTRIBUTE_REGISTRATIONS):
        setattr(method, _ATTRIBUTE_REGISTRATIONS, [])


def _add_to_registration_list(method: ParserListener, name: str, value: Optional[Any] = None):
    _ensure_registration_list_exists(method)
    registrations: List[Tuple[str, Any]] = getattr(method, _ATTRIBUTE_REGISTRATIONS)
    registrations.append((name, value))


def _parser_production_decorator(name: str):
    # when a method decorator takes args in python,
    # instead of just passing the method in the first
    # param and args after, you only get args, return
    # a function that behaves like a normal decorator
    # (only gets the method), and can use the combination
    def decorator_with_args(rule: str, precedence: Optional[Any] = None):
        def decorator_for_method(method: ParserListener):
            _add_to_registration_list(method, name, (rule, precedence))
            return method

        return decorator_for_method

    return decorator_with_args


def _parser_marked_decorator(attribute: str, has_args: bool = True):
    if has_args:
        def outer_wrap(*args):
            def inner_wrap(method: ParserListener):
                _add_decorator(method, attribute, args)
                return method

            return inner_wrap

        return outer_wrap

    def wrapped_method(method):
        setattr(method, attribute, True)
        return method

    return wrapped_method


production = _parser_marked_decorator(_REGISTRATION_TYPE_PRODUCTION)
empty_production = _parser_marked_decorator(_REGISTRATION_TYPE_EMPTY_PRODUCTION)
error = _parser_marked_decorator(_REGISTRATION_TYPE_ERROR, has_args=False)


class StatefulParser(_StatefulParserBase):
    def __init__(self, tokens: List[str]):
        parser_consumer = _ParserConsumer(self, tokens)
        self.parser = parser_consumer.build_parser()

    def parse(self, tokens: Iterable[Token]) -> Any:
        # state is tracked by this class by default, no need to pass state.
        # ...passing state would actually not work if you expect it to replace self
        return self.parser.parse(tokens)


TState = TypeVar('TState')
EmptyProduction = None
Productions = Dict[str, Union[Callable[[List[Token], Optional[TState]], Any], EmptyProduction]]
ProductionPrecedences = Dict[str, Any]
ErrorHandler = Callable[[Token], None]


def _reverse_args_decorator(method):
    return lambda *args: method(args[::-1])


class Parser:
    _parser = LRParser
    _productions: Productions
    _error_handler: ErrorHandler

    def __init__(self, tokens: List[str], productions: Productions, error_handler: ErrorHandler = None,
                 precedences: Optional[ProductionPrecedences] = None):
        if len(productions) < 1:
            raise ValueError('Productions must not be empty')

        self._parser = self._build_parser(tokens, productions, error_handler, precedences)

    @staticmethod
    def _get_precedence(rule: str, precedences: Optional[ProductionPrecedences]):
        return None if precedences is None else precedences[rule]

    def _build_parser(self, tokens: List[str], productions: Productions, error_handler: Optional[ErrorHandler],
                      precedences: Optional[ProductionPrecedences]):
        pg = ParserGenerator(tokens)

        def noop():
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
