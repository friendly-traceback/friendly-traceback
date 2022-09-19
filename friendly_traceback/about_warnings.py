"""This module will expand later."""
import warnings

WARNINGS = {}

# For simplicity, we will use a subset of the same items
# that we used for a traceback info
# items_to_consider = [
#     "message",  #
#     "generic",  # <-- what()
#     "cause",  # <-- why()
#     "last_call_header",  # location; filename and lineno
#     "last_call_source",  # <-- where()
# ]


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
