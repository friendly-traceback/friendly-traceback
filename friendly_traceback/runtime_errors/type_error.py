"""type_error.py

Collection of functions useful in parsing TypeError messages and
providing a more detailed explanation.
"""

import inspect
import re
from types import FrameType
from typing import Any, List, Optional, Tuple, Type

from .. import debug_helper, info_variables, token_utils, utils
from ..ft_gettext import current_lang, no_information, please_report
from ..message_parser import get_parser
from ..tb_data import TracebackData  # for type checking only
from ..typing_info import CauseInfo  # for type checking only

convert_type = info_variables.convert_type
parser = get_parser(TypeError)
_ = current_lang.translate


def _convert_str_to_number(
    obj_type1: str, obj_type2: str, frame: FrameType, tb_data: TracebackData
) -> Tuple[Optional[str], Optional[str]]:
    """Determines if a suggestion should be made to convert a string to a
    number type; potentially useful for beginners that write programs
    that use input() and ask for numbers.
    """
    types = obj_type1, obj_type2
    if "int" in types:
        number_type = "int"
        convert = int
    elif "float" in types:
        number_type = "float"
        convert = float
    elif "complex" in types:
        number_type = "complex"
        convert = complex
    else:
        return None, None

    all_objects = info_variables.get_all_objects(tb_data.bad_line, frame)["name, obj"]
    for name, obj in all_objects:
        if isinstance(obj, str):
            try:
                convert(obj)
            except Exception:  # noqa
                continue
            break
    else:
        return None, None

    hint = _(
        "Did you forget to convert the string `{name}` into {number_type}?\n"
    ).format(
        name=name, number_type=convert_type(number_type)  # noqa
    )
    cause = _(
        "Perhaps you forgot to convert the string `{name}` into {number_type}.\n"
    ).format(name=name, number_type=convert_type(number_type))
    return cause, hint


@parser._add
def cant_mod_complex_number(message: str, tb_data: TracebackData) -> CauseInfo:
    valid_message = "can't mod complex numbers" in message or (
        "unsupported operand type(s) for %:" in message and "complex" in message
    )
    return (
        {"cause": _("You cannot use complex numbers with the modulo operator `%`.\n")}
        if valid_message
        else {}
    )


@parser._add
def cant_take_floor_or_mod_of_complex_number(
    message: str, tb_data: TracebackData
) -> CauseInfo:
    if "can't take floor or mod of complex number." not in message:
        return {}
    if "divmod" not in tb_data.bad_line:
        debug_helper.log(
            "'divmod' not found in cant_take_floor_or_mod_of_complex_number"
        )
        return {}
    cause = _(
        "The arguments of `divmod` must be integers (`int`) or real (`float`) numbers.\n"
    )
    # separate cause in two to minimize the amount of translation required;
    # see unsupported_type_for_divmod
    cause += _("At least one of the arguments was a complex number.\n")
    return {"cause": cause}


@parser._add
def unsupported_type_for_divmod(message: str, _tb_data: TracebackData) -> CauseInfo:
    # TODO: try with string arguments
    if "unsupported operand type(s) for divmod()" not in message:
        return {}
    cause = _(
        "The arguments of `divmod` must be integers (`int`) or real (`float`) numbers.\n"
    )
    if "complex" in message:
        cause += _("At least one of the arguments was a complex number.\n")
    return {"cause": cause}


@parser._add
def getattr_or_hasattr_attribute_name_must_be_string(
    message: str, tb_data: TracebackData
) -> CauseInfo:
    # Python 3.11 does not include 'getattr()' nor 'hasattr()' in message
    # We make the assumption that if the name of these function appears in
    # the bad_line, it is the source of the error.
    if "attribute name must be string" not in message:
        return {}
    if (
        "getattr(): attribute name must be string" in message
        or "getattr" in tb_data.bad_line
    ):
        cause = _("The second argument of the function `getattr()` must be a string.\n")
    elif (
        "hasattr(): attribute name must be string" in message
        or "hasattr" in tb_data.bad_line
    ):
        cause = _("The second argument of the function `hasattr()` must be a string.\n")
    else:
        cause = (
            _("Some attribute of a function you called is expected to be a string.\n")
            + please_report()
        )

    return {"cause": cause}


@parser._add
def parse_can_only_concatenate(message: str, tb_data: TracebackData) -> CauseInfo:
    # example: can only concatenate str (not "int") to str
    pattern = re.compile(
        r"can only concatenate (\w+) \(not [\'\"](\w+)[\'\"]\) to (\w+)"
    )
    match = re.search(pattern, message)
    if match is None:
        return {}

    obj_type1 = match[1]
    obj_type2 = match[2]
    frame = tb_data.exception_frame

    cause = _(
        "You tried to concatenate (add) two different types of objects:\n"
        "{first} and {second}.\n"
    ).format(first=convert_type(obj_type1), second=convert_type(obj_type2))
    if obj_type1 == "str":
        more_cause, possible_hint = _convert_str_to_number(
            obj_type1, obj_type2, frame, tb_data
        )
        if more_cause is not None:
            return {"cause": cause + more_cause, "suggest": possible_hint}
    return {"cause": cause}


