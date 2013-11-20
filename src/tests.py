import impl
from lexer import lexFile
import sys
import copy

TestEnvironment = copy.deepcopy(impl.DefaultEnvironment)

def indent(fn):
    def indenter(*args, **kwargs):
        sys.stdout.write("\t")
        return fn(*args, **kwargs)
    return indenter

TestEnvironment.getLibrary('io').decorate('write', indent)
TestEnvironment.getLibrary('io').decorate('p', indent)
TestEnvironment.getLibrary('io').decorate('pf', indent)


vm = impl.VirtualMachine(TestEnvironment)

file = '../lyssa/examples/example.ly'
#file = '../lyssa/examples/types/native.ly'

print "Running %s" % file

stream = lexFile(file)

print stream

out = vm.run(stream)
if not out:
#for e in vm.errs:
    print "\n\t %s\n" % vm.errs[0]

print "\n\t<> %s\n" % repr(out)
