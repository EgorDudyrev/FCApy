from collections.abc import Iterable
import math
from numbers import Number

from .. import LIB_INSTALLED
if LIB_INSTALLED['numpy']:
    import numpy as np


class AbstractPS:
    def __init__(self, data, name=None):
        self._data = data
        self._name = name

    def intention_i(self, object_indexes):
        raise NotImplementedError

    def extension_i(self, description, base_objects_i=None):
        raise NotImplementedError

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        assert len(value) == len(self._data), "Length of new data does not match the length of old one"
        self._data = value

    @property
    def name(self):
        return self._name

    def description_to_generators(self, description, projection_num):
        raise NotImplementedError

    def generators_to_description(self, generators):
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
        raise NotImplementedError

    def generators_by_intent_difference(self, new_intent, old_intent):
        raise NotImplementedError


class IntervalPS(AbstractPS):
    def __init__(self, data, name=None):
        super(IntervalPS, self).__init__(data, name)
        self.data = data

    @property
    def data(self):
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
            self._data = np.array(self._data)
            # TODO: Rewrite sorting to ascending (right border of interval)
            # TODO: and descending (left border of interval) orders
            map_isort_i = sorted(range(len(self._data)), key=lambda x: self._data[x][1])
            self._map_i_isort = sorted(range(len(self._data)), key=lambda x: map_isort_i[x])

    def intention_i(self, object_indexes):
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
        return self._data, (f"{self.name}_from", f"{self.name}_to")

    def generators_by_intent_difference(self, new_intent, old_intent):
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
