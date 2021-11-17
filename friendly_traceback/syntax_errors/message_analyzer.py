# type: ignore
"""
Collection of functions that examine SyntaxError messages and
return relevant information to users.
"""
import __future__

import ast
import re
import sys

from .. import debug_helper, utils
from ..ft_gettext import current_lang, please_report
from . import error_in_def, fixers, statement_analyzer, syntax_utils

MESSAGE_ANALYZERS = []
_ = current_lang.translate


def _assign_to_identifiers_only():
    return _("You can only assign objects to identifiers (variable names).\n")  # noqa


def _can_only_delete():
    return _(
        "You can only delete names of objects, or items in mutable containers\n"
        "such as `list`, `set`, or `dict`.\n"
    )


def _find_keyword(statement):
    # used in assign_to_keyword
    if statement.bad_token.is_keyword():
        return statement.bad_token
    else:  # something like name.constant = ?
        for tok in statement.tokens[statement.bad_token_index :]:
            if tok.is_keyword():
                return tok
        debug_helper.log(f"Case not covered: {statement.bad_line}")
        return None


def _what_kind_of_literal(literal):
    """Evaluates an expression to see if we can determine its type."""
    try:
        a = ast.literal_eval(literal)
    except Exception:  # noqa
        return None

    kinds = (
        (int, _("of type `int`")),
        (complex, _("of type `complex`")),
        (float, _("of type `float`")),
        (str, _("of type `str`")),
        (dict, _("of type `dict`")),
        (list, _("of type `list`")),
        (set, _("of type `set`")),
        (tuple, _("of type `tuple`")),
    )
    for kind, result in kinds:
        if isinstance(a, kind):
            return result

    debug_helper.log("New kind of literal" + str(a))  # pragma: no cover
    return None  # pragma: no cover


def _proper_decimal_or_octal_number(prev_str, bad_str):
    # Used in invalid_token() and  leading_zeros_in_decimal_integers()
    if not (
        set(prev_str).issubset("_0") and prev_str.startswith("0")
    ):  # pragma: no cover
        debug_helper.log("_proper_decimal_or_octal_number should not have been called")
        return {}

    if prev_str == "0" and set(bad_str).issubset("01234567_"):
        correct = "0o" + bad_str
        hint = _("Did you mean `{num}`?\n").format(num=correct)
        cause = _(
            "Perhaps you meant to write the octal number `{num}`\n"
            "and forgot the letter 'o', or perhaps you meant to write\n"
            "a decimal integer and did not know that it could not start with zeros.\n"
        ).format(num=correct)
        return {"cause": cause, "suggest": hint}

    if set(bad_str).issubset("0123456789_"):
        correct = bad_str.lstrip("_")
        hint = _("Did you mean `{num}`?\n").format(num=correct)
        cause = _(
            "Perhaps you meant to write the integer `{num}`\n"
            "and did not know that it could not start with zeros.\n"
        ).format(num=correct)
        return {"cause": cause, "suggest": hint}

    return {}  # pragma: no cover


def add_python_message(func):
    """A simple decorator that adds a function the the list of functions
    that process a message given by Python.
    """
    MESSAGE_ANALYZERS.append(func)

    # The following is not normally needed; however, for debugging purpose
    # we might wish to access the decorated function.
    def wrapper():
        return func()

    return wrapper


def analyze_message(message: str = "", statement=None):
    for case in MESSAGE_ANALYZERS:
        cause = case(message, statement)
        if cause:
            return cause
    return {}


@add_python_message
def assign_to_conditional_expression(message: str = "", _statement=None):
    if message not in (
        "can't assign to conditional expression",  # Python 3.6, 3.7
        "cannot assign to conditional expression",  # Python 3.8
    ):
        return {}

    cause = _(
        "On the left-hand side of an equal sign, you have a\n"
        "conditional expression instead of the name of a variable.\n"
        "A conditional expression has the following form:\n\n"
        "    variable = object if condition else other_object"
    )
    return {"cause": cause, "suggest": _assign_to_identifiers_only()}


@add_python_message
def assign_to_expression(message: str = "", _statement=None):
    if message != "cannot assign to expression":  # Python 3.10
        return {}

    cause = _(
        "On the left-hand side of an equal sign, you have\n"
        "an expression instead of the name of a variable.\n"
    )
    return {"cause": cause, "suggest": _assign_to_identifiers_only()}


@add_python_message
def assign_to_function_call(message: str = "", statement=None):
    if (
        message != "can't assign to function call"  # Python 3.6, 3.7
        and "cannot assign to function call" not in message
    ):
        # if message not in (
        #     "can't assign to function call",  # Python 3.6, 3.7
        #     "cannot assign to function call",  # Python 3.8
        # ):
        return {}

    hint = _assign_to_identifiers_only()

    fn_call = statement.bad_token.string + "(...)"
    line = statement.bad_line

    if line.count("=") != 1 or line.count("(") != line.count(")"):
        # we have something like  fn(a=1) = 2
        # or fn(a) = 1 = 2, etc., and we cannot determine what is a function
        # argument and what is the value assigned
        value = _("some value")
        cause = _(
            "You wrote an expression like\n\n"
            "    {fn_call} = {value}\n\n"
            "where `{fn_call}`, on the left-hand side of the equal sign, is\n"
            "a function call and not the name of a variable.\n"
        ).format(fn_call=fn_call, value=value)

        return {"cause": cause, "suggest": hint}

    info = line.split("=")
    fn_call = info[0].strip()
    value = info[1].strip()
    cause = _(
        "You wrote the expression\n\n"
        "    {fn_call} = {value}\n\n"
        "where `{fn_call}`, on the left-hand side of the equal sign, either is\n"
        "or includes a function call and is not simply the name of a variable.\n"
    ).format(fn_call=fn_call, value=value)
    return {"cause": cause, "suggest": hint}


@add_python_message
def assign_to_generator_expression(message: str = "", _statement=None):
    if message not in (
        "can't assign to generator expression",  # Python 3.6, 3.7
        "cannot assign to generator expression",  # Python 3.8
    ):
        return {}

    cause = _(
        "On the left-hand side of an equal sign, you have a\n"
        "generator expression instead of the name of a variable.\n"
    )
    return {"cause": cause, "suggest": _assign_to_identifiers_only()}


@add_python_message
def assign_to_f_expression(message: str = "", statement=None):
    if "cannot assign to f-string expression" in message:
        cause = _(
            "You wrote an expression that has the f-string `{fstring}`\n"
            "on the left-hand side of the equal sign.\n"
            "An f-string should only appear on the right-hand "
            "side of an equal sign.\n"
        ).format(fstring=statement.bad_token)
        return {"cause": cause, "suggest": _assign_to_identifiers_only()}
    return {}


