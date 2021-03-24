"""
This module provides a class PatternConcept which represents the Pattern Concept object from FCA theory

"""
from collections.abc import Iterable
import json
from frozendict import frozendict
import numbers


class PatternConcept:
    """A class used to represent Pattern Concept object from FCA theory

    Notes
    -----
    A Pattern Concept `(A, d)` denotes the pair of subset of objects `A` and a (complex) description `d`,
    s.t. objects `A` are all the objects described by description `d`
      and description `d` is the most accurate description of objects `A`

    The set `A` is called `extent`, the description `d` is called `intent`

    The only restriction to a type description `d` is that should encoded by Pattern Structures
    from the module `fcapy.mvcontext.pattern_structure`

    """
    def __init__(self, extent_i, extent, intent_i, intent, pattern_types, measures=None, context_hash=None):
        """Initialize the PatternConcept object

        Parameters
        ----------
        extent_i: `list` of `int`
            A list of indexes of objects described by intent
        extent: `list` of `str`
            A list of names of objects described by intent
        intent_i: `dict` of type {`idx`: description}
            A dict of the most specific descriptions of extent by each of pattern structure from ``pattern_types``
            indexed by the index of pattern structure in ``pattern_types``
        intent: `dict` of type {`str`: description}
            A dict of the most specific descriptions of extent by each of pattern structure from ``pattern_types``
            indexed by the name of pattern structure in ``pattern_types``
        pattern_types: `list` of subtypes of `PatternStructure`
            A set of subtypes of `PatternStructures` used to encode the descriptions from ``intent``
        measures: `dict` of type {`str`: `int`}
            Dict with values of interestingness measures of the concept
        context_hash: `int`
            Hash value of a MVContext the PatternConcept is based on.
            Only the concepts from the same MVContext can be compared

        """
        def unify_iterable_type(value, name="", value_type=str):
            assert isinstance(value, Iterable) and type(value) != str, \
                f"PatternConcept.__init__. Given {name} value should be an iterable but not a string"
            assert all([isinstance(v, value_type) for v in value]),\
                f"PatternConcept.__init__. Given {name} values should be of type {value_type}"
            return tuple(value)

        self._extent_i = unify_iterable_type(extent_i, "extent_i", value_type=numbers.Integral)
        self._extent = unify_iterable_type(extent, "extent", value_type=str)
        self._intent_i = frozendict(intent_i)
        self._intent = frozendict(intent)

        assert len(self._extent_i) == len(self._extent),\
            "PatternConcept.__init__ error. extent and extent_i are of different sizes"
        assert len(self._intent_i) == len(self._intent), \
            "PatternConcept.__init__ error. intent and intent_i are of different sizes"

        self._pattern_types = pattern_types

        self._support = len(self._extent_i)
        self.measures = measures if measures is not None else {}
        self._context_hash = context_hash

    @property
    def extent_i(self):
        """The set of indexes of objects described by intent of the PatternConcept"""
        return self._extent_i

    @property
    def extent(self):
        """The set of names of objects described by intent of the PatternConcept"""
        return self._extent

    @property
    def intent_i(self):
        """A dict of the most specific descriptions of extent by each of pattern structure from ``pattern_types``

        indexed by the index of pattern structure in ``pattern_types``

        """
        return self._intent_i

    @property
    def intent(self):
        """A dict of the most specific descriptions of extent by each of pattern structure from ``pattern_types``

        indexed by the name of pattern structure in ``pattern_types``

        """
        return self._intent

    @property
    def pattern_types(self):
        """A set of subtypes of `PatternStructures` used to encode the descriptions from ``intent``"""
        return self._pattern_types

    @property
    def support(self):
        """The number of objects described by the intent of the PatternConcept"""
        return self._support

    @property
    def context_hash(self):
        """Hash value of a MVContext the PatternConcept is based on.

        Only the concepts from the same MVContext can be compared

        """
        return self._context_hash

    def __eq__(self, other):
        if self._context_hash != other.context_hash:
            raise NotImplementedError('FormalConcept error. Cannot compare concepts from different contexts')

        if self._support != other.support:
            return False

        return self <= other

    def __hash__(self):
        return hash((tuple(sorted(self._extent_i)), frozendict(self._intent_i)))

    def __le__(self, other):
        """A concept is smaller than the ``other`` concept if its extent is a subset of extent of ``other`` concept"""
        if self._context_hash != other.context_hash:
            raise NotImplementedError('PatternConcept error. Cannot compare concepts from different contexts')

        if self._support > other.support:
            return False

        extent_other = set(other.extent_i)
        for g_i in self._extent_i:
            if g_i not in extent_other:
                return False
        return True

    def __lt__(self, other):
        """A concept is smaller than the ``other`` concept if its extent is a subset of extent of ``other`` concept"""
        if self._context_hash != other.context_hash:
            raise NotImplementedError('PatternConcept error. Cannot compare concepts from different contexts')

        if self._support >= other.support:
            return False

        return self <= other

    def to_dict(self):
        """Convert PatternConcept into a dictionary"""
        raise NotImplementedError

    @classmethod
    def from_dict(cls, data):
        """Construct a PatternConcept from a dictionary ``data``"""
        raise NotImplementedError

    def to_json(self, path=None):
        """Save PatternConcept to .json file of return the .json encoded data if ``path`` is None"""
        raise NotImplementedError

    @classmethod
    def from_json(cls, path=None, json_data=None):
        """Load PatternConcept from .json file or from .json encoded string ``json_data``"""
        raise NotImplementedError
