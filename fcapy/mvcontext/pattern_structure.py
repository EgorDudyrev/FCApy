"""
This module contains classes of basic Pattern Structures which allow FCA to work with data of any complex description
"""

from collections.abc import Iterable
import math
from numbers import Number
import json
from typing import Sequence

from fcapy import LIB_INSTALLED
if LIB_INSTALLED['numpy']:
    import numpy as np


class AbstractPS:
    r"""
    An abstract class to provide an interface for any Pattern Structure (PS)

    Notes
    -----
    A pattern structure D is any kind of description of the set of objects G
    for which we can define two functions:

    1) Given description d \\subseteq D we can select a subset of objects A = d' which share this description
    2) Given a subset of objects A \\subseteq G we can determine their common description d = A'

    """
    def __init__(self, data, name=None):
        """Initialize the PatternStructure with some ``data`` and the distinct ``name`` of pattern structure"""
        self.data = data
        self._name = name

    def intention_i(self, object_indexes):
        """Select a common description of objects ``object_indexes``"""
        raise NotImplementedError

    def extension_i(self, description, base_objects_i=None):
        """Select a subset of objects of ``base_objects_i`` which share ``description``"""
        raise NotImplementedError

    @property
    def data(self):
        """The data for PatternStructure to work with"""
        return self._data

    @data.setter
    def data(self, value):
        if '_data' in self.__dict__:
            assert len(value) == len(self._data), "Length of new data does not match the length of old one"
        self._data = self._transform_data(value)

    @property
    def name(self):
        """The distinct name of a PatternStructure"""
        return self._name

    def description_to_generators(self, description, projection_num):
        """Convert a closed ``description`` into a set of generators of this closed description (Optional)"""
        raise NotImplementedError

    def generators_to_description(self, generators):
        """Combine a set of ``generators`` into one closed description (Optional)"""
        raise NotImplementedError

    def __repr__(self):
        str_ = f"{self.__class__.__name__} '{self._name}'"
        return str_

    def __eq__(self, other):
        return self._data == other.data and self._name == other.name

    def __hash__(self):
        return hash((self._name, tuple(self._data)))

    def __getitem__(self, item):
        if isinstance(item, Iterable):
            data = [self._data[g] for g in item]
        else:
            data = self._data[item]
        return data

    def to_numeric(self):
        """Convert the complex ``data`` of the PatternStructure to a set of numeric columns"""
        raise NotImplementedError

    def generators_by_intent_difference(self, new_intent, old_intent):
        """Compute the set of generators to select the ``new_intent`` from ``old_intent``"""
        raise NotImplementedError

    @staticmethod
    def intersect_descriptions(a, b):
        """Compute the maximal common description of two descriptions `a` and `b`"""
        raise NotImplementedError

    @staticmethod
    def unite_descriptions(a, b):
        """Compute the minimal description includes the descriptions `a` and `b`"""
        raise NotImplementedError

    @classmethod
    def leq_descriptions(cls, a, b) -> bool:
        """Check If description `a` is 'smaller' (more general) then description `b`"""
        return cls.intersect_descriptions(a,b) == a

    @classmethod
    def from_json(cls, x_json):
        """Load description from ``x_json`` .json format"""
        return json.loads(x_json)

    @classmethod
    def to_json(cls, x):
        """Convert description ``x`` into .json format"""
        return json.dumps(x)

    @staticmethod
    def _transform_data(values: list) -> list:
        return values

    def describe_pattern(self, value) -> str:
        return f"{self.name}: {value}"


