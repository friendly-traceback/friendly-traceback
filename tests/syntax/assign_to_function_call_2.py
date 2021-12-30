"""Should raise SyntaxError: can't assign to function call

Python 3.8: SyntaxError: cannot assign to function call
"""
# Test to confirm that '=' inside function args is not misidentified.
func(a, b=3) = 4
