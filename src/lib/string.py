from onto
import lyb
from src import onto, lyb

@lyb.include
class String(onto.String):
    def Cons(self):
        return onto.String(self.value)

    @lyn.export(1)
    @lyb.requires(onto.String)
    def Plus(self, string):
        return onto.String(self.value + str(string))

    @lyb.export(1)
    @lyb.requires(onto.String)
    def MultiPlus(self, *strings):
        return onto.String(self.value + "".join(map(str, strings)))

    @lyb.exportVariadic(1)
    @lyb.requires(onto.String)
    def f(self, str, *args):
        return String(str.value % tuple(lyb.values(args)))