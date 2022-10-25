import sys

import friendly_traceback


def test_Can_only_concatenate():
    try:
        a = "2"
        one = 1
        result = a + one
    except TypeError as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    py37 = "TypeError: can only concatenate" in result
    py36 = "must be str, not int" in result
    assert py37 or py36
    if friendly_traceback.get_lang() == "en":
        assert "a string (`str`) and an integer (`int`)" in result
        assert "Perhaps you forgot to convert the string" in result

    try:
        a = "a"
        a_list = [1, 2, 3]
        result = a + a_list
    except TypeError as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    py37 = "TypeError: can only concatenate" in result
    py36 = "must be str, not list" in result
    assert py37 or py36
    if friendly_traceback.get_lang() == "en":
        assert "a string (`str`) and a `list`" in result

    try:
        a_tuple = (1, 2, 3)
        a_list = [1, 2, 3]
        result = a_tuple + a_list
    except TypeError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "TypeError: can only concatenate" in result
    if friendly_traceback.get_lang() == "en":
        assert "a `tuple` and a `list`" in result
    if friendly_traceback._writing_docs:
        return result, message


def test_Cant_mod_complex_numbers():
    try:
        3 + 3j % 2
    except TypeError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    if friendly_traceback.get_lang() == "en":
        assert "You cannot use complex numbers with the modulo" in result
    if friendly_traceback._writing_docs:
        return result, message


def test_divmod():
    a = 2
    b = 3 + 2j
    try:
        result = divmod(a, b)
    except TypeError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    py_before_310 = "can't take floor or mod of complex number."
    py_310_plus = "unsupported operand type(s) for divmod()"
    assert py_before_310 in result or py_310_plus in result
    must_be = "The arguments of `divmod` must be integers (`int`) or real (`float`) numbers"
    if friendly_traceback.get_lang() == "en":
        assert must_be in result
        assert "At least one of the arguments was a complex number" in result

    if friendly_traceback._writing_docs:
        return result, message



