"""This module contains the necessary class and functions needed to
help describing what a given exception or warning means
(i.e. the answer to ``why()``)
of an exception. Most of the content should be considered to be private.

It does contain one decorator (``register``)
which is intended to be part of the public API, but needs to be
imported from this module instead of simply from ``friendly_traceback``.
"""

import inspect
from typing import Any, Callable, Dict, Type

from .ft_gettext import current_lang, no_information
from .typing_info import GenericExplain

GENERIC: Dict[Type[BaseException], GenericExplain] = {}
SUBCLASS: Dict[Any, Any] = {}
_ = current_lang.translate


def get_generic_explanation(exception_type: Type[BaseException]) -> str:
    """Provides a generic explanation about a particular exception."""
    if hasattr(exception_type, "__name__"):
        exception_name = exception_type.__name__
    else:
        exception_name = exception_type
    if exception_type in GENERIC:
        return GENERIC[exception_type]()
    else:
        if not issubclass(exception_type, BaseException):
            return no_information()
        parents = inspect.getmro(exception_type)
        for index, parent in enumerate(parents):
            if parent in GENERIC:
                tree = [p.__name__ for p in parents[: index + 1]]
                break
        else:
            tree = [p.__name__ for p in parents]

        for parent in parents:
            if parent in GENERIC:
                if parent.__name__.endswith("Warning"):
                    explanation = _(
                        "A warning of type `{name}` is a subclass of `{parent}`.\n"
                    ).format(name=exception_name, parent=parent.__name__)
                else:
                    explanation = _(
                        "An exception of type `{name}` is a subclass of `{parent}`.\n"
                    ).format(name=exception_name, parent=parent.__name__)
                nothing_specific = _(
                    "Nothing more specific is known about `{name}`."
                ).format(name=exception_name)
                if len(tree) > 2:
                    nothing_specific += "\n" + _(
                        "The inheritance is as follows:\n\n" "    {tree}\n"
                    ).format(tree=" -> ".join(tree))
                return explanation + nothing_specific + "\n\n" + GENERIC[parent]()

        return no_information()


def register(
    error_class: Type[BaseException],
) -> Callable[[GenericExplain], GenericExplain]:
    """Decorator used to record as available an explanation for a given exception.

    Args:
        error_class: an exception class.

    Usage::

        from friendly_traceback.info_generic import register

        @register
        def describe(SomeErrorOrWarning) -> str:
            '''`SomeErrorOrWarning` means that ...'''
    """

    def add_exception(function):
        if error_class in GENERIC:
            message = f"A description of `{error_class.__name__}` already exists:\n\n"
            message += GENERIC[error_class]()
            raise ValueError(message)

        GENERIC[error_class] = function

        def wrapper():
            return function()

        return wrapper

    return add_exception


@register(Exception)
def _exception() -> str:
    return _(
        "Most built-in exceptions defined by Python are derived from `Exception`.\n"
        "All user-defined exceptions should also be derived from this class.\n"
    )


@register(BaseException)
def base_exception() -> str:
    return _(
        "`BaseException` is the base class for all built-in exceptions.\n"
        "It is not meant to be directly inherited by user-defined classes.\n"
    )


@register(ArithmeticError)
def arithmetic_error() -> str:
    return _(
        "`ArithmeticError` is the base class for those built-in exceptions\n"
        "that are raised for various arithmetic errors.\n"
    )


@register(AssertionError)
def assertion_error() -> str:
    return _(
        "In Python, the keyword `assert` is used in statements of the form\n"
        "`assert condition`, to confirm that `condition` is not `False`,\n"
        "nor equivalent to `False` such as an empty list, etc.\n\n"
        "If `condition` is `False` or equivalent, an `AssertionError` is raised.\n"
    )


@register(AttributeError)
def attribute_error() -> str:
    return _(
        "An `AttributeError` occurs when the code contains something like\n"
        "    `object.x`\n"
        "and `x` is not a method or attribute (variable) belonging to `object`.\n"
    )


@register(EOFError)
def eof_error() -> str:  # pragma: no cover
    return _(
        "An `EOFError` is raised when the `input()` function hits\n"
        "an end-of-file condition (EOF) without reading any data.\n"
    )


@register(FileNotFoundError)
def file_not_found_error() -> str:
    return _(
        "A `FileNotFoundError` exception indicates that you\n"
        "are trying to open a file that cannot be found by Python.\n"
        "This could be because you misspelled the name of the file.\n"
    )


@register(ImportError)
def import_error() -> str:
    return _(
        "An `ImportError` exception indicates that a certain object could not\n"
        "be imported from a module or package. Most often, this is\n"
        "because the name of the object is not spelled correctly.\n"
    )


@register(IndentationError)
def indentation_error() -> str:
    return _(
        "An `IndentationError` occurs when a given line of code is\n"
        "not indented (aligned vertically with other lines) as expected.\n"
    )


@register(IndexError)
def index_error() -> str:
    return _(
        "An `IndexError` occurs when you try to get an item from a list,\n"
        "a tuple, or a similar object (sequence), and use an index which\n"
        "does not exist; typically, this happens because the index you give\n"
        "is greater than the length of the sequence.\n"
    )


@register(KeyError)
def key_error() -> str:
    return _(
        "A `KeyError` is raised when a value is not found as a\n"
        "key in a Python dict or in a similar object.\n"
    )