class AttributePS(AbstractPS):
    """
    A pattern structure to mimic an attribute of formal context.
    That is, there are only two possible values: True and False. And False means not "not True" but "anything"

    """
    def intention_i(self, object_indexes: list[int]):
        """Select a common description of objects ``object_indexes``"""
        if not object_indexes:
            return False

        return all(self._data[g_i] for g_i in object_indexes)

    def extension_i(self, description: bool, base_objects_i=None):
        """Select a subset of objects of ``base_objects_i`` which share ``description``"""
        base_objects_i = range(len(self._data)) if base_objects_i is None else base_objects_i
        if not description:
            return list(base_objects_i)

        return [g_i for g_i in base_objects_i if self._data[g_i]]

    def description_to_generators(self, description, projection_num):
        """Convert a closed ``description`` into a set of generators of this closed description (Optional)"""
        return [description]

    def generators_to_description(self, generators):
        """Combine a set of ``generators`` into one closed description (Optional)"""
        return all(generators)

    def to_numeric(self):
        """Convert the complex ``data`` of the PatternStructure to a set of numeric columns"""
        return [int(x) for x in self.data], self.name

    def generators_by_intent_difference(self, new_intent, old_intent):
        """Compute the set of generators to select the ``new_intent`` from ``old_intent``"""
        if new_intent == old_intent:
            return []

        if not new_intent and old_intent:
            return []

        return [True]

    @staticmethod
    def intersect_descriptions(a, b):
        """Compute the maximal common description of two descriptions `a` and `b`"""
        return a and b

    @staticmethod
    def unite_descriptions(a, b):
        """Compute the minimal description includes the descriptions `a` and `b`"""
        return a or b

    @staticmethod
    def _transform_data(values: list) -> list[bool]:
        return [bool(v) for v in values]

    def describe_pattern(self, value) -> str:
        return self.name if value else ''


class SetPS(AbstractPS):
    """
    A pattern structure describing categorical data.

    """
    def intention_i(self, object_indexes) -> set:
        """Select a common description of objects ``object_indexes``"""
        intent = set()
        for g_i in object_indexes:
            intent |= self._data[g_i]
        return intent

    def extension_i(self, description: set or None, base_objects_i=None):
        """Select a subset of objects of ``base_objects_i`` which share ``description``"""
        if description is None:
            return []

        base_objects_i = range(len(self._data)) if base_objects_i is None else base_objects_i
        return [g_i for g_i in base_objects_i if self._data[g_i] & description == self._data[g_i]]

    def to_numeric(self):
        """Convert the complex ``data`` of the PatternStructure to a set of numeric columns"""
        uniq_vals = set()
        for v in self.data:
            uniq_vals |= v
        uniq_vals = sorted(uniq_vals)
        vals_to_cols_map = {v: i for i, v in enumerate(uniq_vals)}
        zero_row = [False for _ in uniq_vals]

        num_data = []
        for row_vals in self.data:
            x_num = zero_row.copy()
            for v in row_vals:
                x_num[vals_to_cols_map[v]] = True
            num_data.append(x_num)
        return num_data, [f"{self.name}_{v}" for v in uniq_vals]

    @staticmethod
    def intersect_descriptions(a: set, b: set) -> set:
        """Compute the maximal common description of two descriptions `a` and `b`"""
        return a | b

    @staticmethod
    def unite_descriptions(a: set, b: set) -> set:
        """Compute the minimal description includes the descriptions `a` and `b`"""
        return a | b

    @staticmethod
    def _transform_data(values: list[Iterable or str]) -> list[set]:
        return [set(v) if isinstance(v, Iterable) and not isinstance(v, str) else {v} for v in values]

    def describe_pattern(self, value: set) -> str:
        return f"{self.name}: {', '.join([str(v) for v in value])}" if value else ''

    @classmethod
    def to_json(cls, x: Iterable) -> str:
        return super(SetPS, cls).to_json(sorted(x))

    @classmethod
    def from_json(cls, x_json: str) -> set:
        return set(super(SetPS, cls).from_json(x_json))


