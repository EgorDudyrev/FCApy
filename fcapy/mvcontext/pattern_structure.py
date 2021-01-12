from collections.abc import Iterable
import math


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


class IntervalPS(AbstractPS):
    def intention_i(self, object_indexes):
        if len(object_indexes) == 0:
            return None

        min_ = max_ = self._data[object_indexes[0]]
        for g_i in object_indexes[1:]:
            v = self._data[g_i]
            min_ = v if v < min_ else min_
            max_ = v if v > max_ else max_

        if min_ == max_:
            return min_
        return min_, max_

    def extension_i(self, description, base_objects_i=None):
        if description is None:
            return []

        if isinstance(description, (tuple, )):
            min_, max_ = description[0], description[1]
        else:
            min_ = max_ = description

        base_objects_i = range(len(self._data)) if base_objects_i is None else base_objects_i
        g_is = [g_i for g_i in base_objects_i if min_ <= self._data[g_i] <= max_]
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

