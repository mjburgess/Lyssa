import onto
import lyb
import objects

def addTypes(env):
    objects.Type(onto.Value('String'), env)
    objects.Type(onto.Value('Float'), env)
    objects.Type(onto.Value('Integer'), env)

    return env


class Float(onto.Float):
    def Cons(self):
        return onto.Float(self.value)

    @lyb.require(onto.Numeric)
    def Plus(self, value):
        return onto.Float(self.value + float(value))

class Integer(onto.Integer):
    def Cons(self):
        return onto.Integer(self.value)

    @lyb.require(onto.Numeric)
    def Plus(self, value):
        return onto.Integer(self.value + int(value))