@parser._add
def parse_must_be_str(message: str, tb_data: TracebackData) -> CauseInfo:
    # python 3.6 version: must be str, not int
    # example: can only concatenate str (not "int") to str
    pattern = re.compile(r"must be str, not (\w+)")
    match = re.search(pattern, message)
    if match is None:
        return {}

    frame = tb_data.exception_frame
    cause = _(
        "You tried to concatenate (add) two different types of objects:\n"
        "{first} and {second}.\n"
    ).format(first=convert_type("str"), second=convert_type(match[1]))
    if match[1] in ["int", "float", "complex"]:
        more_cause, possible_hint = _convert_str_to_number(
            "str", match[1], frame, tb_data
        )
        if more_cause is not None:
            return {"cause": cause + more_cause, "suggest": possible_hint}
    return {"cause": cause}


@parser._add
def parse_unsupported_operand_type(message: str, tb_data: TracebackData) -> CauseInfo:
    more_cause = possible_hint = hint = None
    # example: unsupported operand type(s) for +: 'int' and 'str'
    pattern = re.compile(
        r"unsupported operand type\(s\) for (.+): [\'\"](\w+)[\'\"] and [\'\"](\w+)[\'\"]"
    )
    match = re.search(pattern, message)
    if match is None:
        return {}

    frame = tb_data.exception_frame
    all_objects = info_variables.get_all_objects(tb_data.bad_line, frame)["name, obj"]
    operator = match[1]
    obj_type1 = match[2]
    obj_type2 = match[3]
    if operator in ["+", "+="]:
        cause = _(
            "You tried to add two incompatible types of objects:\n"
            "{first} and {second}.\n"
        ).format(first=convert_type(obj_type1), second=convert_type(obj_type2))
        more_cause, possible_hint = _convert_str_to_number(
            obj_type1, obj_type2, frame, tb_data
        )
    elif operator in ["-", "-="]:
        cause = _(
            "You tried to subtract two incompatible types of objects:\n"
            "{first} and {second}.\n"
        ).format(first=convert_type(obj_type1), second=convert_type(obj_type2))
        more_cause, possible_hint = _convert_str_to_number(
            obj_type1, obj_type2, frame, tb_data
        )
    elif operator in ["*", "*="]:
        cause = _(
            "You tried to multiply two incompatible types of objects:\n"
            "{first} and {second}.\n"
        ).format(first=convert_type(obj_type1), second=convert_type(obj_type2))
        more_cause, possible_hint = _convert_str_to_number(
            obj_type1, obj_type2, frame, tb_data
        )
    elif operator in ["/", "//", "/=", "//="]:
        cause = _(
            "You tried to divide two incompatible types of objects:\n"
            "{first} and {second}.\n"
        ).format(first=convert_type(obj_type1), second=convert_type(obj_type2))
        more_cause, possible_hint = _convert_str_to_number(
            obj_type1, obj_type2, frame, tb_data
        )
    elif operator in ["&", "|", "^", "&=", "|=", "^="]:
        cause = _(
            "You tried to perform the bitwise operation {operator}\n"
            "on two incompatible types of objects:\n"
            "{first} and {second}.\n"
        ).format(
            operator=operator,
            first=convert_type(obj_type1),
            second=convert_type(obj_type2),
        )
        if "^" in operator:
            can_exponentiate = any(
                hasattr(obj, "__pow__") for _name, obj in all_objects
            )
            if can_exponentiate:
                line = tb_data.bad_line.replace("^", "**").strip()
                hint = _("Did you mean `{line}`?\n").format(line=line)
                cause += _(
                    "Outside of Python, `^` is often used to indicate exponentiation.\n"
                )
                cause += _("Perhaps you meant `{line}`.\n").format(line=line)

    elif operator in [">>", "<<", ">>=", "<<="]:
        cause = _(
            "You tried to perform the bit shifting operation {operator}\n"
            "on two incompatible types of objects:\n"
            "{first} and {second}.\n"
        ).format(
            operator=operator,
            first=convert_type(obj_type1),
            second=convert_type(obj_type2),
        )
    elif operator in ("** or pow()", "**="):
        cause = _(
            "You tried to exponentiate (raise to a power)\n"
            "using two incompatible types of objects:\n"
            "{first} and {second}.\n"
        ).format(first=convert_type(obj_type1), second=convert_type(obj_type2))
        more_cause, possible_hint = _convert_str_to_number(
            obj_type1, obj_type2, frame, tb_data
        )
    elif operator in ["@", "@="]:
        cause = _(
            "You tried to use the operator {operator}\n"
            "using two incompatible types of objects:\n"
            "{first} and {second}.\n"
            "This operator is normally used only\n"
            "for multiplication of matrices.\n"
        ).format(
            operator=operator,
            first=convert_type(obj_type1),
            second=convert_type(obj_type2),
        )
    else:
        return {"cause": no_information()}

    if more_cause is not None:
        cause += more_cause
        hint = possible_hint
    cause = {"cause": cause}
    if hint is not None:
        cause["suggest"] = hint
    return cause


