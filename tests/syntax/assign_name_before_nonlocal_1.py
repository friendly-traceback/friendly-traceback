"""Should raise SyntaxError: name 'q' is used prior to nonlocal declaration """


def f():
    pp = 0
    qq = 1


    def g():
        print(qq)
        nonlocal pp, qq
