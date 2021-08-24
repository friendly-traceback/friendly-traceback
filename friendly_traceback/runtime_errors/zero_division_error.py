from types import FrameType
from typing import SupportsInt, Union

from .. import debug_helper
from ..core import TracebackData
from ..ft_gettext import current_lang
from ..typing import CauseInfo
from ..utils import RuntimeMessageParser

parser = RuntimeMessageParser()
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


@parser.add
def division_by_zero(
    message: str, _frame: FrameType, tb_data: TracebackData
) -> CauseInfo:
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
        cause = _(
            "The following mathematical expression includes a division by zero:\n\n"
            "    {expression}\n"
        ).format(expression=expression)
    return {"cause": cause}


@parser.add
def integer_or_modulo(
    message: str, _frame: FrameType, tb_data: TracebackData
) -> CauseInfo:
    if message != "integer division or modulo by zero":
        return {}
    expression = tb_data.bad_line
    nb_div = expression.count("//")
    nb_mod = expression.count("%")
    nb_divmod = expression.count("divmod")
    if nb_div and not (nb_mod or nb_divmod):
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
            cause = _(
                "The following mathematical expression includes a division by zero:\n\n"
                "    {expression}\n"
            ).format(expression=expression)
    elif nb_mod and not (nb_div or nb_divmod):
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
            cause = _(
                "The following mathematical expression includes a division by zero:\n\n"
                "    {expression}\n"
            ).format(expression=expression)
    elif nb_divmod and not (nb_div or nb_mod):
        cause = _("The second argument of the `divmod()` function is zero.\n")
    else:
        cause = _(
            "The following mathematical expression includes a division by zero:\n\n"
            "    {expression}\n"
        ).format(expression=expression)

    return {"cause": cause}


@parser.add
def zero_negative_power(
    message: str, _frame: FrameType, _tb_data: TracebackData
) -> CauseInfo:
    if message != "0.0 cannot be raised to a negative power":
        return {}
    cause = _(
        "You are attempting to raise the number 0 to a negative power\n"
        "which is equivalent to dividing by zero.\n"
    )
    return {"cause": cause}


@parser.add
def float_modulo(message: str, _frame: FrameType, tb_data: TracebackData) -> CauseInfo:
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
        cause = _(
            "The following mathematical expression includes a division by zero\n"
            "done using the modulo operator:\n\n"
            "    {expression}\n"
        ).format(expression=expression)

    return {"cause": cause}


@parser.add
def float_divmod(message: str, _frame: FrameType, _tb_data: TracebackData) -> CauseInfo:
    if message != "float divmod()":
        debug_helper.log("new case to consider")  # pragma: no cover
        return {}  # pragma: no cover

    cause = _("The second argument of the `divmod()` function is equal to zero.\n")
    return {"cause": cause}