@parser._add
def parse_order_comparison(message: str, tb_data: TracebackData) -> CauseInfo:
    # example: '<' not supported between instances of 'int' and 'str'
    pattern = re.compile(
        r"[\'\"](.+)[\'\"] not supported between instances of [\'\"]([\.\w]+)[\'\"] and [\'\"]([\.\w]+)[\'\"]"  # noqa
    )
    match = re.search(pattern, message)
    if match is None:
        return {}

    frame = tb_data.exception_frame
    if match[2] == match[3] == "complex":
        hint = _("Complex numbers cannot be ordered.\n")
        cause = _(
            "You tried to do an order comparison ({operator})\n"
            "between two complex numbers.\n"
        ).format(operator=match[1])
        return {"cause": cause, "suggest": hint}

    cause = _(
        "You tried to do an order comparison ({operator})\n"
        "between two incompatible types of objects:\n"
        "{first} and {second}.\n"
    ).format(
        operator=match[1],
        first=convert_type(match[2]),
        second=convert_type(match[3]),
    )

    other = number = None
    if match[2] in ["int", "float"]:
        number = match[2]
        other = match[3]
    elif match[3] in ["int", "float"]:
        number = match[3]
        other = match[2]

    other_obj = info_variables.get_object_from_name(other, frame)

    if number is not None:
        if other == "str":
            more_cause, possible_hint = _convert_str_to_number(
                "str", number, frame, tb_data
            )
            if more_cause is not None:
                return {"cause": cause + more_cause, "suggest": possible_hint}
        elif hasattr(other_obj, "__next__") and hasattr(other_obj, "__iter__"):
            more_cause = _(
                "`{iter}` is an iterator. You likely needed to write something like\n\n"
                "    next({iter}())\n\n"
                "or use it in a `for` loop to get a number from it\n"
                "before comparing it to {number}.\n"
            ).format(iter=other, number=convert_type(number))
            return {"cause": cause + "\n" + more_cause}

    return {"cause": cause}


@parser._add
def bad_operand_type_for_unary(message: str, tb_data: TracebackData) -> CauseInfo:
    # example: bad operand type for unary +: 'str'
    pattern = re.compile(r"bad operand type for unary (.+): [\'\"](\w+)[\'\"]")
    match = re.search(pattern, message)
    if match is None:
        return {}

    hint = None
    # The user might have written something like "=+" instead of
    # "+="
    operator = match[1]
    index = token_utils.find_substring_index(
        tb_data.original_bad_line, tb_data.bad_line
    )
    if index > 0:
        tokens = token_utils.get_significant_tokens(tb_data.original_bad_line)
        if (
            tokens[index - 1] == "="
            and tokens[index - 1].end_col == tokens[index].start_col
        ):
            hint = _(
                "Perhaps you meant to write `{operator}=` instead of `={operator}`"
            ).format(operator=operator)

    cause = _(
        "You tried to use the unary operator '{operator}'\n"
        "with the following type of object: {obj}.\n"
        "This operation is not defined for this type of object.\n"
    ).format(operator=operator, obj=convert_type(match[2]))
    if hint is not None:
        cause += "\n" + hint + "\n"
    cause = {"cause": cause}
    if hint is not None:
        cause["suggest"] = hint

    return cause


@parser._add
def does_not_support_item_assignment(
    message: str, _tb_data: TracebackData
) -> CauseInfo:
    # example: 'tuple' object does not support item assignment
    pattern = re.compile(r"[\'\"](\w+)[\'\"] object does not support item assignment")
    match = re.search(pattern, message)
    if match is None:
        return {}

    hint = None
    name = match[1]
    cause = _(
        "In Python, some objects are known as immutable:\n"
        "once defined, their value cannot be changed.\n"
        "You tried change part of such an immutable object: {obj},\n"
        "most likely by using an indexing operation.\n"
    ).format(obj=convert_type(name))
    if name in ("tuple", "set"):
        hint = _("Did you mean to use a list?\n")
        cause += _("Perhaps you meant to use a list instead.\n")
    cause = {"cause": cause}
    if hint is not None:
        cause["suggest"] = hint
    return cause


@parser._add
def exception_derived_from_base_exception(
    message: str, _tb_data: TracebackData
) -> CauseInfo:
    if "exceptions must derive from BaseException" in message:
        return {
            "cause": _(
                "Exceptions must be derived from `BaseException`.\n"
                "It is recommended that user-defined exceptions derive from\n"
                "`Exception`, a subclass of `BaseException`.\n"
            )
        }
    return {}


@parser._add
def catch_class_derived_from_base_exception(
    message: str, tb_data: TracebackData
) -> CauseInfo:
    if (
        "catching classes that do not inherit from BaseException is not allowed"
        not in message
    ):
        return {}

    all_objects = info_variables.get_all_objects(
        tb_data.bad_line, tb_data.exception_frame
    )["name, obj"]
    not_exceptions = [
        name for name, obj in all_objects if not issubclass(obj, BaseException)
    ]

    cause = _(
        "In an `except` statement, you must only have classes that derive from `BaseException`.\n"
    )
    if len(not_exceptions) == 1:
        cause += _("The following is not a valid classes: `{not_exception}`.\n").format(
            not_exception=not_exceptions[0]
        )
    else:
        cause += _("The following are not valid classes: `{not_exception}`.\n").format(
            not_exception=utils.list_to_string(not_exceptions)
        )

    return {"cause": cause}