def test_Unsupported_operand_types():
    try:
        one = 1
        none = None
        result = one + none
    except TypeError as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "TypeError: unsupported operand type(s) for +:" in result
    if friendly_traceback.get_lang() == "en":
        assert (
            "an integer (`int`) and a variable equal to `None` (`NoneType`)" in result
        )

    try:
        one = 1
        two = "two"
        one += two
    except TypeError as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "TypeError: unsupported operand type(s) for +=:" in result
    if friendly_traceback.get_lang() == "en":
        assert "an integer (`int`) and a string (`str`)" in result

    try:
        a = (1, 2)
        b = [3, 4]
        result = a - b
    except TypeError as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "TypeError: unsupported operand type(s) for -:" in result
    if friendly_traceback.get_lang() == "en":
        assert "a `tuple` and a `list`" in result

    try:
        a = (1, 2)
        b = [3, 4]
        b -= a
    except TypeError as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "TypeError: unsupported operand type(s) for -=:" in result
    if friendly_traceback.get_lang() == "en":
        assert "a `list` and a `tuple`" in result

    try:
        a = 1j
        b = {2, 3}
        result = a * b
    except TypeError as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "TypeError: unsupported operand type(s) for *:" in result
    if friendly_traceback.get_lang() == "en":
        assert "a complex number and a `set`" in result

    try:
        a = 1j
        b = {2, 3}
        b *= a
    except TypeError as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "TypeError: unsupported operand type(s) for *=:" in result
    if friendly_traceback.get_lang() == "en":
        assert "a `set` and a complex number" in result

    try:
        a = {1: 1, 2: 2}
        b = 3.1416
        result = a / b
    except TypeError as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "TypeError: unsupported operand type(s) for /:" in result
    if friendly_traceback.get_lang() == "en":
        assert "a dictionary (`dict`) and a number (`float`)" in result

    try:
        a = {1: 1, 2: 2}
        b = 3.1416
        b /= a
    except TypeError as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "TypeError: unsupported operand type(s) for /=:" in result
    if friendly_traceback.get_lang() == "en":
        assert "a number (`float`) and a dictionary (`dict`)" in result

    try:
        a = {1: 1, 2: 2}
        b = 1
        result = a // b
    except TypeError as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "TypeError: unsupported operand type(s) for //:" in result
    if friendly_traceback.get_lang() == "en":
        assert "a dictionary (`dict`) and an integer (`int`)" in result

    try:
        a = {1: 1, 2: 2}
        b = 3.1416
        b //= a
    except TypeError as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "TypeError: unsupported operand type(s) for //=:" in result
    if friendly_traceback.get_lang() == "en":
        assert "an integer (`int`) and a dictionary (`dict`)"

    try:
        a = "a"
        b = 2
        result = a & b
    except TypeError as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "TypeError: unsupported operand type(s) for &:" in result
    if friendly_traceback.get_lang() == "en":
        assert "a string (`str`) and an integer (`int`)" in result

    try:
        a = "a"
        b = 2
        b &= a
    except TypeError as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "TypeError: unsupported operand type(s) for &=:" in result
    if friendly_traceback.get_lang() == "en":
        assert "an integer (`int`) and a string (`str`)" in result

    try:
        a = {1: 1, 2: 2}
        b = 3.1416
        result = a ** b
    except TypeError as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "TypeError: unsupported operand type(s) for ** or pow():" in result
    if friendly_traceback.get_lang() == "en":
        assert "You tried to exponentiate (raise to a power)" in result

    try:
        a = {1: 1, 2: 2}
        b = 3.1416
        a **= b
    except TypeError as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "TypeError: unsupported operand type(s) for **" in result
    if friendly_traceback.get_lang() == "en":
        assert "You tried to exponentiate (raise to a power)" in result

    try:
        a = 3.0
        b = 42
        result = a ^ b
    except TypeError as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "TypeError: unsupported operand type(s) for ^:" in result
    if friendly_traceback.get_lang() == "en":
        assert (
            "Did you mean `a ** b`" in result
            or "Did you mean `result = a ** b`?" in result  # Python 3.11.0a3
        )

    try:
        a = 3.0
        b = 42
        a ^= b
    except TypeError as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "TypeError: unsupported operand type(s) for ^=:" in result
    if friendly_traceback.get_lang() == "en":
        assert "Did you mean `a **= b`" in result

    try:
        a = "a"
        b = 42
        result = a >> b
    except TypeError as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "TypeError: unsupported operand type(s) for >>:" in result
    if friendly_traceback.get_lang() == "en":
        assert "You tried to perform the bit shifting operation >>" in result

    try:
        a = "a"
        b = 42
        a >>= b
    except TypeError as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "TypeError: unsupported operand type(s) for >>=:" in result
    if friendly_traceback.get_lang() == "en":
        assert "You tried to perform the bit shifting operation >>" in result

    try:
        a = "a"
        b = 2
        result = a @ b
    except TypeError as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "TypeError: unsupported operand type(s) for @:" in result
    if friendly_traceback.get_lang() == "en":
        assert "You tried to use the operator @" in result

    try:
        a = "a"
        b = 2
        a @= b
    except TypeError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "TypeError: unsupported operand type(s) for @=:" in result
    if friendly_traceback.get_lang() == "en":
        assert "You tried to use the operator @" in result
    if friendly_traceback._writing_docs:
        return result, message


def test_Comparison_not_supported():
    import itertools
    try:
        3j < 4j
    except TypeError:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    if friendly_traceback.get_lang() == "en":
        assert "Complex numbers cannot be ordered." in result

    try:
        a = "a"
        b = 42
        b < a
    except TypeError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "TypeError: '<' not supported between instances of 'int' and 'str'" in result
    if friendly_traceback.get_lang() == "en":
        assert "You tried to do an order comparison (<)" in result

    try:
        42 < itertools.count()
    except TypeError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "TypeError: '<' not supported between instances of 'int' and 'itertools.count'" in result
    if friendly_traceback.get_lang() == "en":
        assert "`itertools.count` is an iterator" in result

    try:
        a = "2"
        b = 42
        b >= a
    except TypeError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    if friendly_traceback.get_lang() == "en":
        assert "You tried to do an order comparison (>=" in result
        assert "Did you forget to convert the string" in result

    if friendly_traceback._writing_docs:
        return result, message