@add_python_message
def assign_to_keyword(message: str = "", statement=None):
    if message not in (
        "can't assign to keyword",  # Python 3.6, 3.7
        "assignment to keyword",  # Python 3.6, 3.7
        "cannot assign to keyword",  # Python 3.8
        "cannot assign to None",  # Python 3.8
        "cannot assign to True",  # Python 3.8
        "cannot assign to False",  # Python 3.8
        "cannot assign to __debug__",  # Python 3.8
        "can't assign to Ellipsis",  # Python 3.6, 3.7
        "cannot assign to Ellipsis",  # Python 3.8
        "cannot use named assignment with True",  # Python 3.8
        "cannot use named assignment with False",  # Python 3.8
        "cannot use named assignment with None",  # Python 3.8
        "cannot use named assignment with Ellipsis",  # Python 3.8
        "cannot use assignment expressions with True",  # Python 3.8
        "cannot use assignment expressions with False",  # Python 3.8
        "cannot use assignment expressions with None",  # Python 3.8
        "cannot use assignment expressions with Ellipsis",  # Python 3.8
        "cannot assign to Ellipsis here. Maybe you meant '==' instead of '='?",
        "cannot assign to ellipsis here. Maybe you meant '==' instead of '='?",
    ):
        return {}

    for word in ["None", "True", "False", "__debug__", "Ellipsis", "ellipsis"]:
        if word in message:
            break
    else:
        word = _find_keyword(statement)
        if word is None:
            return {}

    hint = _("You cannot assign a value to `{keyword}`.\n").format(keyword=word)

    if word in ["Ellipsis", "ellipsis"]:
        hint = _("You cannot assign a value to the ellipsis symbol [`...`].\n")
        cause = _(
            "The ellipsis symbol `...` is a constant in Python;"
            "you cannot assign it a different value.\n"
        )
    elif word in ["None", "True", "False", "__debug__"]:
        cause = _(
            "`{keyword}` is a constant in Python; you cannot assign it a different value.\n"
        ).format(keyword=word)
    else:  # pragma: no cover
        debug_helper.log(f"Case not covered: {statement.bad_line}")
        cause = _(
            "You were trying to assign a value to the Python keyword `{keyword}`.\n"
            "This is not allowed.\n"
            "\n"
        ).format(keyword=word)
    return {"cause": cause, "suggest": hint}


def _assign_to_literal_in_for_loop(statement):
    # see assign_to_literal() below
    tokens = statement.tokens[0 : statement.bad_token_index]
    for tok in tokens[::-1]:
        if tok == "in":  # pragma: no cover
            debug_helper.log("New case for assign_to_literal")
            break
        elif tok == "for":
            cause = _(
                "A for loop must have the form:\n\n"
                "    for ... in sequence:\n\n"
                "where `...` must contain only identifiers (variable names)\n"
                "and not literals like `{bad_token}`.\n"
            ).format(bad_token=statement.bad_token)
            return {"cause": cause, "suggest": _assign_to_identifiers_only()}
    return {}


@add_python_message
def assign_to_literal(message: str = "", statement=None):
    if message not in (
        "can't assign to literal",  # Python 3.6, 3.7
        "cannot assign to literal",  # Python 3.8
        "cannot assign to set display",  # Python 3.8
        "cannot assign to dict display",  # Python 3.8
        "cannot assign to dict literal here. Maybe you meant '==' instead of '='?",  # 3.10
        "cannot assign to literal here. Maybe you meant '==' instead of '='?",  # 3.10
        "cannot assign to set display here. Maybe you meant '==' instead of '='?",  # 3.10
    ):
        return {}

    # This error can happen if we use a literal as an element of
    # a for loop; we take care of this case first.
    literal_in_for_loop = _assign_to_literal_in_for_loop(statement)
    if literal_in_for_loop:
        return literal_in_for_loop

    line = statement.bad_line.rstrip()
    parts = line.split("=")
    if len(parts) == 2:
        literal = parts[0].strip()
        name = parts[1].strip()
        if sys.version_info < (3, 8) and (
            literal.startswith("f'{") or literal.startswith('f"{')
        ):
            cause = _(
                "You wrote an expression that has the f-string `{fstring}`\n"
                "on the left-hand side of the equal sign.\n"
                "An f-string should only appear on the right-hand "
                "side of an equal sign.\n"
            ).format(fstring=statement.bad_token)
            return {"cause": cause}
    else:
        literal = None
        name = _("variable_name")

    if len(parts) == 2 and name.isidentifier():
        # fmt: off
        suggest = _(
            "Perhaps you meant to write:\n\n"
            "    {name} = {literal}\n"
            "\n"
        ).format(literal=literal, name=name)
        # fmt: on
        hint = _("Perhaps you meant to write `{name} = {literal}`").format(
            literal=literal, name=name
        )
    else:
        hint = _assign_to_identifiers_only()
        suggest = "\n" + hint

    # Impose the right type when we know it.
    if message == "cannot assign to set display":
        of_type = _what_kind_of_literal("{1}")
    elif message == "cannot assign to dict display":
        of_type = _what_kind_of_literal("{1:2}")
    else:
        of_type = _what_kind_of_literal(literal)

    if literal is None:
        literal = "..."
        of_type = ""

    cause = (
        _(
            "You wrote an expression like\n\n"
            "    {literal} = {name}\n"
            "where `{literal}`, on the left-hand side of the equal sign,\n"
            "is or includes an actual object {of_type}\n"
            "and is not simply the name of a variable.\n"
        ).format(literal=literal, name=name, of_type=of_type)
        + suggest
    )
    return {"cause": cause, "suggest": hint}


@add_python_message
def assign_to_operator(message: str = "", statement=None):
    bad_line = statement.bad_line.rstrip()
    if message not in (
        "can't assign to operator",  # Python 3.6, 3.7
        "cannot assign to operator",  # Python 3.8
        "cannot assign to expression here. Maybe you meant '==' instead of '='?",  # Python 3.10
    ):
        return {}

    cause = _(
        "You wrote an expression that includes some mathematical operations\n"
        "on the left-hand side of the equal sign which should be\n"
        "only used to assign a value to a variable.\n"
    )

    def _could_be_identifier(line):
        try:
            if "=" in line and "-" in line:
                lhs, *rhs = line.split("=")
                if "-" in lhs:
                    lhs = lhs.replace("-", "_").strip()
                    if lhs.isidentifier():
                        return lhs
            return ""
        except Exception as e:  # pragma: no cover
            debug_helper.log("Problem in could_be_identifier:" + str(e))
            return ""

    name = _could_be_identifier(bad_line)
    if name:
        hint = _("Did you mean `{name}`?\n").format(name=name)
        cause += _(
            "Perhaps you meant to write `{name}` instead of `{original}`\n"
        ).format(name=name, original=name.replace("_", "-"))
        return {"cause": cause, "suggest": hint}

    hint = _("Perhaps you needed `==` instead of `=`.\n")
    return {"cause": cause, "suggest": hint}


