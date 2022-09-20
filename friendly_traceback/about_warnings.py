"""This module will expand later."""
import warnings

import executing

from .config import session
from .ft_gettext import current_lang
from .info_generic import get_generic_explanation

_ = current_lang.translate


def show_warning(message, category, filename, lineno, file=None, line=None):
    session.write_err(f"`{category.__name__}`: {message}\n")
    info = {}
    info["message"] = _("{name}: {message}\n").format(
        message=message, name=category.__name__
    )
    info["generic"] = get_generic_explanation(category)
    info["last_call_header"] = _("{name}: File '{filename}', line `{lineno}`\n").format(
        name=category.__name__, filename=filename, lineno=lineno
    )
    info["last_call_source"] = get_source(filename, lineno)
    session.saved_info.append(info)
    session.friendly_info.append(info)


def get_source(filename: str, lineno: int):
    new_lines = []
    try:
        source = executing.Source.for_filename(filename)
        statement = source.statements_at_line(lineno).pop()
        lines = source.lines[statement.lineno - 1 : statement.end_lineno]
        for number, line in enumerate(lines, start=statement.lineno):
            if number == lineno:
                new_lines.append(f"    -->{number}| {line}")
            else:
                new_lines.append(f"       {number}| {line}")
        return "\n".join(new_lines)
    except Exception:
        return _("        <'source unavailable'>")


warnings.showwarning = show_warning

# Ensure that warnings are not shown to the end user by default, as they could
# cause confusion.
# In interactive mode, this will be changed.
warnings.simplefilter("ignore")