def test_Bad_type_for_unary_operator():
    try:
        a = +"abc"
        print(a)
    except TypeError as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "TypeError: bad operand type for unary +: 'str'" in result
    assert not "+=" in result
    if friendly_traceback.get_lang() == "en":
        assert "You tried to use the unary operator '+'" in result

    try:
        a = -[1, 2, 3]
        print(a)
    except TypeError as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "TypeError: bad operand type for unary -: 'list'" in result
    if friendly_traceback.get_lang() == "en":
        assert "You tried to use the unary operator '-'" in result

    try:
        a = ~(1, 2, 3)
        print(a)
    except TypeError as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "TypeError: bad operand type for unary ~: 'tuple'" in result
    if friendly_traceback.get_lang() == "en":
        assert "You tried to use the unary operator '~'" in result

    try:
        # fmt: off
        a = "abc"
        a =+ "def"
        # fmt: on
        print(a)
    except TypeError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "TypeError: bad operand type for unary +: 'str'" in result
    if friendly_traceback.get_lang() == "en":
        assert "Perhaps you meant to write `+=`" in result
        assert "You tried to use the unary operator '+'" in result
    if friendly_traceback._writing_docs:
        return result, message


def test_Tuple_no_item_assignment():
    a = (1, 2, 3)
    try:
        a[0] = 0
    except TypeError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "TypeError: 'tuple' object does not support item assignment" in result
    if friendly_traceback.get_lang() == "en":
        assert "In Python, some objects are known as immutable:" in result
        assert "Perhaps you meant to use a list" in result
    if friendly_traceback._writing_docs:
        return result, message


def test_Too_many_positional_argument():
    def fn(*, b=1):
        pass

    try:
        fn(1)
    except TypeError as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "TypeError" in result
    assert "fn() takes 0 positional arguments but 1 was given" in result
    if friendly_traceback.get_lang() == "en":
        assert "1 positional argument(s) while it requires 0" in result

    class A:
        def f(x):
            pass

    try:
        A().f(1)
    except TypeError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "TypeError" in result
    assert "f() takes 1 positional argument but 2 were given" in result
    if friendly_traceback.get_lang() == "en":
        assert "2 positional argument(s) while it requires 1" in result
        # assert "Perhaps you forgot `self`" in result
    if friendly_traceback._writing_docs:
        return result, message


def test_Too_few_positional_argument():
    def fn(a, b, c):
        pass

    try:
        fn(1)
    except TypeError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "TypeError" in result
    assert "fn() missing 2 required positional argument" in result
    if friendly_traceback.get_lang() == "en":
        assert "fewer positional arguments than it requires (2 missing)." in result
    if friendly_traceback._writing_docs:
        return result, message


def test_Not_callable():
    try:
        _ = (1, 2)(3, 4)
    except TypeError as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "TypeError: 'tuple' object is not callable" in result
    if friendly_traceback.get_lang() == "en":
        assert "you have a missing comma between the object" in result

    try:
        _ = 3(4 + 4)
    except TypeError as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "TypeError: 'int' object is not callable" in result
    if friendly_traceback.get_lang() == "en":
        assert "Perhaps you forgot a multiplication operator" in result

    try:
        _ = [1, 2](3, 4)
    except TypeError as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: 'list' object is not callable" in result
    if friendly_traceback.get_lang() == "en":
        assert "you have a missing comma between the object" in result


    # Test with dotted name
    class A:
        a_list = [1, 2, 3]

    try:
        b = A()
        b.a_list(3)
    except TypeError as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: 'list' object is not callable" in result
    if friendly_traceback.get_lang() == "en":
        assert "b.a_list[3]" in result

    try:
        a, b = 3, 7
        _ = [1, 2](a + b)
    except TypeError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: 'list' object is not callable" in result
    if friendly_traceback.get_lang() == "en":
        assert "Perhaps you meant to use `[]` instead of `()`" in result
    if friendly_traceback._writing_docs:
        return result, message


