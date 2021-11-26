import re
from types import FrameType
from typing import Any, Tuple

from .. import debug_helper, info_variables, token_utils, utils
from ..core import TracebackData
from ..ft_gettext import current_lang
from ..typing_info import CauseInfo, SimilarNamesInfo
from ..utils import list_to_string
from . import stdlib_modules
from .modules_attributes import attribute_names

parser = utils.RuntimeMessageParser()
_ = current_lang.translate


def using_python() -> str:  # pragma: no cover
    return _("You are already using Python!")


# The following is also intended to be used in custom environments;
# we currently use it in Mu.  It is meant to recognize names that
# are intended as a single word command, or call to a function
# that does is not available in a given environment.
CUSTOM_NAMES = {"python": using_python, "python3": using_python}


def is_module_attribute(name):
    if name not in attribute_names:
        return ""
    names = attribute_names[name]
    if len(names) == 1:
        return _(
            "`{name}` is a name found in module `{mod}`.\n"
            "Perhaps you forgot to write\n\n    from {mod} import {name}\n"
        ).format(name=name, mod=names[0])
    return _(
        "`{name}` is a name found in the following modules from the standard library:\n"
        "{modules}.\n"
        "Perhaps you forgot to import `{name}` from one of these modules.\n"
    ).format(name=name, modules=list_to_string(names))


@parser.add
def free_variable_referenced(
    message: str, _frame: FrameType, _tb_data: TracebackData
) -> CauseInfo:
    pattern = re.compile(
        r"free variable '(.*)' referenced before assignment in enclosing scope"
    )
    pattern3_11 = re.compile(
        r"cannot access free variable '(.*)'"
        + " where it is not associated with a value in enclosing scope"
    )
    match = re.search(pattern, message)
    if not match:
        match = re.search(pattern3_11, message)
    if not match:
        return {}

    unknown_name = match.group(1)
    cause = _(
        "In your program, `{var_name}` is an unknown name\n"
        "that exists in an enclosing scope,\n"
        "but has not yet been assigned a value.\n"
    ).format(var_name=unknown_name)
    return {"cause": cause}


@parser.add
def name_not_defined(
    message: str, frame: FrameType, tb_data: TracebackData
) -> CauseInfo:
    pattern = re.compile(r"name '(.*)' is not defined")
    match = re.search(pattern, message)
    if not match:
        return {}

    unknown_name = match.group(1)
    is_special_name = perhaps_special_name(unknown_name, tb_data)
    if is_special_name:
        return is_special_name

    cause = _("In your program, no object with the name `{var_name}` exists.\n").format(
        var_name=unknown_name
    )

    hint = ""
    known_module = is_stdlib_module(unknown_name, tb_data)
    if known_module:
        cause = known_module["cause"]
        hint = known_module["suggest"]

    type_hint = info_variables.name_has_type_hint(unknown_name, frame)
    similar = info_variables.get_similar_names(unknown_name, frame)
    if "lowercase" in known_module:
        hint = _("Did you mean `{name}`?\n").format(name=unknown_name.lower())
    elif similar["best"] is not None:
        hint = _("Did you mean `{name}`?\n").format(name=similar["best"])
    elif type_hint:
        hint = _("Did you use a colon instead of an equal sign?\n")

    additional = type_hint + format_similar_names(unknown_name, similar)
    try:
        more, hint = missing_self(unknown_name, frame, tb_data, hint)
        if more:
            additional += "\n" + more
    except Exception as e:  # pragma: no cover
        debug_helper.log("Problem in name_not_defined()")
        debug_helper.log_error(e)

    forgot_import = is_module_attribute(unknown_name)
    if forgot_import:
        if additional:
            additional += "\n" + forgot_import
        else:
            additional = forgot_import
    if not additional:
        additional = _("I have no additional information for you.\n")

    explanation = {"cause": cause + additional}
    if not hint:
        return explanation
    explanation["suggest"] = hint
    return explanation


def perhaps_special_name(name: str, tb_data: TracebackData) -> CauseInfo:
    if name == "ꓺ":  # pragma: no cover
        return flipfloperator()
    if name == "__debug__" and tb_data.bad_line.startswith("del "):
        return delete_debug()
    if name in {"i", "j"}:
        hint = _("Did you mean `1j`?\n")
        cause = _(
            "In your program, no object with the name `{var_name}` exists.\n"
        ).format(var_name=name)
        cause += _(
            "However, sometimes `{name}` is intended to represent\n"
            "the square root of `-1` which is written as `1j` in Python.\n"
        ).format(name=name)
        return {"cause": cause, "suggest": hint}
    if name in CUSTOM_NAMES:
        bad_line = tb_data.bad_line.replace("(", "").replace(")", "").strip()
        if bad_line == name:
            cause = CUSTOM_NAMES[name]()
            return {"cause": cause, "suggest": cause}
    return {}


def delete_debug() -> CauseInfo:
    # https://bugs.python.org/issue45000
    hint = _("`__debug__` is a constant.\n")
    cause = _(
        "`__debug__` is a constant that cannot be deleted.\n"
        "In future Python versions, attempting to delete it will be a SyntaxError.\n"
    )
    return {"cause": cause, "suggest": hint}