@parser._add
def incorrect_nb_positional_arguments(
    message: str, tb_data: TracebackData
) -> CauseInfo:
    missing_self = False
    # example: my_function() takes 0 positional arguments but x was/were given
    pattern = re.compile(r"(.*) takes (\d+) positional argument[s]* but (\d+) ")
    match = re.search(pattern, message)

    if match is None:
        return {}

    hint = None
    fn_name = match[1][:-2]
    nb_required = match[2]
    nb_given = match[3]
    if ".<locals>." in fn_name:
        fn_name = fn_name.split(".<locals>.")[1]
    if int(nb_given) - int(nb_required) == 1:
        if "." in fn_name:
            missing_self = True
        else:
            tokens = token_utils.get_significant_tokens(tb_data.bad_line)
            missing_self = False
            prev_token = tokens[0]
            for token in tokens:
                if token == fn_name and prev_token == ".":
                    missing_self = True
                    break
                prev_token = token
    cause = _(
        "You apparently have called the function `{fn_name}` with\n"
        "{nb_given} positional argument(s) while it requires {nb_required}\n"
        "such positional argument(s).\n"
    ).format(fn_name=fn_name, nb_given=nb_given, nb_required=nb_required)
    if missing_self:
        hint = _("Perhaps you forgot `self` when defining `{fn_name}`.\n").format(
            fn_name=fn_name
        )
        cause += hint
    cause = {"cause": cause}
    if hint:
        cause["suggest"] = hint
    return cause


@parser._add
def missing_positional_arguments(message: str, _tb_data: TracebackData) -> CauseInfo:
    # example: my_function() missing 1 required positional argument
    pattern = re.compile(r"(.*) missing (\d+) required positional argument")
    match = re.search(pattern, message)

    if match is None:
        return {}

    return {
        "cause": _(
            "You apparently have called the function '{fn_name}' with\n"
            "fewer positional arguments than it requires ({nb_required} missing).\n"
        ).format(fn_name=match[1], nb_required=match[2])
    }


@parser._add
def x_is_not_callable(message: str, tb_data: TracebackData) -> CauseInfo:
    pattern = re.compile(r"'(.*)' object is not callable")
    match = re.search(pattern, message)
    if match is None:
        return {}

    frame = tb_data.exception_frame
    obj_type = match[1]
    if obj_type == "NoneType":
        none_type = _(
            "\nNote: `NoneType` means that the object has a value of `None`.\n"
        )
    else:
        none_type = ""

    # Start with default cause, in case we cannot do better
    cause = _(
        "Python indicates that you have an object of type `{obj_type}`,\n"
        "followed by something surrounded by parentheses, `(...)`,\n"
        "which Python took as an indication of a function call.\n"
        "Either the object of type `{obj_type}` was meant to be a function,\n"
        "or you forgot a comma before `(...)`.\n"
    ).format(obj_type=obj_type)

    obj = info_variables.get_object_from_name(obj_type, frame)
    all_objects = info_variables.get_all_objects(tb_data.bad_line, frame)["name, obj"]
    for obj_name, instance in all_objects:
        try:
            if isinstance(instance, obj) or instance == obj:
                fn_call = tb_data.bad_line.replace(obj_name, "", 1).strip()
                if fn_call.startswith("(") and fn_call.endswith(")"):
                    break
        except Exception:  # noqa
            continue
    else:
        return {"cause": cause + none_type}

    if fn_call.replace(" ", "") == "()":
        cause = _(
            "The parenthesis `()` following `{obj_name}` are interpreted\n"
            "by Python as a function call for `{obj_name}`.\n"
            "However, `{obj_name}` is not a function but an object of type `{obj_type}`.\n"
        ).format(obj_name=obj_name, obj_type=obj_type)
        return {"cause": cause + none_type}

    cause = _(
        "Because of the surrounding parenthesis, `{fn_call}` \n"
        "is interpreted by Python as indicating a function call for \n"
        "`{obj_name}`, which is an object of type `{obj_type}`\n"
        "which cannot be called.\n\n"
    ).format(fn_call=fn_call, obj_name=obj_name, obj_type=obj_type)

    try:
        can_eval = utils.eval_expr(fn_call, frame)
    except Exception:  # noqa
        return {"cause": cause + none_type}

    if isinstance(can_eval, tuple):
        cause = cause + _(
            "However, `{fn_call}` is a `tuple`.\n"
            "Either the object `{obj_name}` was meant to be a function\n"
            "or you have a missing comma between the object `{obj_name}`\n"
            "and the tuple `{fn_call}` and meant to write\n"
            "`{obj_name}, {fn_call}`.\n"
        ).format(fn_call=fn_call, obj_name=obj_name)
        hint = _(
            "Did you forget a comma between `{obj_name}` and `{fn_call}`?\n"
        ).format(fn_call=fn_call, obj_name=obj_name)
        return {"cause": cause, "suggest": hint}

    if hasattr(obj, "__getitem__") and isinstance(can_eval, int):
        cause = cause + _(
            "However, `{obj_name}` is a sequence.\n"
            "Perhaps you meant to use `[]` instead of `()` and write\n"
            "`{obj_name}[{slice}]`\n"
        ).format(obj_name=obj_name, slice=fn_call[1:-1])
        hint = _("Did you mean `{obj_name}[{slice}]`?\n").format(
            obj_name=obj_name, slice=fn_call[1:-1]
        )
        return {"cause": cause, "suggest": hint}

    if (  # Many objects can be multiplied, but only numbers should have __abs__
        hasattr(obj, "__abs__")  # Should identify numbers: int, float, ...
        and hasattr(can_eval, "__abs__")  # complex, Fractions, Decimals, ...
        and hasattr(obj, "__mul__")  # Confirming that they can be multiplied
        and hasattr(can_eval, "__mul__")
    ):
        cause = cause + _(
            "However, both `{obj_name}` and `{fn_call}` are numbers.\n"
            "Perhaps you forgot a multiplication operator, `*`,\n"
            "and meant to write `{obj_name} * {fn_call}`.\n"
        ).format(fn_call=fn_call, obj_name=obj_name)
        hint = _("Did you mean `{obj_name} * {fn_call}`?\n").format(
            fn_call=fn_call, obj_name=obj_name
        )
        return {"cause": cause, "suggest": hint}

    return {"cause": cause}


