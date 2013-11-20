Operators =  type('OperatorsEnum', (), {})()
Operators.Bind = '='
Operators.Assign = ':='
Operators.Expand = '~='
Operators.PlusEquals = '+='
Operators.DashEquals = '-='
Operators.Cons = '!'
Operators.Plus = '+'
Operators.Dash = '-'
Operators.Delay = '?'
Operators.MultiPlus = '++'

OperatorNames = {v:k for k, v in Operators.__dict__.items()}

class Error(Exception):
    pass

class OntoError(Error):
    pass

class Kind(object):
    def __init__(self, value, prep=False):
        if prep:
            self.setValue(self.prepareValue(value))
        elif isinstance(value, Kind):
            self.setValue(value.value)
        else:
            self.setValue(value)

    def prepareValue(self, value):
        return value

    def setValue(self, value):
        self.value = value
        return self

    def getValue(self):
        return self.value

    def __eq__(self, other):
        return repr(self) == repr(other)

    def __hash__(self):
        return sum(map(ord, self.__class__.__name__)) * 100 + sum(map(ord, str(self.value)))

    def __str__(self):
        return str(self.value)

    def __float__(self):
        return float(self.value)

    def __int__(self):
        return int(self.value)

    def __repr__(self):
        return self.repr(self.__class__.__name__, self.value)

    def repr(self, name, value=''):
        if isinstance(value, Kind):
            value = ' (' + repr(value) + ')'
        else:
            value = ' (' + str(value) + ')'

        return name + value

class TypeValue(Kind):
    pass


class Value(Kind):
    def respond(self):
        return self

    def perform(self):
        return self.respond()

    def send(self, message):
        raise OntoError('%s does not know how to respond to %s' % (repr(self), repr(message)))


class NullValue(Value):
    def __init__(self):
        Value.__init__(self, '')

    def fail(self):
        raise OntoError('Failed to specify a valid object!')

    def __getattr__(self, item):
        self.fail()


class Empty(Kind):
    def prepareValue(self, value):
        return ''

    def __repr__(self):
        return self.__class__.__name__

class Annotative(Kind):
    pass

class Literal(Value):
    pass


class Numeric(Literal):
    def add(self, value):
        raise NotImplementedError

class Commentation(Annotative):
    pass

class Quote(Empty):
    pass

class BlockQuote(Quote):
    pass

class BlockUnquote(Quote):
    pass

class Termination(Annotative):
    count = 1
    def prepareValue(self, value):
        Termination.count += value.count("\n")
        return Termination.count


class Discard(Termination):
    pass

class String(Literal):
    def prepareValue(self, value):
        return value[1:-1]

    def setValue(self, value):
        self.value = str(value)

class StringyValue(Value):
    def prepareValue(self, value):
        return value[1:]

class Action(Value):
    def prepareValue(self, value):
        return value[1:]

class Pipe(Empty):
    pass

class Block(Value):
    pass

class Lambda(Block):
    pass

class Atom(Value):
    def prepareValue(self, value):
        return value[1:]

class Symbol(Value):
    def semantics(self):
        return OperatorNames[self.value]
    def prepareValue(self, value):
        return value[1:]

class Operator(Value):
    def semantics(self):
        return OperatorNames[self.value]

    def __repr__(self):
        return self.repr('Operator',  self.semantics() + ' (' + self.value + ')')

class Force(Empty):
    pass

class Constant(Value):
    def prepareValue(self, value):
        return value[1:]


class Float(Numeric):
    def setValue(self, value):
       self.value = float(value)



class Integer(Numeric):
    def setValue(self, value):
        self.value = int(value)

# Onto-Meta
class Thunk(Value):
    def __init__(self, libname, libfn, env):
        if isinstance(libname, Value):
            libname = libname.value

        self.lib    = env.getLibrary(libname)
        self.value  = self.lib.name
        self.libfn = libfn
        self.args  = []
        self.delay = False

    def __repr__(self):
        return '%s<%s.%s> %s' %(self.__class__.__name__, self.value, str(self.libfn), repr(self.args))

    def __str__(self):
        raise OntoError('%s cannot be used as a string!' % repr(self))

    def perform(self):
        return self.force()

    def force(self):
        return self.lib.run(self.libfn, self.args)

    def send(self, message):
        if message.value == Operators.Delay:
            self.delay = True
        else:
            self.delay = False
            self.args.append(message)

        return self

    def respond(self):
        if not self.delay and self.lib.complete(self.libfn, len(self.args)):
            return self.lib.run(self.libfn, self.args)
        else:
            return self