@add_python_message
def assign_to_yield_expression(message: str = "", _statement=None):
    if message not in (
        "can't assign to yield expression",
        "cannot assign to yield expression",
        "cannot assign to yield expression here. Maybe you meant '==' instead of '='?",
    ):
        return {}
    cause = _(
        "You wrote an expression that includes the `yield` keyword\n"
        "on the left-hand side of the equal sign.\n"
        "You cannot assign a value to such an expression.\n"
        "Note that, like the keyword `return`,\n"
        "`yield` can only be used inside a function.\n"
    )
    return {"cause": cause, "suggest": _assign_to_identifiers_only()}


@add_python_message
def assignment_cannot_rebind_inside_comprehension(message: str = "", _statement=None):
    if (
        "assignment expression cannot rebind comprehension iteration variable"
        not in message
    ):
        return {}

    var = message.split("'")[1]
    cause = _(
        "You are using the augmented assignment operator `:=` inside\n"
        "a comprehension to assign a value to the iteration variable `{var}`.\n"
        "This variable is meant to be used only inside the comprehension.\n"
        "The augmented assignment operator is normally used to assign a value\n"
        "to a variable so that the variable can be reused later.\n"
        "This is not possible for variable `{var}`.\n"
    ).format(var=var)
    return {"cause": cause}


@add_python_message
def assignment_cannot_rebind_inside_comprehension_inner_loop(
    message: str = "", _statement=None
):
    if (
        "comprehension inner loop cannot rebind assignment expression target"
        not in message
    ):
        return {}

    var = message.split("'")[1]
    cause = _(
        "You are using the augmented assignment operator `:=` inside\n"
        "a comprehension to assign a value to the iteration variable `{var}`.\n"
        "This variable is meant to be used only inside the comprehension.\n"
        "The augmented assignment operator is normally used to assign a value\n"
        "to a variable so that the variable can be reused later.\n"
        "This is not possible for variable `{var}`.\n"
    ).format(var=var)
    return {"cause": cause}


@add_python_message
def annotated_name_cannot_be_global(message: str = "", _statement=None):
    pattern1 = re.compile(r"annotated name '(.)' can't be global")
    match = re.search(pattern1, message)
    if not match:
        return {}
    cause = _(
        "The object named `{name}` is defined with type annotation\n"
        "as a local variable. It cannot be declared to be a global variable.\n"
    ).format(name=match.group(1))

    return {"cause": cause}


@add_python_message
def augmented_assignment_with_literal(message: str = "", statement=None):
    if message != "cannot use assignment expressions with literal":
        return {}

    cause = _(
        "You cannot use the augmented assignment operator `:=`,\n"
        "sometimes called the walrus operator, with literals like `{bad_token}`.\n"
        "You can only assign objects to identifiers (variable names).\n"
    ).format(bad_token=statement.bad_token)
    return {"cause": cause, "suggest": _assign_to_identifiers_only()}


@add_python_message
def both_nonlocal_and_global(message: str = "", statement=None):
    if "is nonlocal and global" in message:
        cause = _(
            "You declared `{name}` as being both a global and nonlocal variable.\n"
            "A variable can be global, or nonlocal, but not both at the same time.\n"
        ).format(name=statement.next_token)
        return {"cause": cause}
    return {}


@add_python_message
def bracket_was_expected(message: str = "", statement=None):
    pattern = re.compile("'(.)' was never closed")  # new in Python 3.10
    match = re.search(pattern, message)
    if not match:
        return {}

    cause = _("Python tells us that the {bracket} was never closed.\n").format(
        bracket=syntax_utils.name_bracket(match.group(1))
    )
    hint = _("The {bracket} was never closed.\n").format(
        bracket=syntax_utils.name_bracket(match.group(1))
    )
    rephrased_cause = statement_analyzer.unclosed_bracket(statement)
    if rephrased_cause:
        cause = rephrased_cause["cause"]
    return {"cause": cause, "suggest": hint}


@add_python_message
def break_outside_loop(message: str = "", _statement=None):
    if "'break' outside loop" in message:
        cause = _(
            "The Python keyword `break` can only be used "
            "inside a `for` loop or inside a `while` loop.\n"
        )
        return {"cause": cause}
    return {}


@add_python_message
def cannot_assign_to_attribute(message: str = "", statement=None):
    if "cannot assign to attribute here" not in message:  # new in Python 3.10
        return {}
    hint = _("Perhaps you needed `==` instead of `=`.\n")
    cause = _(
        "You likely used an assignment operator `=` instead of an equality operator `==`.\n"
    )

    for tok in statement.tokens[statement.bad_token_index :]:
        if tok == "=":
            new_statement = fixers.replace_token(statement.statement_tokens, tok, "==")
            if fixers.check_statement(new_statement):
                cause += _(
                    "The following statement would not contain a syntax error:\n\n"
                    "    {new_statement}"
                ).format(new_statement=new_statement)

    return {"cause": cause, "suggest": hint}


@add_python_message
def cannot_delete_constant(message: str = "", statement=None):
    if message not in (
        "can't delete keyword",  # Python 3.6, 3.7
        "cannot delete None",
        "cannot delete True",
        "cannot delete False",
        "cannot delete __debug__",  # Python 3.10+
    ):
        return {}

    cause = (
        _("You cannot delete the constant `{constant}`.\n").format(
            constant=statement.bad_token
        )
        + _can_only_delete()
    )
    return {"cause": cause}


@add_python_message
def cannot_delete_expression(message: str = "", statement=None):
    if message not in (
        "can't delete operator",  # Python 3.6
        "cannot delete operator",  # Python 3.8
        "cannot delete expression",  # Python 3.10
    ):
        return {}
    if statement.first_token != "del":
        debug_helper.log(
            f"Expected first token to be 'del'; got {statement.first_token}"
        )
        cause = _("You cannot delete a Python expression.\n")
    else:
        expression = statement.bad_line[3:].strip()  # remove del
        cause = _("You cannot delete the expression `{expression}`.\n").format(
            expression=expression
        )
    hint = _can_only_delete()
    return {"cause": cause + _can_only_delete(), "suggest": hint}


@add_python_message
def cannot_delete_function_call(message: str = "", statement=None):
    if message not in (
        "can't delete function call",  # Python 3.6, 3.7
        "cannot delete function call",  # Python 3.8
    ):
        return {}

    line = statement.bad_line.rstrip()
    correct = "del {name}".format(name=statement.bad_token)
    cause = _(
        "You attempted to delete a function call\n\n"
        "    {line}\n"
        "instead of deleting the function's name\n\n"
        "    {correct}\n"
    ).format(line=line, correct=correct)
    return {"cause": cause}


@add_python_message
def cannot_delete_literal(message: str = "", statement=None):
    if message not in (
        "can't delete literal",  # Python 3.6, 3.7
        "cannot delete literal",
    ):
        return {}

    cause = (
        _("You cannot delete the literal `{literal}`.\n").format(
            literal=statement.bad_token
        )
        + _can_only_delete()
    )
    return {"cause": cause}


