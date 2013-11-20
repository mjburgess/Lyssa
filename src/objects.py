import onto

class ObjectError(onto.Error):
    pass

class ContainerError(ObjectError):
    pass

class Object(onto.Value):
    def __init__(self, value, env):
        self.value = value
        self.env = env
        self.types = {}

    def acceptType(self, t):
        self.types[t] = self.__getattribute__(t.__name__)

    def send(self, message):
        if isinstance(message, onto.Atom) and self.value:
            return onto.Thunk(self.value.__class__.__name__, message, self.env).send(self.value)

        if isinstance(message, onto.Operator):
            if hasattr(self, message.semantics()):
                return self.__getattribute__(message.semantics())(message) or self
            if hasattr(self, message.__class__.__name__):
                return self.__getattribute__(message.__class__.__name__)(message) or self

        for type in self.types:
            if isinstance(message, type):
                return self.types[type](message)

        raise ObjectError('%s does not know how to respond to %s' % (repr(self), repr(message)))


    def Expand(self, message):
        raise ObjectError('This object (%s) cannot be concatenated!' % repr(self.value))

    def Bind(self, message):
        return Container(self.value, self.env).send(message)

    def Assign(self, message):
        return Mutable(self.value, self.env).send(message)

class Box(Object):
    def __init__(self, val, env):
        Object.__init__(self, val, env)

        self.type     = val.__class__.__name__
        self.accepter = self.askType
        self.waiting  = None

        self.acceptType(onto.Value)

    def respond(self):
        return self.value

    def perform(self):
        return self.value

    def askType(self, message):
        return onto.Thunk(self.type, self.waiting.semantics(), self.env).send(self.value).send(message).respond()

    def sendValue(self, message):
        return self.value.send(message)

    def Value(self, value):
        return self.accepter(value)

    def Operator(self, data):
        return onto.Thunk(self.type, data.semantics(), self.env).send(self.value).respond()

class Container(Box):
    def __init__(self, val, env):
        Box.__init__(self, None, env)

        self.name = str(val)
        self.open = True

        self.env.setObject(val, self)

    def send(self, message):
        if self.value is None and not self.open:
            return message

        return Object.send(self, message)

    def respond(self):
        return self

    def prime(self, accepter):
        self.open = True
        self.accepter = accepter

        return self

    def wait(self, op):
        self.accepter = self.askType
        self.waiting = op

    def bind(self, data):
        if self.open:
            if isinstance(data, Container):
                self.value = data.value
            else:
                self.value = data

            if not isinstance(data, onto.Literal):
                self.accepter = self.sendValue

            self.open = False
            self.type = self.value.__class__.__name__
        else:
            raise ContainerError('%s cannot be bound!' % self.name)

        return self

    def Bind(self, data):
        self.prime(self.bind)

class Mutable(Container):
    def askType(self, message):
        if self.open:
            self.value = Container.askType(self, message)
            return self
        else:
            return Container.askType(self, message)

    def awaitSymbol(self, data):
        self.waiting = data
        self.prime(self.askType)

        return self

    def Assign(self, message):
        self.prime(self.bind)

    def Expand(self, data):
        self.prime(self.awaitSymbol)

    def PlusEquals(self, data):
        self.awaitSymbol(onto.Symbol(onto.Operators.Plus))

    def DashEquals(self, data):
        self.awaitSymbol(onto.Symbol(onto.Operators.Dash))

class Type(Box):
    def __init__(self, name, env):
        Box.__init__(self, name, env)

        self.type  = name

    def askType(self, message):
        return onto.Thunk(self.type, self.primer.semantics(), self.env).send(message).respond()