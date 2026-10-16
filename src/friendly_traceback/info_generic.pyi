import inspect
from typing import Any, Callable, Dict, Type
from .ft_gettext import current_lang, no_information
from .typing_info import GenericExplain

GENERIC: Dict[Type[BaseException], GenericExplain]
SUBCLASS: Dict[Any, Any]


def get_generic_explanation(exception_type: Type[BaseException]) -> str: ...


def register(error_class: Type[BaseException]) -> Callable[[GenericExplain], GenericExplain]: ...


@register(BaseException)
def base_exception() -> str: ...


@register(ArithmeticError)
def arithmetic_error() -> str: ...


@register(AssertionError)
def assertion_error() -> str: ...


@register(AttributeError)
def attribute_error() -> str: ...


@register(EOFError)
def eof_error() -> str: ...


@register(FileNotFoundError)
def file_not_found_error() -> str: ...


@register(ImportError)
def import_error() -> str: ...


@register(IndentationError)
def indentation_error() -> str: ...


@register(IndexError)
def index_error() -> str: ...


@register(KeyError)
def key_error() -> str: ...


@register(LookupError)
def lookup_error() -> str: ...


@register(MemoryError)
def memory_error() -> str: ...


@register(ModuleNotFoundError)
def module_not_found_error() -> str: ...


@register(NameError)
def name_error() -> str: ...


@register(OSError)
def os_error() -> str: ...


@register(OverflowError)
def overflow_error() -> str: ...


@register(RecursionError)
def recursion_error() -> str: ...


@register(RuntimeError)
def runtime_error() -> str: ...


@register(StopIteration)
def stop_iteration() -> str: ...


@register(SyntaxError)
def syntax_error() -> str: ...


@register(TabError)
def tab_error() -> str: ...


@register(TypeError)
def type_error() -> str: ...


@register(ValueError)
def value_error() -> str: ...


@register(UnboundLocalError)
def unbound_local_error() -> str: ...


@register(ZeroDivisionError)
def zero_division_error() -> str: ...


@register(UserWarning)
def user_warning() -> str: ...


@register(SyntaxWarning)
def syntax_warning() -> str: ...


@register(DeprecationWarning)
def deprecation_warning() -> str: ...


@register(RuntimeWarning)
def runtime_warning() -> str: ...


@register(FutureWarning)
def future_warning() -> str: ...


@register(UnicodeWarning)
def unicode_warning() -> str: ...


@register(BytesWarning)
def bytes_warning() -> str: ...