def test_Derive_from_BaseException():
    class MyException:
        pass
    # silence problem with ASTTokens
    friendly_traceback.debug_helper.DEBUG = False
    try:
        try:
            1/0
        except (MyException, BaseException):
            pass
    except TypeError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    friendly_traceback.debug_helper.DEBUG = True

    assert "catching classes that do not inherit from BaseException" in result
    if friendly_traceback.get_lang() == "en":
        assert "you must only have classes that derive from `BaseException`" in result

    try:
        raise "exception"  # noqa
    except TypeError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "TypeError: exceptions must derive from BaseException" in result
    if friendly_traceback.get_lang() == "en":
        assert "Exceptions must be derived from `BaseException`." in result
    if friendly_traceback._writing_docs:
        return result, message


def test_Cannot_multiply_by_non_int():

    try:
        "b" * "a"
    except TypeError as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "TypeError: can't multiply sequence by non-int of type 'str'" in result
    if friendly_traceback.get_lang() == "en":
        assert "You can only multiply sequences, such as" in result

    try:
        "3" * "a"
    except TypeError as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "TypeError: can't multiply sequence by non-int of type 'str'" in result
    if friendly_traceback.get_lang() == "en":
        assert 'Did you forget to convert `"3"` into an integer?' in result

    a = b = c = "2"
    try:
        d = a * b * c
    except TypeError as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "TypeError: can't multiply sequence by non-int of type 'str'" in result
    if friendly_traceback.get_lang() == "en":
        assert "Did you forget to convert `a` and `b` into integers?" in result

    a = "abc"
    try:
        a *= c
    except TypeError as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "TypeError: can't multiply sequence by non-int of type 'str'" in result
    if friendly_traceback.get_lang() == "en":
        assert "Did you forget to convert `c` into an integer?" in result

    try:
        "a" * "2"
    except TypeError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "TypeError: can't multiply sequence by non-int of type 'str'" in result
    if friendly_traceback.get_lang() == "en":
        assert 'Did you forget to convert `"2"` into an integer?' in result
    if friendly_traceback._writing_docs:
        return result, message


def test_Not_an_integer():
    try:
        range([1, 2])
    except TypeError as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "TypeError: 'list' object cannot be interpreted as an integer" in result
    if friendly_traceback.get_lang() == "en":
        assert "Perhaps you forgot to convert " not in result

    try:
        range("2")
    except TypeError as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "TypeError: 'str' object cannot be interpreted as an integer" in result
    if friendly_traceback.get_lang() == "en":
        assert 'Perhaps you forgot to convert `"2"` into an integer.' in result

    try:
        range(1.0)
    except TypeError as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "TypeError: 'float' object cannot be interpreted as an integer" in result
    if friendly_traceback.get_lang() == "en":
        assert "Perhaps you forgot to convert `1.0" in result

    c, d = "2", "3"
    try:
        range(c, d)
    except TypeError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "TypeError: 'str' object cannot be interpreted as an integer" in result
    if friendly_traceback.get_lang() == "en":
        assert "Perhaps you forgot to convert `c, d` into integers." in result
    if friendly_traceback._writing_docs:
        return result, message


def test_Indices_must_be_integers_or_slices():
    a = [1, 2, 3]

    try:
        a[1, 2]
    except TypeError as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "TypeError: list indices must be integers or slices" in result
    if friendly_traceback.get_lang() == "en":
        assert "Did you mean `a[1:2]`" in result

    a = (1, 2, 3)
    try:
        a[2.0]
    except TypeError as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "TypeError: tuple indices must be integers or slices" in result
    if friendly_traceback.get_lang() == "en":
        assert "Perhaps you forgot to convert `2.0` into an integer." in result

    try:
        [1, 2, 3]["2"]
    except TypeError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "TypeError: list indices must be integers or slices" in result
    if friendly_traceback.get_lang() == "en":
        assert 'Perhaps you forgot to convert `"2"` into an integer.' in result
    if friendly_traceback._writing_docs:
        return result, message


