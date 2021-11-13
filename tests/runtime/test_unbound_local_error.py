# More complex example than needed - used for documentation
import friendly_traceback

spam_missing_global = 1
spam_missing_both = 1

def outer_missing_global():
    def inner():
        spam_missing_global += 1
    inner()

def outer_missing_nonlocal():
    spam_missing_nonlocal = 1
    def inner():
        spam_missing_nonlocal += 1
    inner()

def outer_missing_both():
    spam_missing_both = 2
    def inner():
        spam_missing_both += 1
    inner()


def test_Missing_global():
    try:
        outer_missing_global()
    except UnboundLocalError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert ("local variable 'spam_missing_global' referenced" in result or
            "cannot access local variable 'spam_missing_global'" in result)  # 3.11
    if friendly_traceback.get_lang() == "en":
        assert (
            "Did you forget to add `global spam_missing_global`?\n"
            in result
        )
    return result, message


def test_Missing_nonlocal():
    try:
        outer_missing_nonlocal()
    except UnboundLocalError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    
    assert ("local variable 'spam_missing_nonlocal' referenced" in result
            or "cannot access local variable 'spam_missing_nonlocal'" in result) # 3.11
    if friendly_traceback.get_lang() == "en":
        assert (
            "Did you forget to add `nonlocal spam_missing_nonlocal`?\n"
            in result
        )
    return result, message


def test_Missing_both():
    try:
        outer_missing_both()
    except UnboundLocalError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert ("local variable 'spam_missing_both' referenced" in result
            or "cannot access local variable 'spam_missing_both'" in result) # 3.11
    if friendly_traceback.get_lang() == "en":
        assert  "either `global spam_missing_both`" in result
        assert  "`nonlocal spam_missing_both`" in result

    return result, message


def test_Typo_in_local():
    
    def test1():
        alpha1 = 1
        alpha2 += 1
        
    try:
        test1()
    except UnboundLocalError:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    
    assert ("local variable 'alpha2' referenced before assignment" in result
            or "cannot access local variable 'alpha2'" in result) # 3.11
    if friendly_traceback.get_lang() == "en":
        assert "similar name `alpha1` was found" in result

    def test2():
        alpha1 = 1
        alpha2 = 1
        alpha3 += 1

    try:
        test2()
    except UnboundLocalError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert ("local variable 'alpha3' referenced before assignment" in result
            or "cannot access local variable 'alpha3'" in result)  # 3.11
    if friendly_traceback.get_lang() == "en":
        assert "perhaps you meant one of the following" in result

    return result, message


def test_Using_name_of_builtin():
    def dist(points):
        max = max(points)
        min = min(points)
        return max - min
    try:
        dist([])
    except UnboundLocalError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert ("local variable 'max' referenced" in result
            or "cannot access local variable 'max'" in result)
    if friendly_traceback.get_lang() == "en":
        assert "`max` is a Python builtin function." in result
    return result, message

if __name__ == "__main__":
    print(test_Missing_global()[0])
