import onto

class ActionError(onto.Error):
    pass


class ActionThunk(onto.Thunk):
    def __init__(self, action, env):
        onto.Thunk.__init__(self, action, onto.Atom(''), env)

    def send(self, message):
        if not self.libfn.value:
            self.libfn = message
        else:
            onto.Thunk.send(self, message)

        return self

    def respond(self):
        if not self.libfn.value:
            raise ActionError('%s Action requires a symbol!' % self.lib.__name__)

        return ActionResponse(self.lib.name, lambda: self.lib.run(self.libfn.value, self.args))



class ActionResponse(onto.Value):
    def __init__(self, rqtype, responder):
        self.type = rqtype
        self.responder = responder

    def force(self):
        self.responder()
        return onto.Action(None)

    def send(self, m):
        raise ActionError('%s Action cannot accept any more messages (%s)!' % (self.type, repr(m)))

    def __str__(self):
        return self.type + ' ' + self.__class__.__name__

    def __repr__(self):
        return self.__str__()

