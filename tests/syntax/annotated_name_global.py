# SyntaxError: annotated name 'var' can't be global
def foo():
    global var
    var:int = 1

var = 0
foo()