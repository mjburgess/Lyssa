import actions
import onto
import objects
import meta

from lib import getLibs, getDesc

Null = onto.NullValue()

class ExecutionError(onto.Error):
    pass

class ExecutionContext(object):
    def __init__(self, libs, consts, parent=None):
        self.objects = {}
        self.parent = None
        self.libs = libs
        self.consts = consts

    def setObject(self, obj, object):
        self.objects[obj.value] = object

    def removeObject(self, name):
        del self.objects[name]

    def hasObject(self, obj):
        return (obj.value in self.objects) or (self.parent and self.parent.hasObject(obj))

    def getObject(self, obj):
        if obj.value in self.objects:
            return self.objects[obj.value]
        elif self.parent and self.parent.hasObject(obj):
            return self.parent.getObject(obj)
        else:
            raise ExecutionError('Cannot find %s in execution context' % repr(obj))


    def setLibrary(self, kind, cls):
        self.libs[kind] = cls
        return self

    def getLibrary(self, kind):
        return self.libs[kind]

    def setConstant(self, const, value):
        self.consts[const.value] = value
        return self

    def getConstant(self, const):
        return self.consts[const.value]

    def hasConstant(self, const):
        return const.value in self.consts

class VirtualManager(object):
    def __init__(self, env):
        self.target  = None
        self.memory = []
        self.open  = False
        self.env   = env
        self.line  = 1
        self.errs  = []
    def run(self, stream):
        for token in stream:
            self.direct(token, stream)

            try:
                getattr(self, token.__class__.__name__)(token)
            except ExecutionError as e:
                raise e
            except onto.Error as e:
                self.errs.append('%s (Line %d): %s' % (e.__class__.__name__, self.line, e.message))

        return self.finish()

    def direct(self, token, stream):
        if isinstance(token, onto.Quote):
            token = self.delambda(stream)
        if isinstance(token, onto.BlockQuote):
            token = self.deblock(stream)
        if isinstance(token, onto.Termination):
            self.line = token.value

    def finish(self):
        if self.errs:
            return False

        if isinstance(self.target, actions.ActionThunk):
            return self.target.respond().force()
        elif self.target:
            return self.target.respond()
        else:
            raise ExecutionError('Programs must return a value!')

    def delambda(self, stream):
        partial = []
        for token in stream:
            if isinstance(token, onto.Termination):
                return onto.Block(partial)
            else:
                partial.append(stream.pop())

    def deblock(self, stream):
        partial = []
        for token in stream:
            if isinstance(token, onto.BlockUnquote):
                return onto.Block(partial)
            elif isinstance(token, onto.BlockQuote):
                partial.append(self.deblock(stream))
            else:
                partial.append(stream.pop())

    def send(self, message):
        return self.switch(self.target.send(message.perform()))

    def switch(self, state):
        self.open = True
        if isinstance(state, onto.Literal):
            self.target = objects.Box(state, self.env)
        else:
            self.target = state


    def orient(self, var):
        if self.open:
            self.send(var)
        else:
            self.switch(var)

    def forward(self):
        self.memory.append(self.target)
        self.switch(None)
        self.open = False

    def rewind(self):
        if self.target:
            message = self.target.respond()
        else:
            message = None

        while self.memory:
            target = self.memory.pop()

            if target:
                message = target.send(message).respond()

        self.target = message

    def close(self):
        self.open = False
        self.rewind()



class VirtualMachine(VirtualManager):
    def Pipe(self, p):
        self.forward()

    def Action(self, action):
        self.switch(actions.ActionThunk(action, self.env))

    def Value(self, value):
        if self.env.hasObject(value):
            self.orient(self.env.getObject(value))
        elif not self.open:
            self.switch(objects.Object(value, self.env))
        else:
            raise ExecutionError('Unknown value (%s) in this context' % value)

    def StringyValue(self, value):
        if self.env.hasObject(value):
            var = self.env.getObject(value)
            self.orient(onto.String(var.perform()))
        else:
            raise ExecutionError('Can only string cast variables, %s found' % repr(value))

    def Constant(self, const):
        if self.env.hasConstant(const):
            self.orient(self.env.getConstant(const))
        else:
            raise ExecutionError('%s not found' % repr(const))

    def TypeValue(self, type):
        self.Value(type)

    def Operator(self, op):
        self.send(op)

    def Delay(self, op):
        self.Operator(op)

    def Atom(self, sym):
        if isinstance(self.target, onto.Literal):
            self.switch(objects.Object(self.target, self.env))

        self.orient(sym)

    def Symbol(self, sym):
        self.Atom(sym)

    def String(self, string):
        self.orient(string)

    def Float(self, float):
        self.orient(float)

    def Integer(self, integer):
        self.orient(integer)

    def Termination(self, term):
        self.close()

    def Force(self, force):
        self.close()
        if hasattr(self.target, 'force'):
            self.switch(self.target.force())
        else:
            raise ExecutionError('%s cannot be forced' % repr(self.target))

    def Discard(self, disc):
        pass

DefaultEnvironment = meta.addTypes(ExecutionContext(getLibs(), getDesc()))