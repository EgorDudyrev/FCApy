"""
This subpackage provides a class FormalContext to work with Formal Context object from FCA theory.
Other modules of the subpackage are implemented to shorten FormalContext class.

Classes
-------
formal_context.FormalContext
bintable.BinTable

Modules
-------
  formal_context:
    Implements Formal Context class
  bintable:
    Implements BinTable class
  converters:
    Contains function to read/write a FormalContext object from/to a file

"""

from .formal_context import FormalContext
from .bintable import BINTABLE_CLASSES, init_bintable
from .converters import read_cxt, read_json, read_csv, from_pandas
