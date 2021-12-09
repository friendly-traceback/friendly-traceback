import sys

import friendly_traceback


def test_Short_tuple():
    a = (1, 2, 3)
    b = [1, 2, 3]
    try:
        print(a[3], b[2])
    except IndexError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    
    assert "IndexError: tuple index out of range" in result
    if friendly_traceback.get_lang() == "en":
        if sys.version_info < (3, 11):
            assert "The valid index values of" in result
        else:
            print("skip for Python 3.11")
    return result, message


def test_Long_list():
    a = list(range(40))
    b = tuple(range(50))
    try:
        print(a[60], b[0])
    except IndexError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "IndexError: list index out of range" in result
    if friendly_traceback.get_lang() == "en":
        if sys.version_info < (3, 11):
            assert "The valid index values of" in result
        else:
            print("skip for Python 3.11")
    return result, message

def test_Empty():
    a = []
    try:
        c = a[1]
    except IndexError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "IndexError: list index out of range" in result
    if friendly_traceback.get_lang() == "en":
        if sys.version_info < (3, 11):
            assert "contains no item" in result
        else:
            print("skip for Python 3.11")
    return result, message


def test_Assignment():
    a = list(range(10))
    b = []

    try:
        c, b[1] = 1, 2
    except IndexError:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert "IndexError: list assignment index out of range"
    if friendly_traceback.get_lang() == "en":
        assert "You have tried to assign a value to an item of an object" in result
        assert "of type `list` which I cannot identify" in result
        assert "The index you gave was not an allowed value." in result

    try:
        b[1] = 1
    except IndexError:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert "IndexError: list assignment index out of range"
    if friendly_traceback.get_lang() == "en":
        assert "You have tried to assign a value to index `1` of `b`," in result
        assert "a `list` which contains no item." in result

    try:
        a[13] = 1
    except IndexError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert "IndexError: list assignment index out of range"
    if friendly_traceback.get_lang() == "en":
        assert "You have tried to assign a value to index `13` of `a`," in result
        assert "a `list` of length `10`." in result
        assert "The valid index values of `a` are integers ranging from" in result
        assert "`-10` to `9`." in result
    return result, message
