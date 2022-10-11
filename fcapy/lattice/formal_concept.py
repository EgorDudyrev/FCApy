"""
This module provides a class FormalConcept which represents the Formal Concept object from FCA theory

"""
from abc import ABCMeta, abstractmethod
import json
from pydantic.dataclasses import dataclass
from dataclasses import FrozenInstanceError
from typing import Dict, Container, FrozenSet, Any, List, Tuple
from frozendict import frozendict

JSON_BOTTOM_PLACEHOLDER = {"Inds": (-2,), "Names": ("BOTTOM_PLACEHOLDER",)}


class UnmatchedContextError(ValueError):
    def __str__(self):
        return f'Cannot compare concepts obtained from different contexts'


class UnmatchedMonotonicityError(ValueError):
    def __str__(self):
        return f"Cannot compare monotone and antimonotone concepts"


@dataclass(eq=False)
class AbstractConcept(metaclass=ABCMeta):
    extent_i: Tuple[int, ...]  # Set of indexes of objects described by intent of the concept
    extent: Tuple[str, ...]  # Tuple of names of objects described by intent of the concept
    intent_i: Tuple[int, ...]  # Description of object indices from extent of the concept
    intent: Tuple[str, ...]  # Description of object names from extent of the concept
    measures: Dict[str, float] = frozendict({})  # Dict with values of interestingness measures of the concept
    context_hash: int = None  # Hash value of a FormalContext the FormalConcept is based on
    is_monotone: bool = False  # "Bigger extent->bigger concept" if False else "smaller extent->bigger concept"

    def __setattr__(self, key, value):
        if key in self.__dict__ and key in {'extent_i', 'extent', 'intent_i', 'intent', 'context_hash', 'is_monotone'}:
            raise FrozenInstanceError(f'Value of {key} cannot be updated')

        super(AbstractConcept, self).__setattr__(key, value)

    @property
    def support(self):
        return len(self.extent_i)

    def __eq__(self, other):
        if self.context_hash != other.context_hash:
            raise UnmatchedContextError

        if self.is_monotone != other.is_monotone:
            raise UnmatchedMonotonicityError

        if self.support != other.support:
            return False

        return self.extent_i == other.extent_i

    def __hash__(self):
        return hash(self.extent_i)

    def __le__(self, other: 'AbstractConcept'):
        """A concept is smaller than the `other concept if its extent is a subset of extent of `other concept"""
        if self.context_hash != other.context_hash:
            raise UnmatchedContextError

        if self.is_monotone != other.is_monotone:
            raise UnmatchedMonotonicityError

        lesser, greater = (self, other) if not self.is_monotone else (other, self)

        if lesser.support > greater.support:
            return False

        greater_ext_i = set(greater.extent_i)
        for g_i in lesser.extent_i:
            if g_i not in greater_ext_i:
                return False
        return True

    def __lt__(self, other: 'AbstractConcept'):
        """A concept is smaller than the `other concept if its extent is a subset of extent of `other concept"""
        if self.support == other.support:  # i.e. they definitely not equal
            return False

        return self <= other

    @abstractmethod
    def to_dict(self, objs_order: List[str], attrs_order: List[str]) -> Dict[str, Any]:
        ...

    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AbstractConcept':
        ...

    def write_json(self, objs_order: List[str], attrs_order: List[str], path: str = None):
        """Save FormalConcept to .json file of return the .json encoded data if ``path`` is None"""
        concept_info = self.to_dict(objs_order, attrs_order)

        file_data = json.dumps(concept_info)
        if path is None:
            return file_data

        with open(path, 'w') as f:
            f.write(file_data)

    @classmethod
    def read_json(cls, path: str = None, json_data: str = None) -> 'AbstractConcept':
        """Load FormalConcept from .json file or from .json encoded string ``json_data``"""
        assert path is not None or json_data is not None,\
            "FormalConcept.read_json error. Either path or data attribute should be given"

        if path is not None:
            with open(path, 'r') as f:
                json_data = f.read()
        data = json.loads(json_data)
        c = cls.from_dict(data)
        return c


@dataclass(eq=False)
class FormalConcept(AbstractConcept):
    """A class used to represent Formal Concept object from FCA theory

        Notes
        -----
        A Formal Concept `(A,B)` denotes the pair of subset of objects `A` and subset of attributes `B`,
        s.t. objects `A` are all the objects described by attributes `B`
          and attributes `B` are all the attributes which describe objects `A`.

        The set `A` is called `extent`, the set `B` is called `intent`

        """

    intent_i: Tuple[int, ...]  # Description of object indices from extent of the concept
    intent: Tuple[str, ...]  # Description of object names from extent of the concept

    def to_dict(self, objs_order: List[str], attrs_order: List[str]) -> Dict[str, Any]:
        """Convert FormalConcept into a dictionary"""
        def sort_set(set_, key=None):
            return tuple(sorted(set_, key=key))

        obj_idxs_map = {g: i for i, g in enumerate(objs_order)}
        attrs_idxs_map = {m: i for i, m in enumerate(attrs_order)}

        concept_info = dict()
        concept_info['Ext'] = {
            "Inds": sort_set(self.extent_i),
            "Names": sort_set(self.extent, key=lambda g: obj_idxs_map[g]),
            "Count": len(self.extent_i)
        }
        concept_info['Int'] = {
            "Inds": sort_set(self.intent_i),
            "Names": sort_set(self.intent, key=lambda m: attrs_idxs_map[m]),
            "Count": len(self.intent_i)
        }
        concept_info['Supp'] = self.support
        for k, v in self.measures.items():
            concept_info[k] = v
        concept_info['Context_Hash'] = self.context_hash
        concept_info['Monotone'] = self.is_monotone
        return concept_info

    @classmethod
    def from_dict(cls, data):
        """Construct a FormalConcept from a dictionary ``data``"""
        if data["Int"] == "BOTTOM":
            data["Int"] = JSON_BOTTOM_PLACEHOLDER

        c = FormalConcept(
            data['Ext']['Inds'], data['Ext'].get('Names', []),
            data['Int']['Inds'], data['Int'].get('Names', []),
            context_hash=data.get('Context_Hash'),
            is_monotone=data.get('Monotone', False)
        )

        for k, v in data.items():
            if k in ['Int', 'Ext']:
                continue
            c.measures[k] = v
        return c
