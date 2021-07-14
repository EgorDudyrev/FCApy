"""
This module provides a class FormalConcept which represents the Formal Concept object from FCA theory

"""
from collections.abc import Iterable
import json
import numbers


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

    def __init__(self, extent_i, extent, intent_i, intent, measures=None, context_hash=None):
        """Initialize the FormalConcept object

        Parameters
        ----------
        extent_i: `list` of `int`
            A list of indexes of objects described by intent
        extent: `list` of `str`
            A list of names of objects described by intent
        intent_i: `list` of `int`
            A list of indexes of attributes which describe extent
        intent: `list` of `str`
            A list of names of attributes which describe extent
        measures: `dict` of type {`str`: `int`}
            Dict with values of interestingness measures of the concept
        context_hash: `int`
            Hash value of a FormalContext the FormalConcept is based on.
            Only the concepts from the same FormalContext can be compared

        """
        def unify_iterable_type(value, name="", value_type=str):
            assert isinstance(value, Iterable) and type(value) != str, \
                f"FormalConcept.__init__. Given {name} value should be an iterable but not a string"
            assert all([isinstance(v, value_type) for v in value]),\
                f"FormalConcept.__init__. Given {name} values should be of type {value_type}"
            return tuple(value)

        self._extent_i = unify_iterable_type(extent_i, "extent_i", value_type=numbers.Integral)
        self._extent = unify_iterable_type(extent, "extent", value_type=str)
        self._intent_i = unify_iterable_type(intent_i, "intent", value_type=numbers.Integral)
        self._intent = unify_iterable_type(intent, "intent", value_type=str)

        assert len(self._extent_i) == len(self._extent),\
            "FormalConcept.__init__ error. extent and extent_i are of different sizes"
        assert len(self._intent_i) == len(self._intent), \
            "FormalConcept.__init__ error. intent and intent_i are of different sizes"

        self._support = len(self._extent_i)
        self.measures = measures if measures is not None else {}
        self._context_hash = context_hash

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

    def __eq__(self, other):
        if self._context_hash != other.context_hash:
            raise NotImplementedError('FormalConcept error. Cannot compare concepts from different contexts')

        if self._support != other.support:
            return False

        return self <= other

    def __hash__(self):
        return hash((tuple(sorted(self._extent_i)), tuple(sorted(self._intent_i))))

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