def forgot_to_convert_name_to_int(name: str) -> Tuple[str, str]:
    """Explanations common to many cases about converting a single
    name to an integer.
    """
    hint = _("Did you forget to convert `{name}` into an integer?\n").format(name=name)
    additional_cause = _(
        "Perhaps you forgot to convert `{name}` into an integer.\n"
    ).format(name=name)
    return additional_cause, hint


@parser._add
def cannot_multiply_by_str(message: str, tb_data: TracebackData) -> CauseInfo:
    if "can't multiply sequence by non-int of type 'str'" not in message:
        return {}

    frame = tb_data.exception_frame
    cause = _(
        "You can only multiply sequences, such as list, tuples,\n "
        "strings, etc., by integers.\n"
    )
    names = find_possible_integers(str, frame, tb_data.bad_line)
    if names:
        tokens = token_utils.get_significant_tokens(tb_data.bad_line)
        int_vars = []
        for prev_token, token in zip(tokens, tokens[1:]):
            if prev_token.string in ("*", "*=") and token.string in names:
                int_vars.append(token.string)
            elif prev_token.string in names and token == "*":
                int_vars.append(prev_token.string)
            else:
                continue
        if not int_vars:  # should not happen, but better be safe
            return {"cause": cause}

        if len(int_vars) == 1:
            more_cause, hint = forgot_to_convert_name_to_int(int_vars[0])
            cause += more_cause
        else:
            hint = _(
                "Did you forget to convert `{name1}` and `{name2}` into integers?\n"
            ).format(name1=int_vars[0], name2=int_vars[1])
            cause += _(
                "Perhaps you forgot to convert `{name1}` and `{name2}` into integers.\n"
            ).format(name1=int_vars[0], name2=int_vars[1])
        return {"cause": cause, "suggest": hint}

    return {"cause": cause}


def find_possible_integers(
    object_of_type: Type[Any], frame: FrameType, line: str
) -> List[str]:
    all_objects = info_variables.get_all_objects(line, frame)
    names = []
    for name, obj in all_objects["name, obj"]:
        if isinstance(obj, object_of_type):
            try:
                int(obj)  # noqa
                names.append(name)
            except Exception:  # noqa
                pass

    return names


@parser._add
def object_cannot_be_interpreted_as_an_integer(
    message: str, tb_data: TracebackData
) -> CauseInfo:
    pattern = re.compile(r"'(.*)' object cannot be interpreted as an integer")
    match = re.search(pattern, message)
    if match is None:
        return {}

    frame = tb_data.exception_frame
    obj_name = match[1]
    if obj_name == "NoneType":
        cause = _(
            "You wrote an object whose value is `None` where an integer was expected.\n"
        ).format(obj=obj_name)
        return {"cause": cause}
    object_of_type = info_variables.get_object_from_name(obj_name, frame)
    if object_of_type is None:
        return {}

    hint = None
    names = find_possible_integers(object_of_type, frame, tb_data.bad_line)
    cause = _(
        "You wrote an object of type `{obj}` where an integer was expected.\n"
    ).format(obj=obj_name)

    if names:
        if len(names) == 1:
            more_cause, hint = forgot_to_convert_name_to_int(names[0])
            cause += more_cause
        else:
            names = ", ".join(names)
            hint = _("Did you forget to convert `{names}` into integers?\n").format(
                names=names
            )
            cause += _("Perhaps you forgot to convert `{names}` into integers.").format(
                names=names
            )

    cause = {"cause": cause}
    if hint is not None:
        cause["suggest"] = hint

    return cause