class IntervalPS(AbstractPS):
    r"""
    An class to work with Interval Pattern Structures from FCA theory

    Notes
    -----
    An Interval Pattern Structure describes any object g with a closed interval g' = [g_{min}, g_{max}]
    Thus:

    1) Given an interval [a, b] we can select objects A which description falls into an interval [a,b]:
        A = {g \in G | a <= g_{min} & g_{max} <= b }
    2) Given a set of objects A \subseteq G we can determine their common description [a, b]: \
         a = min({g_{min} | g \in A})
         b = max({g_{max} | g \in A})

    If object description is defined by a single number x we turn it into an interval [x, x]

    """
    @staticmethod
    def _transform_data(values: Iterable[Sequence[float] or Number]) -> list[tuple[float, float]]:
        data = []
        for x in values:
            new_x: tuple[float, float] = None

            if isinstance(x, Sequence) and len(x) == 2:
                new_x = x
            if isinstance(x, Sequence) and len(x) == 1:
                new_x = (x[0], x[0])
            if isinstance(x, Number):
                new_x = (x, x)

            if new_x is None:
                raise TypeError(
                    f"Input data of {type(x)} is not supported by IntervalPS. "
                    f"Possible types are: any of Number, Sequence of 1 or 2 elements"
                )
            data.append((float(new_x[0]), float(new_x[1])))

        return data

    def intention_i(self, object_indexes: Sequence[int]) -> tuple[float, float] or None:
        """Select a common interval description for all objects from ``object_indexes``"""
        if len(object_indexes) == 0:
            return None

        min_, max_ = self._data[object_indexes[0]]
        for g_i in object_indexes[1:]:
            v_min, v_max = self._data[g_i]
            min_ = v_min if v_min < min_ else min_
            max_ = v_max if v_max > max_ else max_
        return min_, max_

    def extension_i(self, description: tuple[float, float] or float or None, base_objects_i: list[int] = None) -> list[int]:
        """Select a set of indexes of objects from ``base_objects_i`` which fall into interval of ``description``"""
        if description is None:
            return []

        min_, max_ = description if not isinstance(description, Number) else (description, description)

        base_objects_i = range(len(self._data)) if base_objects_i is None else base_objects_i
        g_is = [int(g_i) for g_i in base_objects_i if min_ <= self._data[g_i][0] and self._data[g_i][1] <= max_]
        return g_is

    def description_to_generators(self, description: tuple[float, float], projection_num: int)\
            -> list[tuple[float, float] or None]:
        """Convert the closed interval of ``description`` into a set of more broader intervals that generate it

        For example, an interval (-inf, 10] can describe the same set of objects as a closed interval [0, 10].
        Thus we say that an interval (-int, 10] is a generator of a closed description [0,10].

        The projections of IntervalPS are considered as following:
            Projection 0: an interval (-inf, inf)
            Projection 1: an interval (-inf, x] or [x, inf), where x is a real number
            Projection 2: a closed interval [a, b], where a,b are real numbers

        Parameters
        ----------
        description: `tuple` of `float`
            A closed description to turn into generators
        projection_num: `int`
            An index of IntervalPS projection for generators to belong to

        Returns
        -------
        generators: `list` of `tuple`
            A list of generators of a closed ``description``

        """
        if description is None:
            return [None]

        if not isinstance(description, Iterable):
            description = (description, description)
        description = tuple(description)
        if projection_num == 0:
            generators = [(-math.inf, math.inf)]
        elif projection_num == 1:
            generators = [(-math.inf, description[1]), (description[0], math.inf)]
        else:
            generators = [(description[0], description[1])]
        return generators

    def generators_to_description(self, generators: list[tuple[float, float] or None]) -> tuple[float, float] or None:
        """Combine a set of ``generators`` into a single closed description"""
        if any([gen is None for gen in generators]):
            return None

        generators = [tuple(gen) if isinstance(gen, Iterable) else (gen, gen) for gen in generators]
        generators = [list(row)for row in zip(*generators)]
        description = (max(generators[0]), min(generators[1]))
        assert description[0] <= description[1],\
            f"IntervalPS.generators_to_description error. Generators are wrongly defined. " \
            f"Right border of result description interval is smaller than the left one: {description}"
        if description[0] == description[1]:
            description = description[0]
        return description

    def __eq__(self, other):
        same_data = self._data == other.data
        return same_data and self._name == other.name

    def __hash__(self):
        return hash((self._name, tuple([tuple(x) for x in self._data])))

    def to_numeric(self):
        """Turn `IntervalPS` data into a set of numeric columns and their names"""
        return self._data, (f"{self.name}_from", f"{self.name}_to")

    def generators_by_intent_difference(self, new_intent: tuple[float, float], old_intent: tuple[float, float])\
            -> list[tuple[float, float] or None]:
        """Compute the set of generators to select the ``new_intent`` from ``old_intent``"""
        if new_intent is None:
            return [None]

        left_eq = old_intent[0] == new_intent[0]
        right_eq = old_intent[1] == new_intent[1]

        if left_eq and right_eq:
            return []
        if left_eq and not right_eq:
            return [(-math.inf, new_intent[1])]
        if not left_eq and right_eq:
            return [(new_intent[0], math.inf)]
        return [self.generators_to_description([new_intent, old_intent])]

    @staticmethod
    def intersect_descriptions(a: tuple[float, float], b: tuple[float, float]) -> tuple[float, float] or None:
        """Compute the maximal common description of two descriptions `a` and `b`"""
        intersection = (max(a[0], b[0]), min(a[1], b[1]))
        if intersection[0] > intersection[1]:
            return None
        return intersection

    @staticmethod
    def unite_descriptions(a: tuple[float, float], b: tuple[float, float]) -> tuple[float, float]:
        """Compute the minimal description includes the descriptions `a` and `b`"""
        unity = (min(a[0], b[0]), max(a[1], b[1]))
        return unity

    @classmethod
    def to_json(cls, x: tuple[float, float] or None) -> str:
        """Convert description ``x`` into .json format"""
        x = [float(x[0]), float(x[1])] if x is not None else None
        return json.dumps(x)

    @classmethod
    def from_json(cls, x_json: str) -> tuple[float, float] or None:
        """Load description from ``x_json`` .json format"""
        x = json.loads(x_json)
        return tuple(x) if x is not None else None

    def describe_pattern(self, value: tuple[float, float] or None) -> str:
        return f"{self.name}: ({value[0]}, {value[1]})" if value is not None else ''


