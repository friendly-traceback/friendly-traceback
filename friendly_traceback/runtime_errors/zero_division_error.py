from typing import SupportsInt, Union

from .. import debug_helper
from ..ft_gettext import current_lang
from ..message_parser import get_parser
from ..tb_data import TracebackData  # for type checking only
from ..typing_info import CauseInfo  # for type checking only

parser = get_parser(ZeroDivisionError)
_ = current_lang.translate


def expression_is_zero(
    expression: Union[str, bytes, SupportsInt], modulo: bool = False
) -> str:
    """Simpler message when the denominator is a literal 0."""
    try:
        if int(expression) == 0:
            if modulo:
                return _("Using the modulo operator, you are dividing by zero.\n")
            return _("You are dividing by zero.\n")
    except Exception:  # noqa
        return ""
    debug_helper.log("New case to consider for expression_is_zero")  # pragma: no cover


@parser._add
def division_by_zero(message: str, tb_data: TracebackData) -> CauseInfo:
    if message not in (
        "division by zero",
        "float division by zero",
        "complex division by zero",
    ):
        return {}

    expression = tb_data.bad_line
    if expression.count("/") == 1:
        expression = expression.split("/")[1]
        cause = expression_is_zero(expression)
        if not cause:
            cause = _(
                "You are dividing by the following term\n\n"
                "    {expression}\n\n"
                "which is equal to zero.\n"
            ).format(expression=expression)
    else:
        cause = expression_includes_division_by_zero(expression)
    return {"cause": cause}


def expression_includes_division_by_zero(expression):
    if not expression.strip():
        expression = _("<'expression not found'>")
    return _(
        "The following mathematical expression includes a division by zero:\n\n"
        "    {expression}\n"
    ).format(expression=expression)


@parser._add
def integer_division_or_modulo(message: str, tb_data: TracebackData) -> CauseInfo:
    if message not in ["integer division or modulo by zero", "integer modulo by zero"]:
        return {}
    expression = tb_data.bad_line
    nb_div = expression.count("//")
    nb_mod = expression.count("%")
    nb_divmod = expression.count("divmod")
    if nb_div and not nb_mod and not nb_divmod:
        if nb_div == 1:
            expression = expression.split("//")[1]
            cause = expression_is_zero(expression)
            if not cause:
                cause = _(
                    "You are dividing by the following term\n\n"
                    "    {expression}\n\n"
                    "which is equal to zero.\n"
                ).format(expression=expression)
        else:
            cause = expression_includes_division_by_zero(expression)
    elif nb_mod and not nb_div and not nb_divmod:
        if nb_mod == 1:
            expression = expression.split("%")[1]
            cause = expression_is_zero(expression, modulo=True)
            if not cause:
                cause = _(
                    "Using the modulo operator, you are dividing by the following term\n\n"
                    "    {expression}\n\n"
                    "which is equal to zero.\n"
                ).format(expression=expression)
        else:
            cause = expression_includes_division_by_zero(expression)
    elif nb_divmod and not nb_div and not nb_mod:
        cause = _("The second argument of the `divmod()` function is zero.\n")
    else:
        cause = expression_includes_division_by_zero(expression)

    return {"cause": cause}


@parser._add
def zero_negative_power(message: str, _tb_data: TracebackData) -> CauseInfo:
    if message != "0.0 cannot be raised to a negative power":
        return {}
    cause = _(
        "You are attempting to raise the number 0 to a negative power\n"
        "which is equivalent to dividing by zero.\n"
    )
    return {"cause": cause}


@parser._add
def float_modulo(message: str, tb_data: TracebackData) -> CauseInfo:
    if message != "float modulo":
        return {}
    expression = tb_data.bad_line
    if expression.count("%") == 1:
        expression = expression.split("%")[1]
        cause = expression_is_zero(expression, modulo=True)
        if not cause:
            cause = _(
                "Using the modulo operator, you are dividing by the following term\n\n"
                "    {expression}\n\n"
                "which is equal to zero.\n"
            ).format(expression=expression)
    else:
        if not expression.strip():
            expression = _("<'expression not found'>")
        cause = _(
            "The following mathematical expression includes a division by zero\n"
            "done using the modulo operator:\n\n"
            "    {expression}\n"
        ).format(expression=expression)

    return {"cause": cause}


@parser._add
def float_divmod(message: str, _tb_data: TracebackData) -> CauseInfo:
    if message != "float divmod()":
        debug_helper.log("new case to consider")  # pragma: no cover
        return {}  # pragma: no cover

    cause = _("The second argument of the `divmod()` function is equal to zero.\n")
    return {"cause": cause}
