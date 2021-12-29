"""Should raise SyntaxError: name 'r' is used prior to global declaration
"""


def fn():
    print(var)
    global var
