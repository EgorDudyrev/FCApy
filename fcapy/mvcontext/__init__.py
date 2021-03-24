"""
This subpackage provides a class MVContext to work with ManyValued Context object from FCA theory.

Classes
-------
mvcontext.MVContext:
    A class that implements ManyValued Context from FCA theory
pattern_structure.AbstractPS:
    An abstract class that implements basic interface of a Pattern Structure
pattern_structure.IntervalPS:
    A class that implements the work with Interval Pattern Structures (i.e. real valued descriptions of objects)

Modules
-------
  mvcontext:
    Implements MVContext class
  pattern_structure:
    Contains basic classes of Pattern Structures

"""

from .mvcontext import MVContext
from . import pattern_structure as PS
