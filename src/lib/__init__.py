import io
import onto
import integer
import string
import float

def getLibs():
    libs = {}
    libs['io'] = io.lib
    libs['String'] = string.lib
    libs['Float'] = float.lib
    libs['Integer'] = integer.lib

    return libs

def getDesc():
    desc = {}
    desc['version'] = onto.Constant(onto.Float(0.1))
    desc['author']  = onto.Constant(onto.String('Michael Burgess <lyssa@mjburgess.co.uk>'))

    return desc