def test_Slice_indices_must_be_integers_or_None():
    try:
        [1, 2, 3][1.0:2.0]
    except TypeError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert (
        "TypeError: slice indices must be integers or None "
        "or have an __index__ method"
    ) in result
    if friendly_traceback.get_lang() == "en":
        assert "When using a slice to extract a range of elements" in result
    if friendly_traceback._writing_docs:
        return result, message


def test_Unhachable_type():
    try:
        {[1, 2]: 1}
    except TypeError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "unhashable type: 'list'" in result
    if friendly_traceback.get_lang() == "en":
        assert "consider using a `tuple`" in result
    if friendly_traceback._writing_docs:
        return result, message


def test_Object_is_not_subscriptable():

    if sys.version_info.minor <= 8:
        try:
            # in 3.9+, this is assigning to a typing.GenericAlias object
            a = list[1, 2, 3]
        except TypeError:
            friendly_traceback.explain_traceback(redirect="capture")
        result = friendly_traceback.get_output()
        assert "TypeError: 'type' object is not subscriptable" in result
        if sys.version_info.minor == 6:
            assert "list(1, 2, 3)" in result
        else:
            assert "list((1, 2, 3))" in result

    try:
        a = 2[1]
    except TypeError as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "TypeError: 'int' object is not subscriptable" in result
    if friendly_traceback.get_lang() == "en":
        assert "from `2`, an object of type `int`" in result

    def f():
        pass

    try:
        a = f[1]
    except TypeError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "TypeError: 'function' object is not subscriptable" in result
    if friendly_traceback.get_lang() == "en":
        assert "Did you mean `f(1)`" in result
    if friendly_traceback._writing_docs:
        return result, message


def test_Object_is_not_iterable():
    try:
        list(42)
    except TypeError as e:
        friendly_traceback.explain_traceback(redirect="capture")
        message = str(e)
    result = friendly_traceback.get_output()

    assert "TypeError: 'int' object is not iterable" in result
    if friendly_traceback.get_lang() == "en":
        assert "An iterable is required here." in result
    if friendly_traceback._writing_docs:
        return result, message


def test_Argument_of_object_is_not_iterable():
    a = object()
    b = object()
    try:
        a in b
    except TypeError as e:
        friendly_traceback.explain_traceback(redirect="capture")
        message = str(e)
    result = friendly_traceback.get_output()
    assert "TypeError: argument of type 'object' is not iterable" in result
    if friendly_traceback.get_lang() == "en":
        assert "A container is required here." in result

    if friendly_traceback._writing_docs:
        return result, message

def test_Cannot_unpack_non_iterable_object():
    try:
        a, b = 42.0
    except TypeError as e:
        friendly_traceback.explain_traceback(redirect="capture")
        message = str(e)
    result = friendly_traceback.get_output()

    assert (
        "TypeError: cannot unpack non-iterable float object" in result
        or "TypeError: 'float' object is not iterable" in result
    )
    if friendly_traceback.get_lang() == "en":
        assert "An iterable is an object capable" in result
    if friendly_traceback._writing_docs:
        return result, message


def test_Cannot_convert_dictionary_update_sequence():
    try:
        dict([1, 2, 3])
    except TypeError as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "TypeError: cannot convert dictionary update" in result
    if friendly_traceback.get_lang() == "en":
        assert "you should use the `dict.fromkeys()`" in result

    dd = {"a": "a"}
    try:
        dd.update([1, 2, 3])
    except TypeError as e:
        friendly_traceback.explain_traceback(redirect="capture")
        message = str(e)
    result = friendly_traceback.get_output()

    assert "TypeError: cannot convert dictionary update" in result
    if friendly_traceback.get_lang() == "en":
        assert ".update( dict.fromkeys(" in result
    if friendly_traceback._writing_docs:
        return result, message


def test_Builtin_has_no_len():
    try:
        len("Hello world".split)
    except TypeError as e:
        friendly_traceback.explain_traceback(redirect="capture")
        message = str(e)
    result = friendly_traceback.get_output()

    assert "TypeError: object of type 'builtin_function_or_method' has no len()"
    if friendly_traceback.get_lang() == "en":
        assert 'Did you forget to call `"Hello world".split`?' in result
    if friendly_traceback._writing_docs:
        return result, message


