from objects import ObjectError

class LibraryError(ObjectError):
    pass

class Library(object):
    def __init__(self, name, exception):
        self.fns = {}
        self.name = name
        self.exception = exception

    def decorate(self, name, decorator):
        org = self.fns[name]
        self.fns[name] = (decorator(org[0]), org[1], org[2], org[3])

    def export(self, fn, req, optional, variadic):
        self.fns[fn.__name__] = (fn, req, optional, variadic)

    def complete(self, kind, arglen):
        if kind not in self.fns:
            raise LibraryError('%s.%s not found!' % (self.name, kind))

        fn, required, o, variadic = self.fns[kind]

        return not variadic and arglen >= required

    def run(self, kind, args):
        if kind not in self.fns:
            raise LibraryError('%s.%s not found!' % (self.name, kind))

        fn, required, optional, variadic = self.fns[kind]

        if not len(args) >= required + optional:
            raise LibraryError('%s.%s requires more arguments' % (self.name, kind))

        if len(args) > required + optional and not variadic:
            raise LibraryError('%s.%s requires fewer arguments' % (self.name, kind))

        try:
            return fn(*args)
        except Exception as e:
            raise self.exception('%s.%s: %s' % (self.name, kind, e.message))


def define(name):
    return Library(name, type(name + 'Error', (LibraryError,), {}))

def use(cls, method):
    def f(this, *args):
        return getattr(cls(this), method)(*args)

    f.func_name = method
    return f

def values(lst):
    return map(lambda x: x.value, lst)

def using(cls):
    return lambda method: use(cls, method)

def export(lib, required, optional=None):
    if not optional:
        optional = 0

    def exporter(fn):
        lib.export(fn, required, optional, False)
        return fn

    return exporter


def exportVariadic(lib, required, optional=None):
    if not optional:
        optional = 0

    def exporter(fn):
        lib.export(fn, required, optional, True)
        return fn

    return exporter

import onto

def require(*types):
    def checker(f):
        def F(*args, **kwds):
            for (a, t) in zip(args[1:], types):
                if t and not isinstance(a, t):
                    raise LibraryError('Supplied argument should be of type %s, found %s' % (t.__name__, type(a).__name__))

            return f(*args, **kwds)
        F.func_name = f.func_name
        return F
    return checker