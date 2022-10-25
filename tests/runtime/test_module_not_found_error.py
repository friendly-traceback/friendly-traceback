import sys
import friendly_traceback


def test_Standard_library_module():
    try:
        import Tkinter
    except ModuleNotFoundError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    
    assert "No module named 'Tkinter'" in result
    if friendly_traceback.get_lang() == "en":
        assert "Did you mean `tkinter`" in result
    if friendly_traceback._writing_docs:
        return result, message


def test_Not_a_package():

    try:
        import os.xxx
    except ModuleNotFoundError as e:
        friendly_traceback.explain_traceback(redirect="capture")
        message = str(e)
    result = friendly_traceback.get_output()
    
    assert "No module named" in result and "'os.xxx'" in result
    if friendly_traceback.get_lang() == "en":
        assert "`xxx` cannot be imported" in result

    return  result, message

def test_Not_a_package_similar_name():
    try:
        import os.pathh
    except ModuleNotFoundError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    
    assert "No module named" in result and "'os.pathh'" in result
    if friendly_traceback.get_lang() == "en":
        assert "Did you mean `import os.path`" in result
    if friendly_traceback._writing_docs:
        return result, message

def test_Object_not_module():
    try:
        import os.open
    except ModuleNotFoundError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "No module named" in result and " 'os.open'" in result
    if friendly_traceback.get_lang() == "en":
        assert "Did you mean `from os import open`?" in result
    if friendly_traceback._writing_docs:
        return result, message

def test_Similar_object_not_module():
    try:
        import os.opend
    except ModuleNotFoundError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "No module named" in result and " 'os.opend'" in result
    if friendly_traceback.get_lang() == "en":
        assert "Did you mean `from os import open`?" in result
        assert "`open` is a name similar to `opend`" in result
    if friendly_traceback._writing_docs:
        return result, message

def test_Need_to_install_module():
    try:
        import alphabet
    except ModuleNotFoundError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "No module named 'alphabet'" in result
    if friendly_traceback.get_lang() == "en":
        assert "Perhaps you need to install it" in result
    if friendly_traceback._writing_docs:
        return result, message



if sys.platform.startswith("win"):
    def test_no_curses():
        try:
            import curses
        except ModuleNotFoundError as e:
            message = str(e)
            friendly_traceback.explain_traceback(redirect="capture")
        result = friendly_traceback.get_output()
        assert "No module named '_curses'" in result
        if friendly_traceback.get_lang() == "en":
            assert "The curses module is rarely installed with Python on Windows." in result

        if friendly_traceback._writing_docs:
            return result, message


if __name__ == "__main__":
    print(test_Standard_library_module()[0])
