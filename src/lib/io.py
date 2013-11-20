import sys
import onto
import lyb


lib = lyb.define('IO')

@lyb.export(lib, 1)
@lyb.require(onto.String)
def write(str):
    sys.stdout.write(str.value)

@lyb.export(lib, 1)
@lyb.require(onto.String)
def p(str):
    sys.stdout.write(str.value + "\n")

@lyb.exportVariadic(lib, 1)
@lyb.require(onto.String)
def pf(str, *args):
    sprintf(str, *args)
    sys.stdout.write("\n")

@lyb.exportVariadic(lib, 1)
@lyb.require(onto.String)
def sprintf(str, *args):
    sys.stdout.write(str.value % tuple(lyb.values(args)))