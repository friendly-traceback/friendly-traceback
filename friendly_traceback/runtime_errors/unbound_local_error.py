"""UnboundLocalError cases"""

import builtins
import re

from .. import debug_helper, info_variables
from ..ft_gettext import current_lang
from ..message_parser import get_parser
from ..tb_data import TracebackData  # for type checking only
from ..typing_info import CauseInfo, SimilarNamesInfo  # for type checking only

parser = get_parser(UnboundLocalError)
_ = current_lang.translate


@parser._add
def local_variable_referenced(message: str, tb_data: TracebackData) -> CauseInfo:
    pattern = re.compile(r"local variable '(.*)' referenced before assignment")
    pattern3_11 = re.compile(
        r"cannot access local variable '(.*)'"
        + " where it is not associated with a value"
    )
    match = re.search(pattern, message)
    if not match:
        match = re.search(pattern3_11, message)
    if not match:
        return {}

    frame = tb_data.exception_frame
    unknown_name = match.group(1)
    basic_cause = _(
        "You're trying to use the name `{name}` identified by Python as being\n"
        "in the local scope of a function before having assigned it a value.\n"
    ).format(name=unknown_name)

    scopes = info_variables.get_definition_scope(unknown_name, frame)
    if not scopes:
        similar = info_variables.get_similar_names(unknown_name, frame)
        all_similar_locals = similar["locals"]
        if all_similar_locals:
            similar_locals = []
            for name in all_similar_locals:
                obj = info_variables.get_object_from_name(name, frame)
                # Usually, this error message will be because we have
                # something like:
                # unknown += ...
                # or equivalent. We make sure to not include similar
                # names that refer to functions, etc., which could
                # not be assigned a value.
                if hasattr(obj, "__add__"):
                    similar_locals.append(name)
            if similar_locals:
                first_guess = similar_locals[0]
                hint = _("Did you mean `{name}`?\n").format(name=first_guess)
                cause = format_similar_names(unknown_name, similar)
                return {"cause": cause, "suggest": hint}

    if "global" in scopes and "nonlocal" in scopes:
        cause = (
            basic_cause
            + "\n"
            + _(
                "The name `{var_name}` exists in both the global and nonlocal scope.\n"
                "This can be rather confusing and is not recommended.\n"
                "Depending on which variable you wanted to refer to, you needed to add either\n\n"
                "    global {var_name}\n\n"
                "or\n\n"
                "    nonlocal {var_name}\n\n"
                "as the first line inside your function.\n"
            ).format(var_name=unknown_name)
        )
        hint = _(
            "Did you forget to add either `global {var_name}` or \n"
            "`nonlocal {var_name}`?\n"
        ).format(var_name=unknown_name)
        return {"cause": cause, "suggest": hint}

    if "global" in scopes:
        scope = "global"
    elif "nonlocal" in scopes:
        scope = "nonlocal"
    elif unknown_name in dir(builtins):
        return {
            "cause": _(
                "`{name}` is a Python builtin function.\n"
                "You have tried to assign a value to `{name}` inside a function\n"
                "while also using its original meaning in the function.\n\n"
                "Note that it is generally not a good idea to give a local variable\n"
                "the same name as a Python builtin function (like `{name}`).\n"
            ).format(name=unknown_name)
        }
    else:  # pragma: no cover
        debug_helper.log("problem in local_variable_referenced().")
        debug_helper.log("We have found variables in scopes")
        debug_helper.log("yet not in global nor nonlocal.")
        return {}

    cause = (
        basic_cause
        + "\n"
        + _(
            "The name `{var_name}` exists in the {scope} scope.\n"
            "Perhaps the statement\n\n"
            "    {scope} {var_name}\n\n"
            "should have been included as the first line inside your function.\n"
        ).format(var_name=unknown_name, scope=scope)
    )
    hint = _("Did you forget to add `{scope} {var_name}`?\n").format(
        var_name=unknown_name, scope=scope
    )
    return {"cause": cause, "suggest": hint}


def format_similar_names(unknown_name: str, similar: SimilarNamesInfo) -> str:
    """This function formats the names that were found to be similar"""
    nb_similar_names = len(similar["locals"])
    if nb_similar_names == 1:
        return (
            _("The similar name `{name}` was found in the local scope. ").format(
                name=str(similar["locals"][0]).replace("'", "")
            )
            + "\n"
        )
    message = _(
        "Instead of writing `{name}`, perhaps you meant one of the following:\n"
    ).format(name=unknown_name)
    message += (
        _("*   Local scope: ") + str(similar["locals"])[1:-1].replace("'", "`") + "\n"
    )
    return message