def flipfloperator() -> CauseInfo:  # pragma: no cover
    hint = _("You must be a fan of PyConAu!\n")
    cause = _(
        "I am guessing that you tried to use (one of) the flipfloperators\n"
        "shown during the second Lightning Talk session of PyConAu 2018,\n"
        "but that you forgot to install the module from PyPI.\n\n"
        "#### Note that it is still a bad idea.\n"
    )
    return {"cause": cause, "suggest": hint}


def is_stdlib_module(name: str, tb_data: TracebackData) -> CauseInfo:
    """Determine if an unknown name is to be found in the Python standard library.
    We're looking for something like name.attribute"""
    # Some Python 2 libraries used names with uppercase letters.
    lowercase = name.lower()
    if name in stdlib_modules.names or lowercase in stdlib_modules.names:
        hint = _("Did you forget to import `{name}`?\n").format(name=lowercase)
        cause = (
            "\n"
            + _(
                "The name `{name}` is not defined in your program.\n"
                "Perhaps you forgot to import `{lowercase}` which is found\n"
                "in Python's standard library.\n"
            ).format(name=name, lowercase=lowercase)
            + "\n"
        )
        if name != lowercase:
            cause += (
                _(
                    "Note that the name of the module is `{lowercase}` and not `{name}`.\n"
                ).format(lowercase=lowercase, name=name)
                + "\n"
            )
            return {"cause": cause, "suggest": hint, "lowercase": True}
        return {"cause": cause, "suggest": hint}
    return {}


def format_similar_names(name: str, similar: SimilarNamesInfo) -> str:
    """This function formats the names that were found to be similar"""
    nb_similar_names = (
        len(similar["locals"]) + len(similar["globals"]) + len(similar["builtins"])
    )
    if nb_similar_names == 0:
        return ""

    found_local = _("The similar name `{name}` was found in the local scope.\n")
    found_global = _("The similar name `{name}` was found in the global scope.\n")
    builtin_similar = _("The Python builtin `{name}` has a similar name.\n")

    if nb_similar_names == 1:
        if similar["locals"]:
            return found_local.format(name=similar["locals"][0])
        if similar["globals"]:
            return found_global.format(name=similar["globals"][0])
        return builtin_similar.format(name=similar["builtins"][0])

    message = _(
        "Instead of writing `{name}`, perhaps you meant one of the following:\n"
    ).format(name=name)

    for scope, pre in (
        ("locals", _("*   Local scope: ")),
        ("globals", _("*   Global scope: ")),
        ("builtins", _("*   Python builtins: ")),
    ):
        if similar[scope]:
            message += pre + str(similar[scope])[1:-1].replace("'", "`") + "\n"

    return message


def missing_self(
    unknown_name: str, frame: FrameType, tb_data: TracebackData, hint: str
) -> Tuple[str, str]:
    """If the unknown name is referred to with no '.' before it,
    and is an attribute of a known object, perhaps 'self.'
    is missing."""
    message = ""
    try:
        bad_statement = utils.get_bad_statement(tb_data)
        tokens = token_utils.get_significant_tokens(bad_statement)
    except Exception:  # noqa  # pragma: no cover
        debug_helper.log(
            "Exception raised in missing_self() while trying to get tokens"
        )
        return message, hint

    if not tokens:  # pragma: no cover
        return message, hint

    prev_token = tokens[0]
    for index, token in enumerate(tokens):
        if token == unknown_name and prev_token != ".":
            break
        prev_token = token
    else:
        return message, hint

    first_arg_self = (
        len(tokens) > index + 3
        and tokens[index + 1] == "("
        and tokens[index + 2] == "self"
    )

    env = (("local", frame.f_locals), ("global", frame.f_globals))

    for scope, dict_ in env:
        names = info_variables.get_variables_in_frame_by_scope(frame, scope)
        dict_copy = dict(dict_)
        for name in names:
            if name in dict_copy:
                obj = dict_copy[name]
                known_attributes = dir(obj)
                if unknown_name in known_attributes:
                    return missing_self_cause(
                        name, unknown_name, obj, scope, first_arg_self, hint
                    )
    return message, hint


def missing_self_cause(
    name: str, unknown_name: str, obj: Any, scope: str, first_arg_self: bool, hint: str
) -> Tuple[str, str]:
    obj_repr = info_variables.simplify_repr(repr(obj), splitlines=False)
    if first_arg_self and name == "self":
        suggest = _("Did you write `self` at the wrong place?\n")
        message = _(
            "The {scope} object `{obj}`\n"
            "has an attribute named `{unknown_name}`.\n"
            "Perhaps you should have written `self.{unknown_name}(...`\n"
            "instead of `{unknown_name}(self, ...`.\n"
        ).format(scope=scope, obj=obj_repr, unknown_name=unknown_name)
    elif name == "self":
        suggest = _("Did you forget to add `self.`?\n")
        message = _(
            "A {scope} object, `{obj}`,\n"
            "has an attribute named `{unknown_name}`.\n"
            "Perhaps you should have written `self.{unknown_name}`\n"
            "instead of `{unknown_name}`.\n"
        ).format(scope=scope, obj=obj_repr, unknown_name=unknown_name)
    else:
        suggest = _("Did you forget to add `{name}.`?\n").format(name=name)
        message = _(
            "The {scope} object `{name}`\n"
            "has an attribute named `{unknown_name}`.\n"
            "Perhaps you should have written `{name}.{unknown_name}`\n"
            "instead of `{unknown_name}`.\n"
        ).format(scope=scope, name=name, unknown_name=unknown_name)

    hint += suggest
    return message, hint