@register(LookupError)
def lookup_error() -> str:
    return _(
        "`LookupError` is the base class for the exceptions that are raised\n"
        "when a key or index used on a mapping or sequence is invalid.\n"
        "It can also be raised directly by codecs.lookup().\n"
    )


@register(MemoryError)
def memory_error() -> str:
    return _(
        "Like the name indicates, a `MemoryError` occurs when Python\n"
        "runs out of memory. This can happen if you create an object\n"
        "that is too big, like a list with too many items.\n"
    )


@register(ModuleNotFoundError)
def module_not_found_error() -> str:
    return _(
        "A `ModuleNotFoundError` exception indicates that you\n"
        "are trying to import a module that cannot be found by Python.\n"
        "This could be because you misspelled the name of the module\n"
        "or because it is not installed on your computer.\n"
    )


@register(NameError)
def name_error() -> str:
    return _(
        "A `NameError` exception indicates that a variable or\n"
        "function name is not known to Python.\n"
        "Most often, this is because there is a spelling mistake.\n"
        "However, sometimes it is because the name is used\n"
        "before being defined or given a value.\n"
    )


@register(OSError)
def os_error() -> str:
    return _(
        "An `OSError` exception is usually raised by the Operating System\n"
        "to indicate that an operation is not allowed or that\n"
        "a resource is not available.\n"
    )


@register(OverflowError)
def overflow_error() -> str:
    return _(
        "An `OverflowError` is raised when the result of an arithmetic operation\n"
        "is too large to be handled by the computer's processor.\n"
    )


@register(RecursionError)
def recursion_error() -> str:
    return _(
        "A `RecursionError` is raised when a function calls itself,\n"
        "directly or indirectly, too many times.\n"
        "It almost always indicates that you made an error in your code\n"
        "and that your program would never stop.\n"
    )


@register(RuntimeError)
def runtime_error() -> str:
    return _(
        "A `RuntimeError` is raised when an error is detected that doesn't fall in any\n"
        "of the more specific exception types defined by Python.\n"
    )


@register(StopIteration)
def stop_iteration() -> str:
    return _(
        "`StopIteration` is raised to indicate that an iterator has no more\n"
        "item to provide when its `__next__` method is called by\n"
        "the `next()` builtin function.\n"
    )


@register(SyntaxError)
def syntax_error() -> str:
    return _("A `SyntaxError` occurs when Python cannot understand your code.\n")


@register(TabError)
def tab_error() -> str:
    return _(
        "A `TabError` indicates that you have used both spaces\n"
        "and tab characters to indent your code.\n"
        "This is not allowed in Python.\n"
        "Indenting your code means to have block of codes aligned vertically\n"
        "by inserting either spaces or tab characters at the beginning of lines.\n"
        "Python's recommendation is to always use spaces to indent your code.\n"
    )


@register(TypeError)
def type_error() -> str:
    return _(
        "A `TypeError` is usually caused by trying\n"
        "to combine two incompatible types of objects,\n"
        "by calling a function with the wrong type of object,\n"
        "or by trying to do an operation not allowed on a given type of object.\n"
    )


@register(ValueError)
def value_error() -> str:
    return _(
        "A `ValueError` indicates that a function or an operation\n"
        "received an argument of the right type, but an inappropriate value.\n"
    )


@register(UnboundLocalError)
def unbound_local_error() -> str:
    return _(
        "In Python, variables that are used inside a function are known as \n"
        "local variables. Before they are used, they must be assigned a value.\n"
        "A variable that is used before it is assigned a value is assumed to\n"
        "be defined outside that function; it is known as a `global`\n"
        "(or sometimes `nonlocal`) variable. You cannot assign a value to such\n"
        "a global variable inside a function without first indicating to\n"
        "Python that this is a global variable, otherwise you will see\n"
        "an `UnboundLocalError`.\n"
    )


@register(ZeroDivisionError)
def zero_division_error() -> str:
    return _(
        "A `ZeroDivisionError` occurs when you are attempting to divide a value\n"
        "by zero either directly or by using some other mathematical operation.\n"
    )


@register(UserWarning)
def user_warning() -> str:
    return _("`UserWarning` is the default class for `warnings.warn()`.\n")


@register(SyntaxWarning)
def syntax_warning() -> str:
    return _(
        "`SyntaxWarning` often indicates that your code will likely not give the result you expect.\n"
    )


@register(DeprecationWarning)
def deprecation_warning() -> str:
    return _(
        "`DeprecationWarning` indicates that some feature will not be available in a future version.\n"
    )


@register(RuntimeWarning)
def runtime_warning() -> str:
    return _(
        "`RuntimeWarning` often indicates some not recommended runtime features.\n"
    )


@register(FutureWarning)
def future_warning() -> str:
    return _(
        "`FutureWarning` is the base category for features that will likely be deprecated\n"
        "in future Python versions.\n"
    )


@register(UnicodeWarning)
def unicode_warning() -> str:
    return _("`UnicodeWarning` is the base category for warnings related to unicode.\n")


@register(BytesWarning)
def bytes_warning() -> str:
    return _(
        "`BytesWarning` is the base category for warnings related to bytes and bytearray.\n"
    )


@register(Warning)  # Keep this one as the last warning
def _warning() -> str:
    return _("`Warning` is the base class of all warning category classes.\n")


# The following are ignored by default:
#
# PendingDeprecationWarning
# Base category for warnings about features that will be deprecated in the future
#
# ImportWarning
# Base category for warnings triggered during the process of importing a module.
#
# ResourceWarning
# Base category for warnings related to resource usage (ignored by default).