def test_function_has_no_len():
    def bad():
        pass

    try:
        len(bad)
    except TypeError as e:
        friendly_traceback.explain_traceback(redirect="capture")
        message = str(e)
    result = friendly_traceback.get_output()

    assert "TypeError: object of type 'function' has no len()" in result
    if friendly_traceback.get_lang() == "en":
        assert "Did you forget to call `bad`?" in result
    if friendly_traceback._writing_docs:
        return result, message


def test_vars_arg_must_have_dict():
    class F:
        __slots__ = []

    f = F()
    a = [1, 2]
    vars_must = "vars() argument must have __dict__ attribute"
    cause = "The function `vars` is used to list the content of the"
    use_slots = "uses `__slots__` instead of `__dict__`."
    no_slots = "is an object without such an attribute."
    try:
        vars(a)
    except TypeError as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert vars_must in result
    if friendly_traceback.get_lang() == "en":
        assert cause in result
        assert no_slots in result

    try:
        vars([1, 2])
    except TypeError as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert vars_must in result
    if friendly_traceback.get_lang() == "en":
        assert cause in result
        assert no_slots not in result
        assert use_slots not in result

    try:
        vars(f)
    except TypeError as e:
        friendly_traceback.explain_traceback(redirect="capture")
        message = str(e)
    result = friendly_traceback.get_output()
    assert vars_must in result
    if friendly_traceback.get_lang() == "en":
        assert cause in result
        assert use_slots in result

    if friendly_traceback._writing_docs:
        return result, message


def test_function_got_multiple_argument():
    def fn1(a):
        pass

    try:
        fn1(0, a=1)
    except TypeError as e:
        friendly_traceback.explain_traceback(redirect="capture")
        message = str(e)
    result = friendly_traceback.get_output()
    assert "got multiple values for argument" in result
    if friendly_traceback.get_lang() == "en":
        assert "This function has only one argument" in result

    def fn2(a, b=1):
        pass

    try:
        fn2(0, a=1)
    except TypeError as e:
        friendly_traceback.explain_traceback(redirect="capture")
        message = str(e)
    result = friendly_traceback.get_output()
    assert "got multiple values for argument" in result
    if friendly_traceback.get_lang() == "en":
        assert "This function has the following arguments" in result

    if friendly_traceback._writing_docs:
        return result, message


def test_method_got_multiple_argument():
    class T:
        def some_method(self, a):
            pass

    t = T()
    try:
        t.some_method(0, a=1)
    except TypeError as e:
        friendly_traceback.explain_traceback(redirect="capture")
        message = str(e)
    result = friendly_traceback.get_output()
    assert "got multiple values for argument" in result
    if friendly_traceback.get_lang() == "en":
        assert "This function has only one argument" in result

    if friendly_traceback._writing_docs:
        return result, message


def test_getattr_attribute_name_must_be_string():
    # we also test for hasattr
    try:
        hasattr("__repr__", 1)
    except TypeError as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert "attribute name must be string" in result
    if friendly_traceback.get_lang() == "en":
        assert (
            "The second argument of the function `hasattr()` must be a string."
            in result
        )

    try:
        getattr("__repr__", 1)  # as reported in issue #77
    except TypeError as e:
        friendly_traceback.explain_traceback(redirect="capture")
        message = str(e)
    result = friendly_traceback.get_output()
    assert "attribute name must be string" in result
    if friendly_traceback.get_lang() == "en":
        assert (
            "The second argument of the function `getattr()` must be a string."
            in result
        )

    if friendly_traceback._writing_docs:
        return result, message


def test_Generator_has_no_len():
    try:
        nb = len(letter
                 for letter in "word")
    except TypeError as e:
        friendly_traceback.explain_traceback(redirect="capture")
        message = str(e)
    result = friendly_traceback.get_output()
    assert "object of type 'generator' has no len()" in result
    if friendly_traceback.get_lang() == "en":
        assert 'len([letter' in result
        assert 'for letter in "word"])' in result
        assert "You likely need to build a list first." in result
    if friendly_traceback._writing_docs:
        return result, message

if __name__ == "__main__":
    print(test_Not_an_integer()[0])
