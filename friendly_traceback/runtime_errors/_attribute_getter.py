"""Helper script to obtain a list of available attributes for each modules.

This is not meant to be imported anywhere.

The output is shown in the console. It should be saved in
modules_attributes.py located in this directory.
"""
import sys
from pprint import pprint

from stdlib_modules import names

all_attributes = {}
for mod_name in names:
    # List compiled with Python 3.9
    if mod_name in [
        "antigravity",  # has side-effects
        "binhex",  # deprecated
        "formatter",  # deprecated
        "imp",  # deprecated
        "parser",  # deprecated
        "symbol",  # deprecated
        "this",  # has side-effects
    ]:
        continue
    try:
        imported_mod = __import__(mod_name)
    except ImportError:
        continue
    for attr_name in dir(imported_mod):
        if attr_name.startswith("_") or len(attr_name) == 1:
            continue
        elif attr_name in names and attr_name != mod_name:
            continue
        elif attr_name in all_attributes:
            all_attributes[attr_name].append(mod_name)
        else:
            all_attributes[attr_name] = [mod_name]

with open("modules_attributes.py", "w") as f:
    f.write(f"# Created with {sys.version_info}\n")
    f.write("attribute_names = ")
    pprint(all_attributes, stream=f, indent=4)