@parser._add
def indices_must_be_integers_or_slices(
    message: str, tb_data: TracebackData
) -> CauseInfo:
    pattern = re.compile(r"(.*) indices must be integers or slices, not (.*)")
    match = re.search(pattern, message)
    if match is None:
        return {}

    frame = tb_data.exception_frame
    container_type = match[1]
    index_type = match[2]
    cause = _(
        "In the expression `{line}`\n"
        "what is included between the square brackets, `[...]`,\n"
        "must be either an integer or a slice\n"
        "(`start:stop` or `start:stop:step`) \n"
        "and you have used {obj_type} instead.\n"
    ).format(line=tb_data.bad_line, obj_type=convert_type(index_type))

    if index_type == "tuple":  # Example: [1, 2] [2,3] --> tuple == 2,3
        # Default message in case we do not manage to separate out what is
        # the first object and the list.
        additional_cause = "\n" + _(
            "Note: sometimes this exception is raised because what Python\n"
            "interprets as indices was meant to be a separate list, and a comma\n"
            "should have been written before the opening `[` of that list.\n"
        )
        hint = _("Did you forget a comma?\n")
    else:
        additional_cause = hint = None

    # To see if we can get more specific info,
    # we assume we have container[...]
    # and we look for two cases:
    # 1. if ... is a tuple, if we replace commas by colons (, --> :)
    #    do we get a valid expression.
    # 2. if ... is something of another type that can be converted into an integer
    try:
        container_type = utils.eval_expr(container_type, frame)
    except Exception:  # noqa
        if additional_cause:
            return {"cause": cause + additional_cause, "suggest": hint}
        return {"cause": cause}

    all_objects = info_variables.get_all_objects(tb_data.bad_line, frame)
    for name, obj in all_objects["name, obj"]:
        if isinstance(obj, container_type) and tb_data.bad_line.startswith(name):
            container = name
            break
    else:
        if additional_cause:
            return {"cause": cause + additional_cause, "suggest": hint}
        return {"cause": cause}

    not_index = tb_data.bad_line.replace(container, "", 1).strip()
    if not not_index.startswith("[") or not not_index.endswith("]"):
        if additional_cause:
            return {"cause": cause + additional_cause, "suggest": hint}
        return {"cause": cause}

    wrong_index = not_index[1:-1]
    if container == not_index:
        additional_cause = "\n" + _(
            "Perhaps you have forgotten a comma between two identical lists\n"
            "`{container}`. The second list had been interpreted as\n"
            "the indexation of the first one by the index `{new_index}`\n"
        ).format(container=container, new_index=f"({wrong_index})")
    else:
        additional_cause = "\n" + _(
            "Perhaps you have forgotten a comma between the object `{container}`\n"
            "and the list `{index}`.  The list `{index}` had been interpreted as\n"
            "the indexation of object `{container}` by the index `{new_index}`\n"
        ).format(container=container, index=not_index, new_index=f"({wrong_index})")
        hint = _("Did you forget a comma before `{index}`?\n").format(index=not_index)

    try:
        index = utils.eval_expr(wrong_index, frame)
        index_type = utils.eval_expr(index_type, frame)
    except Exception:  # noqa
        if additional_cause:
            return {"cause": cause + additional_cause, "suggest": hint}
        return {"cause": cause}

    if not isinstance(index, index_type):
        if additional_cause:
            return {"cause": cause + additional_cause, "suggest": hint}
        return {"cause": cause}

    if isinstance(index, tuple):
        # container[a, b] --> [][a: b]
        newline = (
            tb_data.bad_line.replace(container, "[]", 1)
            .replace(",", ":")
            .replace(" ", "")
        )
        try:
            result = [] == utils.eval_expr(newline, frame)
        except Exception:  # noqa
            result = False

        if not result:
            if additional_cause:
                return {"cause": cause + additional_cause, "suggest": hint}
            return {"cause": cause + "\n" + additional_cause, "suggest": hint}

        hint = _("Did you mean `{line}`?\n").format(
            line=container + newline.replace("[]", "", 1)
        )
        cause += "\n" + _("Perhaps you meant `{line}`.\n").format(
            line=container + newline.replace("[]", "", 1)
        )
        return {"cause": cause + "\n" + additional_cause, "suggest": hint}

    names = find_possible_integers(index_type, frame, tb_data.bad_line)
    if len(names) == 1:  # This should usually be the case
        more_cause, hint = forgot_to_convert_name_to_int(names[0])
        cause += "\n" + more_cause
        return {"cause": cause} if hint is None else {"cause": cause, "suggest": hint}
    if additional_cause:
        return {"cause": cause + additional_cause, "suggest": hint}
    return {"cause": cause}


@parser._add
def slice_indices_must_be_integers_or_none(
    message: str, _tb_data: TracebackData
) -> CauseInfo:
    if message != (
        "slice indices must be integers or None or have an __index__ method"
    ):
        return {}

    cause = _(
        "When using a slice to extract a range of elements\n"
        "from a sequence, that is something like\n"
        "`[start:stop]` or `[start:stop:step]`\n"
        "each of `start`, `stop`, `step` must be either an integer, `None`,\n"
        "or possibly some other object having an `__index__` method.\n"
    )
    return {"cause": cause}


@parser._add
def unhashable_type(message: str, _tb_data: TracebackData) -> CauseInfo:
    pattern = re.compile(r"unhashable type: '(.*)'")
    match = re.search(pattern, message)
    if match is None:
        return {}

    cause = _(
        "Only hashable objects can be used\n"
        "as elements of `set` or keys of `dict`.\n"
        "Hashable objects are objects that do not change value\n"
        "once they have been created."
    )

    original = match[1]
    replacements = {"list": "tuple", "set": "frozenset"}
    if original in replacements:
        cause += _(
            "Instead of using {original}, consider using {replacement}.\n"
        ).format(
            original=convert_type(original),
            replacement=convert_type(replacements[original]),
        )

    return {"cause": cause}