@add_python_message
def cannot_delete_named_expression(message: str = "", statement=None):
    if message not in ("cannot delete named expression",):  # Python 3.8 +
        return {}
    if statement.first_token != "del":
        debug_helper.log(
            f"Expected first token to be 'del'; got {statement.first_token}"
        )
        cause = _("You cannot delete a Python expression.\n")
    else:
        expression = statement.bad_line[3:].strip()  # remove del
        cause = _("You cannot delete the named expression `{expression}`.\n").format(
            expression=expression
        )
    hint = _can_only_delete()
    return {"cause": cause + _can_only_delete(), "suggest": hint}


@add_python_message
def cannot_use_starred_expression(message: str = "", statement=None):
    if message not in [
        "can't use starred expression here",
        "cannot use starred expression here",
        "cannot delete starred",
    ]:
        return {}

    cause = _(
        "The star operator `*` is interpreted to mean that\n"
        "iterable unpacking is to be used to assign a name\n"
        "to each item of an iterable, which does not make sense here.\n"
    )
    if statement.first_token == "del":
        cause += _can_only_delete()
    elif (
        len(statement.tokens) > statement.bad_token_index + 2
        and statement.prev_token == "("
        and statement.next_token.is_identifier()
        and statement.tokens[statement.bad_token_index + 2] == ")"
        and sys.version_info >= (3, 9)
    ):
        cause += "\n" + _(
            "It looks like you surrounded a starred name by parentheses.\n"
            "This was not considered a SyntaxError before Python version 3.9.\n"
        )

    return {"cause": cause}


@add_python_message
def cannot_delete_something_else(message: str = "", statement=None):
    if not message.startswith("cannot delete"):
        return {}
    return {"cause": _can_only_delete()}


@add_python_message
def colon_expected(message: str = "", statement=None):
    if message != "expected ':'":  # new in Python 3.10
        return {}

    # Try to be consistent with older versions
    cause = statement_analyzer.missing_colon(statement)
    if cause:
        return cause

    # That did not work, so we try something else
    hint = _("Did you forget a colon?\n")
    cause = _("Python expected a colon at the position indicated.\n")

    new_statement = fixers.replace_token(
        statement.statement_tokens, statement.bad_token, ":"
    )
    if fixers.check_statement(new_statement):
        cause += _("You wrote `{bad}` instead of a colon.\n").format(
            bad=statement.bad_token
        )
        return {"cause": cause, "suggest": hint}

    new_statement = fixers.modify_token(
        statement.statement_tokens, statement.bad_token, append=":"
    )
    if fixers.check_statement(new_statement):  # pragma: no cover
        debug_helper.log("New case for colon_expected.")
        return {"cause": cause, "suggest": hint}

    return {}


@add_python_message
def colon_missing_after_dict_key(message: str = "", _statement=None):
    if message != "':' expected after dictionary key":
        return {}
    cause = _(
        "It looks like the error occurred as you were writing a Python dict.\n"
        "Perhaps you wrote a dict key without writing the corresponding value.\n"
    )
    hint = _("Did you forget to write a dict value?\n")
    return {"cause": cause, "suggest": hint}


@add_python_message
def continue_outside_loop(message: str = "", _statement=None):
    if "'continue' not properly in loop" in message:
        cause = _(
            "The Python keyword `continue` can only be used "
            "inside a `for` loop or inside a `while` loop.\n"
        )
        return {"cause": cause}
    return {}


@add_python_message
def duplicate_argument_in_function_definition(message: str = "", _statement=None):
    if "duplicate argument" in message and "function definition" in message:
        name = message.split("'")[1]
        cause = _(
            "You have defined a function repeating the keyword argument\n\n"
            "    {name}\n"
            "twice; each keyword argument should appear only once"
            " in a function definition.\n"
        ).format(name=name)
        return {"cause": cause}
    return {}


@add_python_message
def else_after_if(message: str = "", _statement=None):
    if message != "expected 'else' after 'if' expression":
        return {}

    hint = _("Did you forget to add `else`?\n")
    cause = _("An `else some_value` clause was expected after the `if` expression.\n")
    return {"cause": cause, "suggest": hint}


@add_python_message
def eof_unclosed_triple_quoted(message: str = "", _statement=None):
    if not (
        message == "EOF while scanning triple-quoted string literal"
        or "unterminated triple-quoted string literal" in message
    ):
        return {}

    cause = _(
        "You started writing a triple-quoted string but never wrote\n"
        "the triple quotes needed to end the string.\n"
    )

    return {"cause": cause}


@add_python_message
def eol_while_scanning_string_literal(message: str = "", statement=None):
    if (
        "EOL while scanning string literal" in message
        or "unterminated string literal" in message  # Python 3.10
    ):
        hint = _("Did you forget a closing quote?\n")
        cause = _(
            "You started writing a string with a single or double quote\n"
            "but never ended the string with another quote on that line.\n"
        )
        # skipcq: PYL-R1714
        # second if case for Python 3.10
        if statement.prev_token == "\\" or statement.bad_line[-2] == "\\":
            cause += _(
                "Perhaps you meant to write the backslash character, `\\`\n"
                "as the last character in the string and forgot that you\n"
                "needed to escape it by writing two `\\` in a row.\n"
            )
            hint = _("Did you forget to escape a backslash character?\n")

        return {"cause": cause, "suggest": hint}
    return {}


@add_python_message
def expression_cannot_contain_assignment(message: str = "", statement=None):
    if (
        "expression cannot contain assignment, perhaps you meant" not in message
        and "keyword can't be an expression" not in message
    ):
        return {}
    if statement.bad_token.is_keyword() or statement.next_token.is_keyword():
        if statement.bad_token.is_keyword():
            keyword = statement.bad_token
        else:
            keyword = statement.next_token
        hint = _("You cannot assign a value to `{keyword}`.\n").format(keyword=keyword)
        cause = (
            _(
                "You likely called a function using the Python keyword"
                " `{keyword}` as an argument:\n\n"
                "    a_function({keyword}=something) \n\n"
                "which Python interpreted as trying to assign a value to a Python keyword.\n"
                "\n"
            ).format(keyword=keyword)
            + hint
        )
        return {"cause": cause, "suggest": hint}

    cause = _(
        "You likely called a function with a named argument:\n\n"
        "    a_function(invalid=something) \n\n"
        "where `invalid` is not a valid variable name in Python\n"
        "either because it starts with a number, or is a string,\n"
        "or contains a period, etc.\n"
    )
    return {"cause": cause}


@add_python_message
def expression_missing_after_dict_key_and_colon(message: str = "", _statement=None):
    if message != "expression expected after dictionary key and ':'":
        return {}
    cause = _(
        "It looks like the error occurred as you were writing a Python dict.\n"
        "Perhaps you forgot to write a value after a colon.\n"
    )
    hint = _("Did you forget to write a dict value?\n")
    return {"cause": cause, "suggest": hint}


