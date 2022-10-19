# Used to add names and attribute information from third-party packages
# when extending friendly_traceback; for example, by when using friendly_pandas.

modules = set()  # noqa
# example: modules.add("numpy")

module_synonyms = {}  # noqa
# example: module_synonyms["np"] = "numpy"
# this will lead to a suggestion:
# Perhaps you meant to write `import numpy as np`

attribute_names = {}  # noqa
# For example attribute_names["read_excel"] = ["pandas"]
