import pydoc
import sys
try:
    import tkinter
except Exception:
    tkinter = False

import pytest

import friendly_traceback
from math import *

def test_Generic():
    try:
        this = something
    except NameError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    
    assert "NameError: name 'something' is not defined" in result
    if friendly_traceback.get_lang() == "en":
        assert "In your program, no object with the name `something` exists." in result
    if friendly_traceback._writing_docs:
        return result, message

x: 3

def test_Annotated_variable():
    try:
        y = x
    except NameError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    
    assert "NameError: name 'x' is not defined" in result
    if friendly_traceback.get_lang() == "en":
        assert "x = 3" in result
    if friendly_traceback._writing_docs:
        return result, message

alphabet = 'abc'


def test_Synonym():
    try:
        a = i
    except NameError:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    
    assert "NameError: name 'i' is not defined" in result
    if friendly_traceback.get_lang() == "en":
        assert "Did you mean `1j`" in result

    try:
        a = j
    except NameError:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    
    assert "NameError: name 'j' is not defined" in result
    if friendly_traceback.get_lang() == "en":
        assert "Did you mean `1j`" in result

    nabs = 1
    try:
        x = babs(-1)
    except NameError as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    
    assert "NameError: name 'babs' is not defined" in result
    if friendly_traceback.get_lang() == "en":
        assert "perhaps you meant one of the following" in result

    try:
        alphabets
    except NameError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    if friendly_traceback.get_lang() == "en":
        assert "The similar name `alphabet` was found in the global scope" in result

    try:
        char
    except NameError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    if friendly_traceback.get_lang() == "en":
        assert "The Python builtin `chr` has a similar name." in result

    try:
        cost  # wrote from math import * above
    except NameError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    
    assert "NameError: name 'cost' is not defined" in result
    if friendly_traceback.get_lang() == "en":
        assert "perhaps you meant one of the following" in result
    if friendly_traceback._writing_docs:
        return result, message


def test_Missing_import():
    # Check to see if a module from the stdlib should have been
    # imported.
    try:
        Tkinter.frame
    except NameError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "NameError: name 'Tkinter' is not defined" in result
    if friendly_traceback.get_lang() == "en":
        assert "Perhaps you forgot to import `tkinter`" in result
        assert "module is `tkinter` and not `Tkinter`." in result

    # The following is for negative result
    try:
        unknown.attribute
    except NameError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "NameError: name 'unknown' is not defined" in result
    if friendly_traceback.get_lang() == "en":
        assert "I have no additional information for you." in result

    try:
        unicodedata.something
    except NameError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "NameError: name 'unicodedata' is not defined" in result
    if friendly_traceback.get_lang() == "en":
        assert "Perhaps you forgot to import `unicodedata`" in result
    if friendly_traceback._writing_docs:
        return result, message


def test_missing_import2():
    try:
        ABCMeta
    except NameError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "NameError: name 'ABCMeta' is not defined"
    if friendly_traceback.get_lang() == "en":
        assert "Perhaps you forgot to import `ABCMeta` from one of these modules." in result
    if friendly_traceback._writing_docs:
        return result, message


def test_missing_import3():
    try:
        AF_APPLETALK
    except NameError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "NameError: name 'AF_APPLETALK' is not defined" in result
    assert "from socket import AF_APPLETALK" in result
    if friendly_traceback._writing_docs:
        return result, message


def test_missing_import_from_other_1():
    friendly_traceback.add_other_module_names_synonyms({"plt": "matplotlib.pyplot"})
    try:
        plt.something
    except NameError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert "NameError: name 'plt' is not defined" in result
    assert "import matplotlib.pyplot as plt" in result
    if friendly_traceback._writing_docs:
        return result, message


def test_missing_import_from_other_2():
    friendly_traceback.add_other_attribute_names({"show": ["matplotlib.pyplot", "funny"] })
    try:
        show()
    except NameError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert "NameError: name 'show' is not defined" in result
    assert "matplotlib.pyplot" in result
    if friendly_traceback.get_lang() == "en":
        assert "`show` is a name found in the following modules:" in result
    if friendly_traceback._writing_docs:
        return result, message

def test_Free_variable_referenced():
    def outer():
        def inner():
            return var
        inner()
        var = 4

    try:
        outer()
    except NameError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert ("free variable 'var' referenced" in result
            or "cannot access free variable 'var'" in result)  # 3.11
    if friendly_traceback.get_lang() == "en":
        assert "that exists in an enclosing scope" in result
        assert "but has not yet been assigned a value." in result
    if friendly_traceback._writing_docs:
        return result, message


def test_Custom_name():
    try:
        python
    except NameError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "NameError: name 'python' is not defined" in result
    if friendly_traceback.get_lang() == "en":
        assert "You are already using Python!" in result
    if friendly_traceback._writing_docs:
        return result, message


def test_Missing_self_1():
    class Pet(object):
        # Inspired by a StackOverflow question
        def __init__(self, name=""):
            self.name = name
            self.toys = []

        def add_toy(self, toy=None):
            if toy is not None:
                self.toys.append(toy)
            return self.toys

        def __str__(self):
            # self at the wrong place
            toys_list = add_toy(  # ensure that it can see 'self' on following line
                                self, 'something')
            if self.toys:
                return "{} has the following toys: {}".format(self.name, toys_list)
            else:
                return "{} has no toys".format(self.name)

    a = Pet('Fido')
    try:
        str(a)
    except NameError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "NameError: name 'add_toy' is not defined" in result
    if friendly_traceback.get_lang() == "en":
        assert "Perhaps you should have written `self.add_toy" in result
    if friendly_traceback._writing_docs:
        return result, message


def test_Missing_self_2():
    class Pet(object):
        # Inspired by a StackOverflow question
        def __init__(self, name=""):
            self.name = name
            self.toys = []

        def add_toy(self, toy=None):
            if toy is not None:
                self.toys.append(toy)
            return self.toys

        def __str__(self):
            # Missing self.
            toys_list = add_toy('something')
            if self.toys:
                return "{} has the following toys: {}".format(self.name, toys_list)
            else:
                return "{} has no toys".format(self.name)

    a = Pet('Fido')
    try:
        str(a)
    except NameError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "NameError: name 'add_toy' is not defined" in result
    if friendly_traceback.get_lang() == "en":
        assert "Perhaps you should have written `self.add_toy`" in result
    if friendly_traceback._writing_docs:
        return result, message

@pytest.mark.skipif(not tkinter, reason="tkinter not present; likely MacOS")
def test_Missing_module_name():
    try:
        frame = Frame()
    except NameError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "NameError: name 'Frame' is not defined" in result
    if friendly_traceback.get_lang() == "en":
        assert "Perhaps you should have written `tkinter.Frame`" in result
    if friendly_traceback._writing_docs:
        return result, message


def test_special_keyword():
    # These are keyword that should appear on their own in a single line
    try:
        passs
    except NameError as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert "NameError: name 'passs' is not defined" in result
    if friendly_traceback.get_lang() == "en":
        assert "Did you mean `pass`" in result
    try:
        continuee
    except NameError as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert "NameError: name 'continuee' is not defined" in result
    if friendly_traceback.get_lang() == "en":
        assert "Did you mean `continue`" in result
    try:
        brek
    except NameError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert "NameError: name 'brek' is not defined" in result
    if friendly_traceback.get_lang() == "en":
        assert "Did you mean `break`" in result
    if friendly_traceback._writing_docs:
        return result, message


if __name__ == "__main__":
    print(test_Generic()[0])