@add_python_message
def f_string_backslash(message: str = "", _statement=None):
    if message != "f-string expression part cannot include a backslash":
        return {}

    cause = _(
        "You have written an f-string whose content `{...}`\n"
        "includes a backslash; this is not allowed.\n"
        "Perhaps you can replace the part that contains a backslash by\n"
        "some variable. For example, suppose that you have an f-string like:\n\n"
        "    f\"{... 'hello\\n' ...}\"\n\n"
        "you could write this as\n\n"
        "    hello = 'hello\\n'\n"
        '    f"{... hello ...}"\n'
    )
    return {"cause": cause}


@add_python_message
def f_string_curly_not_allowed(message: str = "", _statement=None):
    if message != "f-string: single '}' is not allowed":
        return {}
    cause = _(
        "You have written an f-string which has an unmatched `}`.\n"
        "If you want to print a single `}`, you need to write `}}` in the f-string;\n"
        "otherwise, you need to add an opening `{`.\n"
    )
    return {"cause": cause}


@add_python_message
def f_string_expecting_curly(message: str = "", _statement=None):
    if message != "f-string: expecting '}'":
        return {}
    cause = _(
        "You have written an f-string which has an unmatched `{`.\n"
        "If you want to print a single `{`, you need to write `{{` in the f-string;\n"
        "otherwise, you need to add a closing `}`.\n"
    )
    return {"cause": cause}


@add_python_message
def forgot_paren_around_comprehension(message: str = "", _statement=None):
    # Python 3.10+
    if message != "did you forget parentheses around the comprehension target?":
        return {}

    # message same as from statement_analyzer.comprehension_condition_or_tuple

    cause_tuple = _(
        "I am guessing that you were writing a comprehension or a generator expression\n"
        "and forgot to include parentheses around tuples.\n"
        "As an example, instead of writing\n\n"
        "    [i, i**2 for i in range(10)]\n\n"
        "you would need to write\n\n"
        "    [(i, i**2) for i in range(10)]\n\n"
    )
    hint = _("Did you forget parentheses?\n")
    return {"cause": cause_tuple, "suggest": hint}


@add_python_message
def from__future__at_begin(message: str = "", _statement=None):
    if message != "from __future__ imports must occur at the beginning of the file":
        return {}

    cause = _(
        "A `from __future__ import` statement changes the way Python\n"
        "interprets the code in a file.\n"
        "It must appear at the beginning of the file."
    )
    return {"cause": cause}


@add_python_message
def from__future__not_defined(message: str = "", _statement=None):
    pattern = re.compile(r"future feature (.*) is not defined")
    match = re.search(pattern, message)
    if match is None:
        return {}

    names = __future__.all_feature_names
    available = _("The available features are `{names}`.\n").format(
        names=utils.list_to_string(names).replace(",", ",\n")
    )
    feature = match.group(1)
    if feature == "*":
        cause = _(
            "When using a `from __future__ import` statement,\n"
            "you must import specific named features.\n"
        )
        cause += "\n" + available
        return {"cause": cause}

    names = __future__.all_feature_names
    similar = utils.get_similar_words(feature, names)
    if similar:
        hint = _("Did you mean `{name}`?\n").format(name=similar[0])
        cause = _(
            "Instead of `{feature}`, perhaps you meant to import `{name}`.\n"
        ).format(feature=feature, name=similar[0])
        return {"cause": cause, "suggest": hint}

    cause = _("`{feature}` is not a valid feature of module `__future__`.\n").format(
        feature=feature
    )
    cause += "\n" + available
    return {"cause": cause}


@add_python_message
def generator_expression_must_be_parenthesized(message: str = "", _statement=None):
    if "Generator expression must be parenthesized" not in message:
        return {}
    cause = _(
        "You are using a generator expression, something of the form\n\n"
        "    x for x in thing\n\n"
        "You must add parentheses enclosing that expression.\n"
    )
    return {"cause": cause}


@add_python_message
def import_braces(message: str = "", _statement=None):
    if message != "not a chance":
        return {}

    cause = _(
        "I suspect you wrote `from __future__ import braces` following\n"
        "someone else's suggestion. This will never work.\n\n"
        "Unlike other programming languages, Python's code block are defined by\n"
        "their indentation level, and not by using some curly braces, like `{...}`.\n"
    )
    return {"cause": cause}


@add_python_message
def invalid_character_in_identifier(message: str = "", statement=None):
    if "invalid character" not in message:
        return {}

    bad_character = statement.bad_token.string
    copy_paste = _("Did you use copy-paste?\n")
    python_says = _(
        "Python indicates that you used the unicode character"
        " `{bad_character}`\n"
        "which is not allowed.\n"
    ).format(bad_character=bad_character)

    potential_cause = syntax_utils.identify_bad_quote_char(
        bad_character, statement.bad_line
    )
    if potential_cause:
        potential_cause["cause"] = copy_paste + python_says + potential_cause["cause"]
        return potential_cause

    potential_cause = syntax_utils.identify_unicode_fraction(bad_character)
    if potential_cause:
        potential_cause["cause"] = copy_paste + python_says + potential_cause["cause"]
        return potential_cause

    return {"cause": python_says}


@add_python_message
def invalid_decimal_literal(message: str = "", statement=None):
    if message != "invalid decimal literal":  # new in Python 3.10
        return {}
    if not statement.highlighted_tokens or len(statement.highlighted_tokens) == 1:
        statement.highlighted_tokens = [statement.bad_token, statement.next_token]

    cause_prefix = _("Python tells us that you have written an invalid number.")
    however = _("However, I think that the problem might be the following.")

    if statement.first_token == "def" or (
        statement.first_token == "async" and statement.tokens[1] == "def"
    ):
        cause = error_in_def.analyze_def_statement(statement)
        if cause:
            cause["cause"] = cause_prefix + "\n" + however + "\n\n" + cause["cause"]
            return cause

    cause = statement_analyzer.invalid_name(statement)
    if cause:
        cause["cause"] = cause_prefix + "\n" + however + "\n\n" + cause["cause"]
        return cause

    if statement.next_token is not None and statement.bad_token.is_number():
        bad_character = statement.next_token.string
        potential_cause = syntax_utils.identify_bad_math_symbol(
            bad_character, statement.bad_line
        )
        if potential_cause:
            potential_cause["cause"] = (
                cause_prefix + "\n" + however + "\n\n" + potential_cause["cause"]
            )
            return potential_cause

        potential_cause = syntax_utils.identify_unicode_fraction(bad_character)
        if potential_cause:
            potential_cause["cause"] = (
                cause_prefix + "\n" + however + "\n\n" + potential_cause["cause"]
            )
            return potential_cause

    return {
        "cause": cause_prefix
        + "\n"
        + _("I have no suggestion to offer to fix this problem.\n")
        + please_report()
    }