@parser._add
def object_is_not_subscriptable(message: str, tb_data: TracebackData) -> CauseInfo:
    pattern = re.compile(r"'(.*)' object is not subscriptable")
    match = re.search(pattern, message)
    if match is None:
        return {}

    frame = tb_data.exception_frame
    obj_type = match[1]
    if obj_type == "NoneType":
        none_type = _(
            "\nNote: `NoneType` means that the object has a value of `None`.\n"
        )
    else:
        none_type = ""

    cause = _(
        "Subscriptable objects are typically containers from which\n"
        "you can retrieve item using the notation `[...]`.\n"
    )

    # first, try to identify object
    all_objects = info_variables.get_all_objects(tb_data.bad_line, frame)
    for name, obj in all_objects["name, obj"]:
        truncated = tb_data.bad_line.replace(name, "", 1).strip()
        if truncated.startswith("[") and truncated.endswith("]"):
            break
    else:
        cause += _(
            "Using this notation, you attempted to retrieve an item\n"
            "from an object of type `{obj_type}` which is not allowed.\n"
        ).format(obj_type=obj_type)
        return {"cause": cause + none_type}

    if callable(obj):
        arg = truncated[1:-1]
        if "," in arg:
            # list[1, 2, 3] --> list((1, 2, 3))
            try:
                if len(inspect.getfullargspec(obj).args) == 1:
                    arg = f"({arg})"
            except:  # noqa
                pass
        line = f"{name}({arg})"
        hint = _("Did you mean `{line}`?\n").format(line=line)
        cause += "\n" + _("Perhaps you meant to write `{line}`.\n").format(line=line)
        return {"cause": cause, "suggest": hint}

    cause += _(
        "Using this notation, you attempted to retrieve an item\n"
        "from `{name}`, an object of type `{obj_type}`. This is not allowed.\n"
    ).format(obj_type=obj_type, name=name)

    return {"cause": cause + none_type}


@parser._add
def argument_of_object_is_not_iterable(
    message: str, tb_data: TracebackData
) -> CauseInfo:
    """This is usually the result of checking if something is contained
    in an object, so the code would include '... in ...'."""
    pattern = re.compile(r"argument of type '(.*)' is not iterable")
    match = re.search(pattern, message)
    if match is None:
        return {}
    obj_type = match[1]
    # Suppose we have two objects of the same type, a and b.
    # For the expression:
    #    if a in b
    # we want to identify 'b' and not 'a'.
    if "in" in tb_data.bad_line:
        after_in = tb_data.bad_line.split(" in ", 1)[1]
    else:  # should never happen; see docstring
        after_in = tb_data.bad_line
    all_obj = info_variables.get_all_objects(after_in, tb_data.exception_frame)
    for obj_name, obj_type2 in all_obj["name, type"]:
        if obj_type2 == obj_type:
            break
    else:  # Using the info from the exception message
        obj_name = obj_type

    cause = _(
        "An iterable is an object capable of returning its members one at a time.\n"
        "Python containers (`list, tuple, dict`, etc.) are iterables.\n"
        "'{obj_name}' is not a container. A container is required here.\n"
    ).format(obj_name=obj_name)
    return {"cause": cause}


@parser._add
def object_is_not_iterable(message: str, _tb_data: TracebackData) -> CauseInfo:
    pattern = re.compile(r"'(.*)' object is not iterable")
    match = re.search(pattern, message)
    if match is None:
        return {}

    cause = _(
        "An iterable is an object capable of returning its members one at a time.\n"
        "Python containers (`list, tuple, dict`, etc.) are iterables.\n"
        "An iterable is required here.\n"
    )
    return {"cause": cause}


@parser._add
def cannot_unpack_non_iterable(message: str, _tb_data: TracebackData) -> CauseInfo:
    pattern = re.compile(r"cannot unpack non-iterable (.*) object")
    match = re.search(pattern, message)
    if match is None:
        return {}

    cause = _(  # reusing definition from elsewhere
        "Unpacking is a convenient way to assign a name,\n"
        "to each item of an iterable.\n"
    )
    cause += _(
        "An iterable is an object capable of returning its members one at a time.\n"
        "Python containers (`list, tuple, dict`, etc.) are iterables,\n"
        "but not objects of type `{obj_type}`.\n"
    ).format(obj_type=match[1])
    return {"cause": cause}


@parser._add
def cannot_convert_dictionary_update_sequence(
    message: str, tb_data: TracebackData
) -> CauseInfo:
    if "cannot convert dictionary update sequence element" not in message:
        return {}

    possible_cause = _(
        "{function} does not accept a sequence as an argument.\n"
        "Instead of writing `{line}`\n"
        "perhaps you should use the `dict.fromkeys()` method: `{new_line}`.\n"
    )
    possible_hint = _("Perhaps you need to use the `dict.fromkeys()` method.\n")

    bad_line = tb_data.bad_line
    if bad_line.startswith("dict("):
        cause = possible_cause.format(
            function="`dict()`",
            line=bad_line,
            new_line=bad_line.replace("dict(", "dict.fromkeys(", 1),
        )
        hint = possible_hint
    elif ".update(" in bad_line:
        cause = possible_cause.format(
            function="`dict.update()`",
            line=bad_line,
            new_line=bad_line.replace(".update(", ".update( dict.fromkeys(", 1) + " )",
        )
        hint = possible_hint
    else:
        return {}

    return {"cause": cause, "suggest": hint}


