"""
This module contains classes of basic Pattern Structures which allow FCA to work with data of any complex description
"""

from collections.abc import Iterable
import math
from numbers import Number
import json

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
        self._data = data
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
        assert len(value) == len(self._data), "Length of new data does not match the length of old one"
        self._data = value

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
    def to_json(cls, x):
        """Convert description ``x`` into .json format"""
        raise NotImplementedError

    @classmethod
    def from_json(cls, x_json):
        """Load description from ``x_json`` .json format"""
        raise NotImplementedError


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
    def __init__(self, data, name=None):
        """Initialize the Interval PS with the ``data`` and a distinct ``name``"""
        super(IntervalPS, self).__init__(data, name)
        self.data = data

    @property
    def data(self):
        """The data for IntervalPS to work with (`list` of `tuple` representing the intervals)"""
        return self._data

    @data.setter
    def data(self, value):
        assert len(value) == len(self._data), "Length of new data does not match the length of old one"

        self._data = []
        for x in value:
            if isinstance(x, Iterable) and len(x) == 2:
                new_x = x
            elif isinstance(x, Iterable) and len(x) == 1:
                new_x = (x[0], x[0])
            elif isinstance(x, Number):
                new_x = (x, x)
            else:
                raise TypeError(
                    f"Input data of {type(x)} is not supported by IntervalPS. "
                    f"Possible types are: any of Number, iterables of 1 or 2 elements"
                )
            self._data.append(new_x)

        if LIB_INSTALLED['numpy']:
            self._data = np.array(self._data, dtype=np.float32)
            # TODO: Rewrite sorting to ascending (right border of interval)
            # TODO: and descending (left border of interval) orders
            map_isort_i = sorted(range(len(self._data)), key=lambda x: self._data[x][1])
            self._map_i_isort = sorted(range(len(self._data)), key=lambda x: map_isort_i[x])

    def intention_i(self, object_indexes):
        """Select a common interval description for all objects from ``object_indexes``"""
        if len(object_indexes) == 0:
            return None

        if not LIB_INSTALLED['numpy']:
            min_, max_ = self._data[object_indexes[0]]
            for g_i in object_indexes[1:]:
                v_min, v_max = self._data[g_i]
                min_ = v_min if v_min < min_ else min_
                max_ = v_max if v_max > max_ else max_
        else:
            min_g_i, max_g_i = object_indexes[0], object_indexes[0]
            min_sort_i, max_sort_i = self._map_i_isort[min_g_i], self._map_i_isort[max_g_i]
            for g_i in object_indexes[1:]:
                sort_i = self._map_i_isort[g_i]
                if sort_i < min_sort_i:
                    min_g_i = g_i
                    min_sort_i = sort_i
                if sort_i > max_sort_i:
                    max_g_i = g_i
                    max_sort_i = sort_i

            min_, max_ = self._data[min_g_i][0], self._data[max_g_i][1]

        return min_, max_

    def extension_i(self, description, base_objects_i=None):
        """Select a set of indexes of objects from ``base_objects_i`` which fall into interval of ``description``"""
        if description is None:
            return []

        if isinstance(description, Iterable):
            min_, max_ = description[0], description[1]
        else:
            min_ = max_ = description

        if not LIB_INSTALLED['numpy']:
            base_objects_i = range(len(self._data)) if base_objects_i is None else base_objects_i
            g_is = [g_i for g_i in base_objects_i if min_ <= self._data[g_i][0] and self._data[g_i][1] <= max_]
        else:
            if base_objects_i is None:
                base_objects_i = np.arange(len(self._data))
            if not isinstance(base_objects_i, np.ndarray):
                if isinstance(base_objects_i, (list, tuple)):
                    base_objects_i = np.array(base_objects_i)
                else:
                    base_objects_i = np.array(tuple(base_objects_i))

            g_is = base_objects_i[(min_ <= self._data[base_objects_i, 0]) & (self._data[base_objects_i, 1] <= max_)]
        return g_is

    def description_to_generators(self, description, projection_num):
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

    def generators_to_description(self, generators):
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
        same_data = self._data == other.data if not LIB_INSTALLED['numpy'] else (self._data == other.data).all()
        return same_data and self._name == other.name

    def __hash__(self):
        return hash((self._name, tuple([tuple(x) for x in self._data])))

    def to_numeric(self):
        """Turn `IntervalPS` data into a set of numeric columns and their names"""
        return self._data, (f"{self.name}_from", f"{self.name}_to")

    def generators_by_intent_difference(self, new_intent, old_intent):
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
    def intersect_descriptions(a, b):
        """Compute the maximal common description of two descriptions `a` and `b`"""
        intersection = (max(a[0], b[0]), min(a[1], b[1]))
        if intersection[0]>intersection[1]:
            return None
        return intersection

    @staticmethod
    def unite_descriptions(a, b):
        """Compute the minimal description includes the descriptions `a` and `b`"""
        unity = (min(a[0], b[0]), max(a[1], b[1]))
        return unity

    @classmethod
    def to_json(cls, x):
        """Convert description ``x`` into .json format"""
        if LIB_INSTALLED['numpy'] and x is not None:
            x = (float(x[0]) , float(x[1]))
        x_json = json.dumps(x)
        return x_json

    @classmethod
    def from_json(cls, x_json):
        """Load description from ``x_json`` .json format"""
        x = json.loads(x_json)
        if LIB_INSTALLED['numpy'] and x is not None:
            x = (np.float32(x[0]), np.float32(x[1]))
        return x
