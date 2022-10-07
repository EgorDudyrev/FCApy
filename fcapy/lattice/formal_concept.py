"""
This module provides a class FormalConcept which represents the Formal Concept object from FCA theory

"""
from abc import ABCMeta
from collections.abc import Iterable
import json
import numbers
from typing import Type, List, Dict


class FormalConcept:
    """A class used to represent Formal Concept object from FCA theory

    Notes
    -----
    A Formal Concept `(A,B)` denotes the pair of subset of objects `A` and subset of attributes `B`,
    s.t. objects `A` are all the objects described by attributes `B`
      and attributes `B` are all the attributes which describe objects `A`.

    The set `A` is called `extent`, the set `B` is called `intent`

    """
    JSON_BOTTOM_PLACEHOLDER = {"Inds": (-2,), "Names": ("BOTTOM_PLACEHOLDER",)}

    def __init__(
            self,
            extent_i: List[int], extent: List[str], intent_i: List[int], intent: List[str],
            measures: Dict[str, float] = None, context_hash: int = None, is_monotone: bool = False,
    ):
        """Initialize the FormalConcept object

        Parameters
        ----------
        extent_i: List[int]
            A list of indexes of objects described by intent
        extent: List[int]
            A list of names of objects described by intent
        intent_i: List[int]
            A list of indexes of attributes which describe extent
        intent: List[int]
            A list of names of attributes which describe extent
        measures: Dict[str, float]
            Dict with values of interestingness measures of the concept
        context_hash: int
            Hash value of a FormalContext the FormalConcept is based on.
            Only the concepts from the same FormalContext can be compared
        is_monotone: bool
            A flag whether the concept is describes monotone extent and intent obtained with
            FormalContext(...).extension(..., is_monotone=True) and FormalContext(...).intention(..., is_monotone=True)

        """
        def assert_iterable_type(value, value_name: str = "", value_type: Type = str):
            assert isinstance(value, Iterable) and type(value) != str, \
                f"FormalConcept.__init__. Given {value_name} value should be an iterable but not a string"
            assert all([isinstance(v, value_type) for v in value]),\
                f"FormalConcept.__init__. Given {value_name} values should be of type {value_type}"

        for name in ['extent_i', 'extent', 'intent', 'intent_i']:
            assert_iterable_type(locals()[name], name, numbers.Integral if name.endswith('_i') else str)

        assert len(extent_i) == len(extent), \
            "FormalConcept.__init__ error. extent and extent_i are of different sizes"
        assert len(intent_i) == len(intent), \
            "FormalConcept.__init__ error. intent and intent_i are of different sizes"

        self._extent_i = tuple(extent_i)
        self._extent = tuple(extent)
        self._intent_i = tuple(intent_i)
        self._intent = tuple(intent)

        self._support = len(self._extent_i)
        self.measures = measures if measures is not None else {}
        self._context_hash = context_hash
        self._is_monotone = is_monotone

    @property
    def extent_i(self):
        """The set of indexes of objects described by intent of the FormalConcept"""
        return self._extent_i

    @property
    def extent(self):
        """The set of names of objects described by intent of the FormalConcept"""
        return self._extent

    @property
    def intent_i(self):
        """The set of indexes of attributes which describe the extent of the FormalConcept"""
        return self._intent_i

    @property
    def intent(self):
        """The set of names of attributes which describe the extent of the FormalConcept"""
        return self._intent

    @property
    def support(self):
        """The number of objects described by the intent of the FormalConcept"""
        return self._support

    @property
    def context_hash(self):
        """Hash value of a FormalContext the FormalConcept is based on.

        Only the concepts from the same FormalContext can be compared

        """
        return self._context_hash

    @property
    def is_monotone(self):
        return self._is_monotone

    def __eq__(self, other):
        if self.context_hash != other.context_hash:
            raise NotImplementedError('FormalConcept error. Cannot compare concepts from different contexts')

        if self.is_monotone != other.is_monotone:
            raise ValueError('FormalConcept error. Cannot compare monotone and antimonotone concepts')

        if self.support != other.support:
            return False

        return self <= other

    def __hash__(self):
        return hash((tuple(sorted(self._extent_i)), tuple(sorted(self._intent_i)), self.is_monotone))

    def __le__(self, other):
        """A concept is smaller than the `other concept if its extent is a subset of extent of `other concept"""
        if self._context_hash != other.context_hash:
            raise NotImplementedError('FormalConcept error. Cannot compare concepts from different contexts')

        if self._support > other.support:
            return False

        extent_other = set(other.extent_i)
        for g_i in self._extent_i:
            if g_i not in extent_other:
                return False
        return True

    def __lt__(self, other):
        """A concept is smaller than the `other concept if its extent is a subset of extent of `other concept"""
        if self._context_hash != other.context_hash:
            raise NotImplementedError('FormalConcept error. Cannot compare concepts from different contexts')

        if self._support >= other.support:
            return False

        return self <= other

    def to_dict(self):
        """Convert FormalConcept into a dictionary"""
        concept_info = dict()
        concept_info['Ext'] = {"Inds": self._extent_i, "Names": self._extent, "Count": len(self._extent_i)}
        concept_info['Int'] = {"Inds": self._intent_i, "Names": self._intent, "Count": len(self._intent_i)}
        concept_info['Supp'] = self.support
        for k, v in self.measures.items():
            concept_info[k] = v
        concept_info['Context_Hash'] = self._context_hash
        return concept_info

    @classmethod
    def from_dict(cls, data):
        """Construct a FormalConcept from a dictionary ``data``"""
        if data["Int"] == "BOTTOM":
            data["Int"] = cls.JSON_BOTTOM_PLACEHOLDER
            #data["Int"] = {'Inds': [], "Names": []}

        c = FormalConcept(
            data['Ext']['Inds'], data['Ext'].get('Names', []),
            data['Int']['Inds'], data['Int'].get('Names', []),
            context_hash=data.get('Context_Hash')
        )

        for k, v in data.items():
            if k in ['Int', 'Ext']:
                continue
            c.measures[k] = v
        return c

    def write_json(self, path=None):
        """Save FormalConcept to .json file of return the .json encoded data if ``path`` is None"""
        concept_info = self.to_dict()

        file_data = json.dumps(concept_info)
        if path is None:
            return file_data

        with open(path, 'w') as f:
            f.write(file_data)

    @classmethod
    def read_json(cls, path=None, json_data=None):
        """Load FormalConcept from .json file or from .json encoded string ``json_data``"""
        assert path is not None or json_data is not None,\
            "FormalConcept.read_json error. Either path or data attribute should be given"

        if path is not None:
            with open(path, 'r') as f:
                json_data = f.read()
        data = json.loads(json_data)
        c = cls.from_dict(data)
        return c
