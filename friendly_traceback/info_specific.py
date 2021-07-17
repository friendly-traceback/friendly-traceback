"""info_specific.py

Attempts to provide some specific information about the likely cause
of a given exception.
"""

import re
from types import FrameType
from typing import Callable, Dict, Type, TypeVar


from . import debug_helper
from .base_formatters import Info
from .core import TracebackData
from .ft_gettext import current_lang, internal_error

_E = TypeVar("_E", bound=BaseException)

Explain = Callable[[_E, FrameType, TracebackData], Info]


get_cause: Dict[Type[BaseException], Explain[BaseException]] = {}


def get_likely_cause(
    etype: Type[_E], value: _E, frame: FrameType, tb_data: TracebackData
) -> Info:
    """Gets the likely cause of a given exception based on some information
    specific to a given exception.
    """
    _ = current_lang.translate
    try:
        if etype in get_cause:
            return get_cause[etype](value, frame, tb_data)
    except Exception as e:  # noqa  # pragma: no cover
        debug_helper.log("Exception caught in get_likely_cause().")
        debug_helper.log_error(e)
        return {"cause": internal_error(e)}

    try:
        # see if it could be the result of using socket, or urllib, urllib3, etc.
        if issubclass(etype, OSError):
            return get_cause[OSError](value, frame, tb_data)
    except Exception:  # noqa  # pragma: no cover
        pass

    return {}


def register(error_name: Type[_E]) -> Callable[[Explain[_E]], Explain[_E]]:
    """Decorator used to record as available an explanation for a given exception"""

    def add_exception(function):
        get_cause[error_name] = function

    return add_exception


@register(AttributeError)
def _attribute_error(
    value: AttributeError, frame: FrameType, tb_data: TracebackData
) -> Info:
    from .runtime_errors import attribute_error

    return attribute_error.get_cause(value, frame, tb_data)


@register(FileNotFoundError)
def _file_not_found_error(value: FileNotFoundError, *_args) -> Info:
    _ = current_lang.translate
    # str(value) is expected to be something like
    #
    # fileNotFoundError: No module named 'does_not_exist'
    # or
    # [Error 2] No such file or directory: 'does_not_exist'
    #
    # By splitting value using ', we can extract the module name.
    message = str(value)
    pattern1 = re.compile("No module named '(.*)'")
    match1 = re.search(pattern1, message)
    pattern2 = re.compile("No such file or directory: '(.*)'")
    match2 = re.search(pattern2, message)
    if match1 is None:
        if match2 is None:
            return {}
        filename = match2.group(1)
    else:
        filename = match1.group(1)

    return {
        "cause": _(
            "In your program, the name of the\n"
            "file that cannot be found is `{filename}`.\n"
        ).format(filename=filename)
    }


@register(ImportError)
def _import_error(value: ImportError, frame: FrameType, tb_data: TracebackData) -> Info:
    from .runtime_errors import import_error

    return import_error.parser.get_cause(str(value), frame, tb_data)


@register(IndexError)
def _index_error(value: IndexError, frame: FrameType, tb_data: TracebackData) -> Info:
    from .runtime_errors import index_error

    return index_error.get_cause(value, frame, tb_data)


@register(KeyError)
def _key_error(value: KeyError, frame: FrameType, tb_data: TracebackData) -> Info:
    _ = current_lang.translate
    from .runtime_errors import key_error

    return key_error.parser.get_cause(value, frame, tb_data)


@register(ModuleNotFoundError)
def _module_not_found_error(
    value: ModuleNotFoundError, frame: FrameType, tb_data: TracebackData
) -> Info:

    from .runtime_errors import module_not_found_error

    return module_not_found_error.parser.get_cause(str(value), frame, tb_data)


@register(NameError)
def _name_error(value: NameError, frame: FrameType, tb_data: TracebackData) -> Info:

    from .runtime_errors import name_error

    return name_error.get_cause(value, frame, tb_data)


@register(OSError)
def _os_error(value: OSError, frame: FrameType, tb_data: TracebackData) -> Info:

    from .runtime_errors import os_error

    return os_error.get_cause(value, frame, tb_data)


@register(OverflowError)
def _overflow_error(*_args) -> Info:
    return {}
    # can be provided for real test cases


@register(TypeError)
def _type_error(value: TypeError, frame: FrameType, tb_data: TracebackData) -> Info:
    from .runtime_errors import type_error

    return type_error.parser.get_cause(str(value), frame, tb_data)


@register(ValueError)
def _value_error(value: ValueError, frame: FrameType, tb_data: TracebackData) -> Info:
    from .runtime_errors import value_error

    return value_error.parser.get_cause(str(value), frame, tb_data)


@register(UnboundLocalError)
def _unbound_local_error(
    value: UnboundLocalError, frame: FrameType, tb_data: TracebackData
) -> Info:
    from .runtime_errors import unbound_local_error

    return unbound_local_error.get_cause(value, frame, tb_data)


@register(ZeroDivisionError)
def _zero_division_error(
    value: ZeroDivisionError, frame: FrameType, tb_data: TracebackData
) -> Info:
    from .runtime_errors import zero_division_error

    return zero_division_error.parser.get_cause(str(value), frame, tb_data)
