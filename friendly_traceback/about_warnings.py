"""This module will expand later."""
import warnings

WARNINGS = {}


def show_warning(message, category, filename, lineno, file=None, line=None):
    new_warning = warnings.WarningMessage(
        message, category, filename, lineno, file, line
    )
    print(f"{category.__name__}: {filename}, line: {lineno}")
    WARNINGS[len(WARNINGS) + 1] = new_warning


warnings.showwarning = show_warning

# Ensure that warnings are not shown to the end user by default, as they could
# cause confusion.
# In interactive mode, this will be changed.
warnings.simplefilter("ignore")