class IntervalNumpyPS(IntervalPS):
    r"""
    An class to work with Interval Pattern Structures from FCA theory via Numpy package

    Notes
    -----
    An Interval Pattern Structure describes any object g with a closed interval g' = [g_{min}, g_{max}]
    Thus:

    1) Given an interval [a, b] we can select objects A which description falls into an interval [a,b]:
        A = {g \in G | a <= g_{min} & g_{max} <= b }
    2) Given a set of objects A \subseteq G we can determine their common description [a, b]: \
         a = min({g_{min} | g \in A})
         b = max({g_{max} | g \in A})

    If object description is defined by a single number x we turn it into an interval [x, x]

    """
    @classmethod
    def _transform_data(cls, values: Iterable) -> np.ndarray:
        return np.array(super(IntervalNumpyPS, cls)._transform_data(values))

    def intention_i(self, object_indexes: list[int]) -> tuple[float, float] or None:
        """Select a common interval description for all objects from ``object_indexes``"""
        if len(object_indexes) == 0:
            return None

        return float(self._data[object_indexes, 0].min()), float(self._data[object_indexes, 1].max())

    def extension_i(self, description: tuple[float, float] or None, base_objects_i: list[int] = None) -> list[int]:
        """Select a set of indexes of objects from ``base_objects_i`` which fall into interval of ``description``"""
        if description is None:
            return []

        min_, max_ = description
        if base_objects_i is None:
            flg = (min_ <= self._data[:,0]) & (self._data[:, 1] <= max_)
        else:
            flg = (min_ <= self._data[base_objects_i, 0]) & (self._data[base_objects_i, 1] <= max_)

        return flg.nonzero()[0].tolist()

    def __eq__(self, other):
        same_data = (self._data == other.data).all()
        return same_data and self._name == other.name

    @classmethod
    def to_json(cls, x: tuple[float, float] or None) -> str:
        if isinstance(x, np.ndarray):
            x = x.tolist()
        return super(IntervalNumpyPS, cls).to_json(x)