@parser._add
def builtin_callable_has_no_len(message: str, tb_data: TracebackData) -> CauseInfo:
    if message != "object of type 'builtin_function_or_method' has no len()":
        return {}

    frame = tb_data.exception_frame
    all_objects = info_variables.get_all_objects(tb_data.bad_line, frame)["name, obj"]
    for name, obj in all_objects:
        if name == "len":
            continue
        if str(obj).startswith("<built-in"):
            break
    else:
        return {}

    hint = _("Did you forget to call `{name}`?\n").format(name=name)
    cause = _(
        "I suspect that you forgot to add parentheses to call `{name}`.\n"
        "You might have meant to write:\n"
        "`{line}`\n"
    ).format(name=name, line=tb_data.bad_line.replace(name, name + "()"))
    return {"cause": cause, "suggest": hint}


@parser._add
def function_has_no_len(message: str, tb_data: TracebackData) -> CauseInfo:
    if message != "object of type 'function' has no len()":
        return {}

    frame = tb_data.exception_frame
    all_objects = info_variables.get_all_objects(tb_data.bad_line, frame)["name, obj"]
    for name, obj in all_objects:
        if name == "len":
            continue
        if str(obj).startswith("<function"):
            break
    else:
        return {}

    hint = _("Did you forget to call `{name}`?\n").format(name=name)
    cause = _(
        "I suspect that you forgot to add parentheses to call `{name}`.\n"
        "You might have meant to write:\n"
        "`{line}`\n"
    ).format(name=name, line=tb_data.bad_line.replace(name, name + "()"))
    return {"cause": cause, "suggest": hint}


@parser._add
def vars_arg_must_have_dict(message: str, tb_data: TracebackData) -> CauseInfo:
    if message != "vars() argument must have __dict__ attribute":
        return {}

    frame = tb_data.exception_frame
    cause = _(
        "The function `vars` is used to list the content of the\n"
        "`__dict__` attribute of an object.\n"
    )
    all_objects = info_variables.get_all_objects(tb_data.bad_line, frame)["name, obj"]
    if len(all_objects) == 2:
        for name, obj in all_objects:
            if name != "vars":
                if hasattr(obj, "__slots__"):
                    cause += _(
                        "Object `{name}` uses `__slots__` instead of `__dict__`.\n"
                    ).format(name=name)
                else:
                    cause += _(
                        "`{name}`, the argument of `vars`, is an object without such an attribute.\n"
                    ).format(name=name)

    return {"cause": cause}


@parser._add
def function_got_multiple_argument(message: str, tb_data: TracebackData) -> CauseInfo:
    pattern = r"(.*)\(\) got multiple values for argument '(.*)'"
    match = re.search(pattern, message)
    if not match:
        return {}

    frame = tb_data.exception_frame
    function_name = match[1]
    # Annoyingly, Python 3.10 inserts <locals> as part of the name of functions
    # defined locally, which is what we often do in unit tests.
    if ".<locals>." in function_name:
        function_name = function_name.split(".<locals>.")[1]
    argument = match[2]
    cause = _(
        "You have specified the value of argument `{argument}` more than once\n"
        "when calling the function named `{function}`.\n"
    )

    all_objects = info_variables.get_all_objects(tb_data.bad_line, frame)["name, obj"]
    for name, obj in all_objects:
        if (
            name == function_name
            or "." in name
            and function_name in repr(obj)  # method of object
        ):
            function = obj
            function_name = name
            break
    else:
        return {"cause": cause.format(argument=argument, function=function_name)}

    cause = cause.format(argument=argument, function=function_name)
    arguments = inspect.signature(function)
    if len(arguments.parameters) == 1:
        cause += _("This function has only one argument: `{arguments}`\n").format(
            function=function_name, arguments=str(arguments)[1:-1]
        )
    else:
        cause += _(
            "This function has the following arguments:\n`{arguments}`\n"
        ).format(function=function_name, arguments=str(arguments)[1:-1])
    return {"cause": cause}


@parser._add
def generator_has_no_len(message: str, tb_data: TracebackData) -> CauseInfo:
    if message != "object of type 'generator' has no len()":
        return {}
    cause = _(
        "I am guessing that you were trying to count the number of elements\n"
        "produced by a generator expression. You first need to capture them\n"
        "in a list:\n\n"
    )
    tokens = token_utils.get_significant_tokens(tb_data.bad_line)
    nb_open = sum(tok == "(" for tok in tokens)
    nb_close = sum(tok == ")" for tok in tokens)
    if (
        nb_open == nb_close
        and nb_open >= 1
        and tokens[0] == "len"
        and tokens[1] == "("
        and tokens[-1] == ")"
    ):
        tokens[1].string = "(["
        tokens[-1].string = "])"
        new_line = token_utils.untokenize(tokens)
    else:
        new_line = "len([...])"

    cause += _("    {new_line}\n").format(new_line=new_line)
    hint = _("You likely need to build a list first.\n")

    return {"cause": cause, "suggest": hint}
