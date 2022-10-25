import os
import friendly_traceback


def test_Filename_not_found():
    try:
        open("does_not_exist")
    except FileNotFoundError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert (
        "FileNotFoundError: [Errno 2] No such file or directory: 'does_not_exist'"
        in result
    )
    if friendly_traceback.get_lang() == "en":
        assert "that cannot be found is `does_not_exist`." in result
        assert "I have no additional information" in result
    if friendly_traceback._writing_docs:
        return result, message


def test_Filename_not_found_2():
    # For documentation, cwd is tests rather than the root of the repository.
    cwd = os.getcwd()
    chdir = cwd.endswith("tests")
    if chdir:
        os.chdir("..")

    try:
        open("setupp.py")
    except FileNotFoundError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert (
        "FileNotFoundError: [Errno 2] No such file or directory: 'setupp.py'"
        in result
    )
    if friendly_traceback.get_lang() == "en":
        assert "The file `setup.py` has a similar name." in result, os.getcwd()
    if chdir:
        os.chdir(cwd)
    if friendly_traceback._writing_docs:
        return result, message


def test_Filename_not_found_3():
    cwd = os.getcwd()
    chdir = cwd.endswith("tests")
    if chdir:
        os.chdir("..")
    try:
        open("setup.pyg")
    except FileNotFoundError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert (
        "FileNotFoundError: [Errno 2] No such file or directory: 'setup.pyg'"
        in result
    )
    if friendly_traceback.get_lang() == "en":
        assert "Perhaps you meant one of the following files with similar names:" in result
    if chdir:
        os.chdir(cwd)
    if friendly_traceback._writing_docs:
        return result, message


def test_Directory_not_found():
    try:
        open("does_not_exist/file.txt")
    except FileNotFoundError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert (
        "FileNotFoundError: [Errno 2] No such file or directory: 'does_not_exist/file.txt'"
        in result
    )
    if friendly_traceback.get_lang() == "en":
        assert "is not a valid directory" in result
    if friendly_traceback._writing_docs:
        return result, message


if __name__ == "__main__":
    print(test_Filename_not_found()[0])
