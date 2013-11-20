
import lyb
import meta

lib = lyb.define('Integer')
use = lyb.using(meta.Integer)

lyb.export(lib, 1)(use('Cons'))
lyb.export(lib, 2)(use('Plus'))
lyb.exportVariadic(lib, 2)(use('MultiPus'))