@add_python_message
def invalid_double_star_operator(message: str = "", _statement=None):
    # Used to be "invalid syntax" prior to Python version 3.10
    if (
        message == "f-string: can't use double starred expression here"  # 3.10.0a7
        or message == "f-string: cannot use double starred expression here"  # future?
    ):
        cause = _(
            "The double star operator `**` is likely interpreted to mean that\n"
            "dict unpacking is to be used which is not allowed or does not make sense here.\n"
        )
        return {"cause": cause}

    return {}


@add_python_message
def invalid_hexadecimal_literal(message: str = "", statement=None):
    if message != "invalid hexadecimal literal":  # new in Python 3.10
        return {}
    if not statement.highlighted_tokens:
        statement.highlighted_tokens = [statement.bad_token, statement.next_token]

    if statement.first_token == "def" or (
        statement.first_token == "async" and statement.tokens[1] == "def"
    ):
        cause = error_in_def.analyze_def_statement(statement)
        if cause:
            return cause

    return statement_analyzer.invalid_hexadecimal(statement)


@add_python_message
def invalid_imaginary_literal(message: str = "", statement=None):
    if message != "invalid imaginary literal":  # new in Python 3.10
        return {}
    if not statement.highlighted_tokens or len(statement.highlighted_tokens) == 1:
        statement.highlighted_tokens = [statement.bad_token, statement.next_token]

    if statement.first_token == "def" or (
        statement.first_token == "async" and statement.tokens[1] == "def"
    ):
        cause = error_in_def.analyze_def_statement(statement)
        if cause:
            return cause

    return statement_analyzer.invalid_name(statement)


@add_python_message
def invalid_octal(message: str = "", statement=None):
    # Before Python 3.8, we'd only get "invalid syntax"
    if "in octal literal" not in message:
        return {}

    return statement_analyzer.invalid_octal(statement)


@add_python_message
def iterable_unpacking_cannot_be_used_in_comprehension(
    message: str = "", statement=None
):
    if message != "iterable unpacking cannot be used in comprehension":
        return {}
    cause = _(
        "You cannot use the `*` operator to unpack the iteration variable\n"
        "in a comprehension.\n"
    )
    if statement.bad_token == "*":
        bad_token = statement.bad_token
    elif statement.next_token == "*":
        bad_token = statement.next_token
    else:
        return {"cause": cause}
    new_statement = fixers.replace_token(statement.statement_tokens, bad_token, "")
    if fixers.check_statement(new_statement):
        cause += "\n" + _(
            "The following statement has no syntax error:\n\n    {statement}\n"
        ).format(statement=new_statement)
    return {"cause": cause}


@add_python_message
def invalid_token(message: str = "", statement=None):
    # Seen this for Python 3.6, 3.7 for would-be decimal number starting with zero.
    if message != "invalid token":
        return {}

    prev_str = statement.prev_token.string
    bad_str = statement.bad_token.string
    return _proper_decimal_or_octal_number(prev_str, bad_str)


@add_python_message
def keyword_argument_repeated(message: str = "", statement=None):
    if "keyword argument repeated" not in message:
        return {}
    cause = _(
        "You have called a function repeating the same keyword argument (`{arg}`).\n"
        "Each keyword argument should appear only once in a function call.\n"
    ).format(arg=statement.bad_token)
    return {"cause": cause}


@add_python_message
def leading_zeros_in_decimal_integers(message: str = "", statement=None):
    # Same as previous case but for Python 3.8+
    if not (
        message.startswith(
            "leading zeros in decimal integer literals are not permitted"
        )
    ):
        return {}

    if statement.bad_token.string[0] == "0":
        prev_str = statement.bad_token.string
        bad_str = statement.next_token.string
    else:
        prev_str = statement.prev_token.string
        bad_str = statement.bad_token.string
    return _proper_decimal_or_octal_number(prev_str, bad_str)


@add_python_message
def mismatched_parenthesis(message: str = "", statement=None):
    pattern1 = re.compile(
        r"closing parenthesis '(.)' does not match opening parenthesis '(.)' on line (\d+)"
    )
    match = re.search(pattern1, message)
    if match is None:
        lineno = None
        pattern2 = re.compile(
            r"closing parenthesis '(.)' does not match opening parenthesis '(.)'"
        )
        match = re.search(pattern2, message)
        if match is None:
            return {}
    else:
        lineno = match.group(3)

    opening = match.group(2)
    closing = match.group(1)

    cause = statement_analyzer.mismatched_brackets(statement)
    if cause:
        return cause

    debug_helper.log(
        "statement_analyzer.mismatched_brackets failed."
    )  # pragma: no cover
    if lineno is not None:  # pragma: no cover
        cause = _(
            "Python tells us that the closing `{closing}` on the last line shown\n"
            "does not match the opening `{opening}` on line {lineno}.\n\n"
        ).format(closing=closing, opening=opening, lineno=lineno)
    else:  # pragma: no cover
        cause = _(
            "Python tells us that the closing `{closing}` on the last line shown\n"
            "does not match the opening `{opening}`.\n\n"
        ).format(closing=closing, opening=opening)

    return {"cause": cause}  # pragma: no cover


@add_python_message
def named_arguments_must_follow_bare_star(message: str = "", _statement=None):
    # TODO: revise this as it can be greatly improved
    if message != "named arguments must follow bare *":
        return {}

    hint = _("Did you forget something after `*`?\n")
    cause = _(
        "Assuming you were defining a function, you need\n"
        "to replace `*` by either `*arguments` or\n"
        "by `*, named_argument=value`.\n"
    )
    return {"cause": cause, "suggest": hint}


@add_python_message
def name_assigned_to_prior_global(message: str = "", _statement=None):
    # something like: name 'p' is assigned to before global declaration
    if "is assigned to before global declaration" not in message:
        return {}

    name = message.split("'")[1]
    cause = _(
        "You assigned a value to the variable `{name}`\n"
        "before declaring it as a global variable.\n"
    ).format(name=name)
    return {"cause": cause}


@add_python_message
def name_assigned_to_prior_nonlocal(message: str = "", _statement=None):
    # something like: name 'p' is assigned to before global declaration
    if "is assigned to before nonlocal declaration" not in message:
        return {}

    name = message.split("'")[1]
    hint = _("Did you forget to add `nonlocal`?\n")
    cause = _(
        "You assigned a value to the variable `{name}`\n"
        "before declaring it as a nonlocal variable.\n"
    ).format(name=name)
    return {"cause": cause, "suggest": hint}


@add_python_message
def name_is_parameter_and_global(message: str = "", statement=None):
    # something like: name 'x' is parameter and global
    line = statement.entire_statement
    if "is parameter and global" not in message:
        return {}

    name = message.split("'")[1]
    if name in line and "global" in line:
        newline = line
    else:  # pragma: no cover
        debug_helper.log("New case for name_is_parameter_and_global")
        newline = f"global {name}"
    cause = _(
        "You are including the statement\n\n"
        "    {newline}\n\n"
        "indicating that `{name}` is a variable defined outside a function.\n"
        "You are also using the same `{name}` as an argument for that\n"
        "function, thus indicating that it should be variable known only\n"
        "inside that function, which is the contrary of what `global` implied.\n"
    ).format(newline=newline, name=name)
    return {"cause": cause}


