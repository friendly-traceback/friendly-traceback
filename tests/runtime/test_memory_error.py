import friendly_traceback

# We can set a memory limit on Linux (and OSX?) using the
# resource module; unfortunately, it is not available on Windows.

def test_Generic():
    try:
        # Raise explicitly, just to make sure that all the
        # pieces are in place to catch this error.
        raise MemoryError('Out of memory')
    except MemoryError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    
    assert "MemoryError" in result
    if friendly_traceback.get_lang() == "en":
        assert "a `MemoryError` occurs when Python" in result
    return result, message


if __name__ == "__main__":
    print(test_Generic()[0])
