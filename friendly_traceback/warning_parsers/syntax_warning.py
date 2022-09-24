import re

from ..about_warnings import get_warning_parser
from ..ft_gettext import current_lang
from ..info_variables import convert_type

parser = get_warning_parser(SyntaxWarning)
_ = current_lang.translate


@parser._add
def object_is_not_callable(message: str) -> dict:
    pattern = re.compile("'(.*)' object is not callable")
    match = re.match(pattern, message)
    if not match:
        return {}

    obj_type = match[1]
    if obj_type == "NoneType":
        none_type = _(
            "\nNote: `NoneType` means that the object has a value of `None`.\n"
        )
    else:
        none_type = ""

    cause = _(
        "Python indicates that you have an object of type `{obj_type}`,\n"
        "followed by something surrounded by parentheses, `(...)`,\n"
        "which Python took as an indication of a function call.\n"
        "Either the object of type `{obj_type}` was meant to be a function,\n"
        "or you forgot a comma before `(...)`.\n"
    ).format(obj_type=obj_type)

    return {"cause": cause + none_type}


@parser._add
def list_indices_must_be(message: str) -> dict:
    pattern = re.compile(r"(.*) indices must be integers or slices, not (.*);")
    match = re.search(pattern, message)
    if match is None:
        return {}

    container_type = match[1]
    index_type = match[2]
    cause = _(
        "You have {container_type} followed by square brackets, `[...]`.\n"
        "What is included between the square brackets, `[...]`,\n"
        "must be either an integer or a slice\n"
        "(`start:stop` or `start:stop:step`) \n"
        "and you have used {obj_type} instead.\n"
    ).format(
        container_type=convert_type(container_type), obj_type=convert_type(index_type)
    )

    return {"cause": cause}
