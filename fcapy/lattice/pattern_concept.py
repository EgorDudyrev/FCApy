from collections.abc import Iterable
import json
from frozendict import frozendict


class PatternConcept:
    def __init__(self, extent_i, extent, intent_i, intent, pattern_types, measures=None, context_hash=None):
        def unify_iterable_type(value, name="", value_type=str):
            assert isinstance(value, Iterable) and type(value) != str, \
                f"PatternConcept.__init__. Given {name} value should be an iterable but not a string"
            assert all([type(v) == value_type for v in value]),\
                f"PatternConcept.__init__. Given {name} values should be of type {value_type}"
            return tuple(value)

        self._extent_i = unify_iterable_type(extent_i, "extent_i", value_type=int)
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
        return self._extent_i

    @property
    def extent(self):
        return self._extent

    @property
    def intent_i(self):
        return self._intent_i

    @property
    def intent(self):
        return self._intent

    @property
    def pattern_types(self):
        return self._pattern_types

    @property
    def support(self):
        return self._support

    @property
    def context_hash(self):
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
        if self._context_hash != other.context_hash:
            raise NotImplementedError('PatternConcept error. Cannot compare concepts from different contexts')

        if self._support >= other.support:
            return False

        return self <= other

    def to_dict(self):
        raise NotImplementedError

    @classmethod
    def from_dict(cls, data):
        raise NotImplementedError

    def to_json(self, path=None):
        raise NotImplementedError

    @classmethod
    def from_json(cls, path=None, json_data=None):
        raise NotImplementedError
