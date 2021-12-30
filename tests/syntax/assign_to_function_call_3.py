"""Should raise SyntaxError: can't assign to function call

Python 3.8: SyntaxError: cannot assign to function call
"""
# tests for continuation marker
a = f(1, 2,  # this is a comment
      3, 4) = 5
