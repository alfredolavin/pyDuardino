from collections import OrderedDict
from typing import Iterable
import itertools
import operator
import builtins
import ctypes
import re

#global last,first
#last,first = -1, 0

p= print

kilobytes= 1024
newline= '\n'

class dotDict(dict):
  __getattr__ = dict.__getitem__
  __setattr__ = dict.__setitem__
  __delattr__ = dict.__delitem__

class OrderedDotDict(OrderedDict):
  __getattr__ = OrderedDict.__getitem__
  __setattr__ = OrderedDict.__setitem__
  __delattr__ = OrderedDict.__delitem__

class PyObject(ctypes.Structure):
  pass

Py_ssize_t = hasattr(ctypes.pythonapi, 'Py_InitModule4_64') and ctypes.c_int64 or ctypes.c_int

PyObject._fields_ = [('ob_refcnt', Py_ssize_t), ('ob_type', ctypes.POINTER(PyObject)), ]

class SlotsPointer(PyObject):
  _fields_ = [('dict', ctypes.POINTER(PyObject))]

def proxy_builtin(klass):
  name = klass.__name__
  slots = getattr(klass, '__dict__', name)

  pointer = SlotsPointer.from_address(id(slots))
  namespace = {}

  ctypes.pythonapi.PyDict_SetItem(
    ctypes.py_object(namespace),
    ctypes.py_object(name),
    pointer.dict,)

  return namespace[name]

class forEach(list):
  def __init__(self, args, **kwargs):
    super().__init__(args)
    self.fname = kwargs.get('fname')

  def __getattr__(self, key):
    return forEach(self, fname = key)

  def __call__(self, *args, **kwargs):
    if not self.fname:
      raise TypeError()
    func = getattr(operator, self.fname, None) or\
           getattr(builtins, self.fname, None) or\
           getattr(itertools, self.fname, None)
    if func:
      return forEach(list( func(*((item,) + args), **kwargs) for item in self ))
    else:
      return forEach(getattr(item, self.fname)(*args, **kwargs) for item in self)

class _re(str):
  def __init__(self, _fname = None):
    super().__init__()
    self.fname = _fname

  def __getattr__(self, key):
    return _re(self, key)

  def __call__(self, *args, **kwargs):
    if not self.fname:
      raise TypeError()
    func = getattr(re, self.fname, None)

    if func:
      return _re(func(args[0], self, *args[1:], **kwargs))
    else:
      return _re(getattr(self, self.fname)(*args, **kwargs))

def nones(self, n= 10):
  return forEach([None,]*(n or self.len))

def column(self, *names):
  if isinstance(names, str):
    names = [str(names),]
  if len(names) == 1:
    names= names[0]
    return forEach([getattr(i, names) for i in self])
  else:
    return forEach([[getattr(i, name) for name in names] for i in self])

def position_evens(self):
  return forEach(self[1::2])

def position_odds(self):
  return forEach(self[::2])

def value_evens(self):
  return forEach(filter(lambda x: x%2!=0,self))

def value_odds(self):
  return forEach(filter(lambda x: x%2==0,self))

def last(self):
  return (self)[-1]

def middle(self):
  return self[self.len//2]

def first(self):
  return self[0]

def _reversed(self):
  return forEach(reversed(self))

def _len(self):
  return len(list(self))

def exclude(self, *what):
  tmp= forEach(self)
  for item in what:
    try:
      tmp.remove(item)
    except ValueError:
      pass
  return tmp

def _map(self, func):
  tmp= forEach(self)
  for i in range(tmp):
    tmp[i]= eval(func)
  return tmp

def enumerate_me(self, func):
  return forEach(enumerate(self))

def where(self, what):
  if callable(what):
    return forEach(filter(what, self))
  elif isinstance(what, str):
    filter_code = '[item for item in self if item %s]'%what
    return forEach(eval(filter_code))
  else:
    raise TypeError()

def p(*args, **kwargs):
  print(*args, **kwargs)

def eduardinize():
  for built_in_class in (list, tuple, range, set):
    proxy_builtin( built_in_class )['column']= property(column)
    proxy_builtin( built_in_class )['enumerate_me']= property(enumerate_me)
    proxy_builtin( built_in_class )['exclude']= property(exclude)
    proxy_builtin( built_in_class )['first']= property(first)
    proxy_builtin( built_in_class )['forEach']= property(forEach)
    proxy_builtin( built_in_class )['last']= property(last)
    proxy_builtin( built_in_class )['len']= property(_len)
    proxy_builtin( built_in_class )['map']= property(_map)
    proxy_builtin( built_in_class )['middle']= property(middle)
    proxy_builtin( built_in_class )['nones']= property(nones)
    proxy_builtin( built_in_class )['position_evens']= property(position_evens)
    proxy_builtin( built_in_class )['position_odds']= property(position_odds)
    proxy_builtin( built_in_class )['reversed']= property(_reversed)
    proxy_builtin( built_in_class )['evens']= property(value_evens)
    proxy_builtin( built_in_class )['odds']= property(value_odds)
    proxy_builtin( built_in_class )['where']= property(where)

eduardinize()



test='''
sample = list(range(0,10,3))
test = list(range(10)) + ['a','b']
print(test.forEach.str().upper())
print(range(66,88).forEach.chr().lower())
pass'''


def main():
  # Run some test and examples
  print('Running: '+test)
  exec(test)

if __name__ == '__main__':
    main()

