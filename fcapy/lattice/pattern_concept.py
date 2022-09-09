"""
This module provides a class PatternConcept which represents the Pattern Concept object from FCA theory

"""
from collections.abc import Iterable
import json
from frozendict import frozendict
import numbers
from typing import Tuple

from fcapy.mvcontext import PS


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
    JSON_BOTTOM_PLACEHOLDER = {"Inds": (-2,), "Names": ("BOTTOM_PLACEHOLDER",)}

    def __init__(self, extent_i, extent, intent_i, intent,
                 pattern_types: Tuple[PS.AbstractPS], attribute_names: Tuple[str],
                 measures=None, context_hash=None):
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
        attribute_names: `tuple` of `str`
            A mapping from an index of pattern_type to its name
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

        self._attribute_names = attribute_names
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
        #return hash((tuple(sorted(self._extent_i)), frozendict(self._intent_i)))
        return hash((tuple(sorted(self._extent_i)), self._context_hash))

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

    def to_dict(self, json_ready : bool = False):
        """Convert FormalConcept into a dictionary"""
        concept_info = dict()
        concept_info['Ext'] = {"Inds": self._extent_i, "Names": self._extent, "Count": len(self._extent_i)}
        concept_info['Int'] = {"Inds": self._intent_i, "Names": self._intent, "Count": len(self._intent_i),
                               "PTypes": self._pattern_types, "AttrNames": self._attribute_names}
        concept_info['Supp'] = self.support
        for k, v in self.measures.items():
            concept_info[k] = v
        concept_info['Context_Hash'] = self._context_hash

        if json_ready:
            int_dict = concept_info['Int']
            int_dict['Inds'] = {k: int_dict['PTypes'][int_dict['AttrNames'][k]].to_json(v)
                                for k, v in int_dict['Inds'].items()}
            int_dict['Names'] = {k: int_dict['PTypes'][k].to_json(v) for k, v in int_dict['Names'].items()}
            int_dict['PTypes'] = {k: v.__name__ for k, v in int_dict['PTypes'].items()}

        return concept_info

    @classmethod
    def from_dict(cls, data, json_ready: bool = False, pattern_types: Tuple[PS.AbstractPS] = None):
        """Construct a FormalConcept from a dictionary ``data``

        Parameters
        ----------
        data: `dict`
            Data to load concept from
        json_ready: `bool`
            A flag whether to load the json compatible dictionary
        pattern_types: `tuple` of pattern structure types
            A tuple of pattern structure classes that encounter in the dictionary ``data``

        Returns
        -------
        `Pattern Concept`
        """
        if data["Int"] == "BOTTOM":
            data["Int"] = cls.JSON_BOTTOM_PLACEHOLDER
            #data["Int"] = {'Inds': [], "Names": []}

        if json_ready:
            pattern_types = {pt.__name__: pt for pt in pattern_types} if pattern_types is not None else []

            int_dict = data['Int']
            int_dict['PTypes'] = {k: getattr(PS, v) if v in dir(PS) else pattern_types[v] for k, v in
                                  int_dict['PTypes'].items()}
            int_dict['Inds'] = frozendict({int(k): int_dict['PTypes'][int_dict['AttrNames'][int(k)]].from_json(v)
                                           for k, v in int_dict['Inds'].items()})
            int_dict['Names'] = frozendict({k: int_dict['PTypes'][k].from_json(v)
                                            for k, v in int_dict['Names'].items()})

        c = PatternConcept(
            data['Ext']['Inds'], data['Ext'].get('Names', []),
            data['Int']['Inds'], data['Int'].get('Names', []),
            data['Int']['PTypes'], data['Int']['AttrNames'],
            context_hash=data.get('Context_Hash')
        )

        for k, v in data.items():
            if k in ['Int', 'Ext']:
                continue
            c.measures[k] = v
        return c

    def write_json(self, path=None):
        """Save PatternConcept to .json file of return the .json encoded data if ``path`` is None"""
        concept_dict = self.to_dict(json_ready=True)

        file_data = json.dumps(concept_dict)
        if path is None:
            return file_data

        with open(path, 'w') as f:
            f.write(file_data)

    @classmethod
    def read_json(cls, path: str = None, json_data: str = None, pattern_types: Tuple[PS.AbstractPS] = None):
        """Load PatternConcept from .json file or from .json encoded string ``json_data``

        Parameters
        ----------
        path: `str`
            Path to the .json file to read from (optional)
        json_data: `str`
            Json data to read from (optional)
        pattern_types: `tuple[AbstractPS]`
            Tuple of additional Pattern Structures not defined in fcapy.mvcontext.pattern_structure
            that may encounter in the read data
        Returns
        -------
        c: `PatternConcept`
        """
        assert path is not None or json_data is not None,\
            "FormalConcept.read_json error. Either path or data attribute should be given"

        if path is not None:
            with open(path, 'r') as f:
                json_data = f.read()
        c_dict = json.loads(json_data)

        c = cls.from_dict(c_dict, json_ready=True, pattern_types=pattern_types)
        return c