@add_python_message
def name_is_parameter_and_nonlocal(message: str = "", _statement=None):
    if "is parameter and nonlocal" not in message:
        return {}

    name = message.split("'")[1]
    cause = _(
        "You used `{name}` as a parameter for a function\n"
        "before declaring it also as a nonlocal variable:\n"
        "`{name}` cannot be both at the same time.\n"
    ).format(name=name)
    return {"cause": cause}


@add_python_message
def name_used_prior_global(message: str = "", _statement=None):
    # something like: name 'p' is used prior to global declaration
    if "is used prior to global declaration" not in message:
        return {}

    name = message.split("'")[1]
    cause = _(
        "You used the variable `{name}`\nbefore declaring it as a global variable.\n"
    ).format(name=name)
    return {"cause": cause}


@add_python_message
def name_used_prior_nonlocal(message: str = "", _statement=None):
    # something like: name 'q' is used prior to nonlocal declaration
    if "is used prior to nonlocal declaration" not in message:
        return {}

    hint = _("Did you forget to write `nonlocal` first?\n")
    name = message.split("'")[1]
    cause = _(
        "You used the variable `{name}`\n"
        "before declaring it as a nonlocal variable.\n"
    ).format(name=name)
    return {"cause": cause, "suggest": hint}


@add_python_message
def no_binding_for_nonlocal(message: str = "", _statement=None):
    if "no binding for nonlocal" not in message:
        return {}

    name = message.split("'")[1]
    cause = _(
        "You declared the variable `{name}` as being a\n"
        "nonlocal variable but it cannot be found.\n"
    ).format(name=name)
    return {"cause": cause}


@add_python_message
def nonlocal_at_module_level(message: str = "", _statement=None):
    if "nonlocal declaration not allowed at module level" not in message:
        return {}
    cause = _(
        "You used the nonlocal keyword at a module level.\n"
        "The nonlocal keyword refers to a variable inside a function\n"
        "given a value outside that function."
    )
    return {"cause": cause}


@add_python_message
def non_default_arg_follows_default_arg(message: str = "", _statement=None):
    if "non-default argument follows default argument" not in message:
        return {}
    cause = _(
        "In Python, you can define functions with only positional arguments\n\n"
        "    def test(a, b, c): ...\n\n"
        "or only keyword arguments\n\n"
        "    def test(a=1, b=2, c=3): ...\n\n"
        "or a combination of the two\n\n"
        "    def test(a, b, c=3): ...\n\n"
        "but with the keyword arguments appearing after all the positional ones.\n"
        "According to Python, you used positional arguments after keyword ones.\n"
    )
    return {"cause": cause}


@add_python_message
def parens_around_exceptions(message: str = "", _statement=None):
    # keep in sync with statement_analyzer.parens_around_exceptions
    if message != "multiple exception types must be parenthesized":
        return {}

    hint = _("Did you forget parentheses?\n")
    cause = _(
        "I am guessing that you wanted to use an `except` statement\n"
        "with multiple exception types. If that is the case, you must\n"
        "surround them with parentheses.\n"
    )
    return {"cause": cause + "\n", "suggest": hint}


@add_python_message
def positional_argument_follows_keyword_arg(message: str = "", _statement=None):
    if "positional argument follows keyword argument" not in message:
        return {}
    cause = _(
        "In Python, you can call functions with only positional arguments\n\n"
        "    test(1, 2, 3)\n\n"
        "or only keyword arguments\n\n"
        "    test(a=1, b=2, c=3)\n\n"
        "or a combination of the two\n\n"
        "    test(1, 2, c=3)\n\n"
        "but with the keyword arguments appearing after all the positional ones.\n"
        "According to Python, you used positional arguments after keyword ones.\n"
    )
    return {"cause": cause}


@add_python_message
def python2_print(message: str = "", _statement=None):
    if not message.startswith(
        "Missing parentheses in call to 'print'. Did you mean print("
    ):
        return {}
    message = message[59:-2]
    possible_statement = f"print({message})"
    valid = fixers.check_statement(possible_statement)
    if not valid:
        if '"' not in message:
            message = f'"{message}"'
        elif "'" not in message:
            message = f"'{message}'"
        else:
            message = "'...'"
    if len(message) > 40:
        message = message[0:25] + " ... "
    cause = _(
        "Perhaps you need to type\n\n"
        "     print({message})\n\n"
        "In older version of Python, `print` was a keyword.\n"
        "Now, `print` is a function; you need to use parentheses to call it.\n"
    ).format(message=message)
    if not valid:
        cause += _("Note that arguments of `print` must be separated by commas.\n")
    hint = _("Did you mean `print({message})`?\n").format(message=message)
    return {"cause": cause, "suggest": hint}


@add_python_message
def return_outside_function(message: str = "", _statement=None):
    if message != "'return' outside function":
        return {}

    cause = _("You can only use a `return` statement inside a function or method.\n")
    return {"cause": cause}


@add_python_message
def star_assignment_target_must_be_list(message: str = "", _statement=None):
    if message != "starred assignment target must be in a list or tuple":
        return {}

    cause = _(
        "A star assignment must be of the form:\n\n    ... *name = list_or_tuple\n\n"
    )
    return {"cause": cause}


@add_python_message
def starred_expression_in_dict_value(message: str = "", statement=None):
    if message != "cannot use a starred expression in a dictionary value":
        return {}
    cause = _(
        "It looks like you tried to use a starred expression as a dict value;\n"
        "this is not allowed.\n"
    )
    if statement.bad_token == "*":
        bad_token = statement.bad_token
    else:
        return {"cause": cause}
    new_statement = fixers.replace_token(statement.statement_tokens, bad_token, "")
    if fixers.check_statement(new_statement):
        cause += "\n" + _(
            "The following statement has no syntax error:\n\n    {statement}\n"
        ).format(statement=new_statement)
    return {"cause": cause}


@add_python_message
def too_many_nested_blocks(message: str = "", _statement=None):
    if message != "too many statically nested blocks":
        return {}

    cause = _(
        "Your code is too complex for Python:\n"
        "you need to reduce the number of indented code blocks\n"
        "contained inside other code blocks.\n"
    )
    return {"cause": cause}


@add_python_message
def too_many_nested_parenthesis(message: str = "", _statement=None):
    if message != "too many nested parentheses":  # python 3.89+
        return {}

    cause = _(
        "Your code is too complex for Python:\n"
        "you need to reduce the number of parentheses\n"
        "contained inside other parentheses.\n"
    )
    return {"cause": cause}


