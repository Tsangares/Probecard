from math import log

def prefix(number):
    mag=int(log(number)/log(10)//3)
    key=['','K','M','G','T','P']
    return key[mag]
        
def precision(number):
    mag=log(number)/log(10)//3
    return number/10**(3*mag)

def SI(number):
    prec=precision(number)
    unit=prefix(number)
    return "%.01f%s"%(prec,unit)
