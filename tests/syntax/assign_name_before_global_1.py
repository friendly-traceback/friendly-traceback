"""Should raise SyntaxError: name 'cc' is assigned to prior to global declaration
"""
aa, bb, cc, dd = 1, 2, 3, 4

def fn():
    cc = 1
    global aa, bb, cc, dd