@add_python_message
def trailing_comma_not_allowed(message: str = "", statement=None):
    # As far as I know, this is only in import statement; for example:
    # from math import sin, cos,
    if message != "trailing comma not allowed without surrounding parentheses":
        return {}

    cause = _(
        "Python indicates that you need to surround an expression\n"
        "ending with a comma by parentheses.\n"
    )
    perhaps_new_statement = lambda: _(  # noqa
        "Perhaps you meant to write\n\n`{new_statement}`\n"
    )

    bad_token = statement.bad_token
    if bad_token.is_keyword():
        new_statement = fixers.replace_token(statement.statement_tokens, bad_token, "")
        if fixers.check_statement(new_statement):
            cause += _(
                "However, I suspect that you wrote the keyword `{boolean}` by mistake.\n"
            ).format(boolean=bad_token)
            if bad_token.string in ["and", "or"]:
                cause += _(
                    "The Python keyword `{boolean}` can only be used for boolean expressions.\n"
                ).format(boolean=bad_token) + perhaps_new_statement().format(
                    new_statement=new_statement
                )
            else:
                cause += perhaps_new_statement().format(new_statement=new_statement)
            return {"cause": cause}
    elif bad_token == ",":  # Python 3.9+
        new_statement = fixers.replace_token(statement.statement_tokens, bad_token, "")
        if fixers.check_statement(new_statement):
            hint = _("Did you write a comma by mistake?\n")
            cause += _(
                "However, if you remove the last comma, there will be no syntax error.\n"
            )
            cause += perhaps_new_statement().format(new_statement=new_statement)
            return {"cause": cause, "suggest": hint}
    elif (
        statement.last_token == ","
    ):  # Python 3.6 - 3.8   (bad_token is at beginning of items)
        new_statement = fixers.replace_token(
            statement.statement_tokens, statement.last_token, ""
        )
        if fixers.check_statement(new_statement):
            hint = _("Did you write a comma by mistake?\n")
            cause += _(
                "However, if you remove the last comma, there will be no syntax error.\n"
            )
            cause += perhaps_new_statement().format(new_statement=new_statement)
            return {"cause": cause, "suggest": hint}

    debug_helper.log("new case to consider.")
    cause += _(
        "I have no additional suggestion to offer.\n"
        "Please feel free to report this case.\n"
    )

    return {"cause": cause}


@add_python_message
def unexpected_character_after_continuation(message: str = "", statement=None):
    if "unexpected character after line continuation character" not in message:
        return {}

    cause = _(
        "You are using the continuation character `\\` outside of a string,\n"
        "and it is followed by some other character(s).\n"
    )

    # For 3.9.0 and 3.10.0a6 (and possibly others), the new peg parser is
    # not giving us the correct location for the error; so we need to find it.
    bad_token = statement.bad_token
    if statement.prev_token != "\\":
        found_continuation = False
        for tok in statement.tokens:
            if tok == "\\":
                found_continuation = True
                continue

            if found_continuation:
                bad_token = tok
                break
        else:  # pragma: no cover
            debug_helper.log("Could not find bad token after continuation character.")

    if bad_token.is_number():
        number = bad_token
        cause += _(
            "I am guessing that you wanted to divide by the number {number} \n"
            "and wrote \\ instead of /."
        ).format(number=number)
        hint = _("Did you mean to divide by {number}?\n").format(number=number)
        return {"cause": cause, "suggest": hint}

    cause += _("I am guessing that you forgot to enclose some content in a string.\n")
    return {"cause": cause}


@add_python_message
def unexpected_eof_while_parsing(message: str = "", statement=None):
    if "unexpected EOF while parsing" not in message:
        return {}

    cause = _(
        "Python tells us that it reached the end of the file\n"
        "and expected more content.\n\n"
    )
    additional_cause = statement_analyzer.unclosed_bracket(statement)
    if additional_cause:
        cause += (
            _("I will attempt to be give a bit more information.\n\n")
            + additional_cause["cause"]
        )
    return {"cause": cause}


@add_python_message
def unicode_error(message: str = "", _statement=None):
    if "unicode error" not in message or "truncated \\UXX" not in message:
        return {}
    hint = _("Perhaps you need to double the backslash characters.\n")
    cause = _(
        "I suspect that you wrote a string that contains\n"
        "one backslash character, `\\` followed by an uppercase `U`\n"
        "and some more characters.\n"
        "Python likely interpreted this as indicating the beginning of\n"
        "what is known as an escape sequence for special unicode characters.\n"
        "To solve the problem, either write a so-called 'raw string'\n"
        "by adding the letter `r` as a prefix in\n"
        "front of the string, or replace `\\U`, by `\\\\U`.\n"
    )
    return {"cause": cause, "suggest": hint}


@add_python_message
def unmatched_parenthesis(message: str = "", statement=None):
    # Python 3.8
    if message == "unmatched ')'":
        bracket = syntax_utils.name_bracket(")")
    elif message == "unmatched ']'":
        bracket = syntax_utils.name_bracket("]")
    elif message == "unmatched '}'":
        bracket = syntax_utils.name_bracket("}")
    else:
        return {}
    cause = _(
        "The closing {bracket} on line {linenumber} does not match anything.\n"
    ).format(bracket=bracket, linenumber=statement.linenumber)
    return {"cause": cause}


@add_python_message
def unterminated_f_string(message: str = "", statement=None):
    if "f-string: unterminated string" not in message:
        return {}

    hint = _("Perhaps you forgot a closing quote.\n")
    # Depending on the Python version, the error points at the f-string itself
    # or the previous or the next token. We must guard against the case where
    # someone writes three strings in a row.
    for tok in [statement.prev_token, statement.bad_token, statement.next_token]:
        # escaped quotes are not allowed in f-strings, so we can simply count the number
        # of quotes of both kinds and look for an odd-number.
        if (
            tok.is_string()
            and tok.string.startswith("f")
            and (tok.string.count("'") % 2 or tok.string.count('"') % 2)
        ):
            fstring = tok
            break
    else:  # pragma: no cover
        debug_helper.log("Need to record case in unterminated_f_string")
        fstring = "<not found>"
    cause = _(
        "Inside the f-string `{fstring}`, \n"
        "you have another string, which starts with either a\n"
        "single quote (') or double quote (\"), without a matching closing one.\n"
    ).format(fstring=fstring)
    return {"cause": cause, "suggest": hint}


@add_python_message
def yield_outside_function(message: str = "", _statement=None):
    if message != "'yield' outside function":
        return {}

    cause = _("You can only use a `yield` statement inside a function.\n")
    return {"cause": cause}


@add_python_message
def you_found_it(message: str = "", statement=None):  # pragma: no cover
    if message != "You found it!" or statement.bad_token != "__peg_parser__":
        return {}

    cause = _(
        "This is a message that was added in Python 3.9\n"
        "to prevent redefining `__peg_parser__`.\n"
        "It should not be present in other versions.\n"
    )
    return {"cause": cause}
