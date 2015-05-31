from copy import copy
import inspect
from itertools import takewhile
from os import path
import types


class GeneratedFunction(object):
    """
    Simple holder for functions' declaration/implementation generated code
    """
    def __init__(self, name, declaration=None, implementation=None):
        self.name = name
        self.declaration = declaration
        self.implementation = implementation


class FieldAccessor(GeneratedFunction):
    """Generated function that expose field read access"""
    def __init__(self, name, field, field_type, c_declaration, **kwargs):
        super(FieldAccessor, self).__init__(name, **kwargs)
        self.field = field
        self.field_type = field_type
        self.c_declaration = c_declaration


class TypeDeclaration(object):
    """Simple holder for generated type declarations"""

    def __init__(self, type, public_part, private_part):
        self.type = type
        self.public_part = public_part
        self.private_part = private_part

    @staticmethod
    def render(renderer, template_name, t_env, type, **kwargs):
        """
        Helper to create a TypeDeclaration out of the instantiations of a
        single template.
        """
        public_part = renderer.render(template_name, t_env, private_part=False,
                                      **kwargs)
        private_part = renderer.render(template_name, t_env, private_part=True,
                                       **kwargs)
        return TypeDeclaration(type, public_part, private_part)


class GeneratedParser(object):
    """Simple holder for generated parsers"""

    def __init__(self, name, spec, body):
        self.name = name
        self.spec = spec
        self.body = body


class StructEq(object):
    """ Mixin for structural equality.
    """
    def __eq__(self, other):
        if type(other) is type(self):
            if hasattr(self, "_eq_keys"):
                eq_keys = self._eq_keys
            elif hasattr(self, "_excl_eq_keys"):
                eq_keys = set(self.__dict__.keys()) ^ set(self._excl_eq_keys)
            else:
                return self.__dict__ == other.__dict__

            return all(v == other.__dict__[k] for k, v in self.__dict__
                       if k in eq_keys)

        return False


def unescape(char):
    if char[0] == "\\":
        return char[1:]
    return char


def copy_with(obj, **kwargs):
    """
    :type obj: T
    :rtype: T
    """
    c = copy(obj)

    for k, v in kwargs.items():
        setattr(c, k, v)

    return c


def make_tupled(fn):

    def _call(tpl):
        return fn(*tpl)

    return _call


def extract(lst, idx=0, alt=None):
    if lst:
        return lst[idx]
    else:
        return alt


def isalambda(v):
    return isinstance(v, type(lambda: None)) and v.__name__ == '<lambda>'


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


def printcol(msg, color):
    print "{0}{1}{2}".format(color, msg, Colors.ENDC)


def file_path(f):
    return path.dirname(path.abspath(f))


def common_ancestor(*classes):
    """Return the bottom-most common parent class for all `classes`."""
    rmro = lambda k: reversed(k.mro())
    result = list(takewhile(lambda a: len(set(a)) == 1,
                            zip(*map(rmro, classes))))[-1][0]
    return result


def memoized(func):
    """
    Decorator to memoize a function.

    This function must be passed only hashable arguments.
    """
    cache = {}

    def wrapper(*args, **kwargs):
        key = (args, tuple(kwargs.items()))
        try:
            result = cache[key]
        except KeyError:
            result = func(*args, **kwargs)
            cache[key] = result
            result = result
        return result

    return wrapper


def type_check(klass):
    """Return a predicate that will return true if its parameter is a subclass
    of `klass`
    :param type klass: Class to check against
    :rtype: (T) -> bool
    """
    return lambda t: t and issubclass(t, klass)


def type_check_instance(klass):
    """Return a predicate that will return true if its parameter is a subclass
    of `klass`
    :param type klass: Class to check against
    :rtype: (T) -> bool
    """
    return lambda t: isinstance(t, klass)
