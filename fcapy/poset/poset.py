"""
This module provides a POSet class. It may be considered as the main module (and class) of poset subpackage

POSet (Partially Ordered Set) is a set in which some elements are bigger then other,
some are smaller and some are incomparable
"""
from numbers import Integral
from fcapy.utils.utils import slice_list
from copy import copy


class POSet:
    def __init__(self, elements=None, leq_func=None):
        self._elements = list(elements) if elements is not None else None
        self._leq_func = leq_func

    @property
    def elements(self):
        return self._elements

    @property
    def leq_func(self):
        return self._leq_func

    def super_elements(self, element_index:int):
        el = self._elements[element_index]
        sup_indexes = [i for i, el_comp in enumerate(self._elements)
                       if self._leq_func(el, el_comp) and i != element_index]
        return sup_indexes

    def sub_elements(self, element_index:int):
        el = self._elements[element_index]
        sub_indexes = [i for i, el_comp in enumerate(self._elements)
                       if self._leq_func(el_comp, el) and i != element_index]
        return sub_indexes

    def join_elements(self, element_indexes=None):
        if element_indexes is None or len(element_indexes)==0:
            element_indexes = list(range(len(self._elements)))

        join_indexes = self.super_elements(element_indexes[0])+[element_indexes[0]]
        for el_i in element_indexes[1:]:
            join_indexes = [idx for idx in self.super_elements(el_i)+[el_i] if idx in join_indexes]

        for el_idx in copy(join_indexes):
            sups_indexes = self.super_elements(el_idx)
            join_indexes = [idx for idx in join_indexes if idx not in sups_indexes]

        return join_indexes[0] if len(join_indexes) == 1 else None

    def meet_elements(self, element_indexes=None):
        if element_indexes is None or len(element_indexes) == 0:
            element_indexes = list(range(len(self._elements)))

        meet_indexes = self.sub_elements(element_indexes[0])+[element_indexes[0]]
        for el_i in element_indexes[1:]:
            meet_indexes = [idx for idx in self.sub_elements(el_i)+[el_i] if idx in meet_indexes]

        for el_idx in copy(meet_indexes):
            subs_indexes = self.sub_elements(el_idx)
            meet_indexes = [idx for idx in meet_indexes if idx not in subs_indexes]

        return meet_indexes[0] if len(meet_indexes) == 1 else None

    def supremum(self, element_indexes=None):
        """Alias for `self.join_elements(element_indexes)`"""
        return self.join_elements(element_indexes)

    def infimum(self, element_indexes=None):
        """Alias for `self.meet_elements(element_indexes)`"""
        return self.meet_elements(element_indexes)

    def leq_elements(self, a_index, b_index):
        return self._leq_func(self._elements[a_index], self._elements[b_index])

    def __getitem__(self, item):
        return slice_list(self._elements, item) if not isinstance(item, Integral) else self._elements[item]

    def __and__(self, other):
        assert self._leq_func == other.leq_func,\
            'POSet.__and__ assertion. Compared posets have to have the same leq_func'
        elements_and = [x for x in self._elements if x in other._elements]
        s = POSet(elements_and, self._leq_func)
        return s

    def __or__(self, other):
        assert self._leq_func == other.leq_func, \
            'POSet.__or__ assertion. Compared posets have to have the same leq_func'
        elements_or = [x for x in self._elements]
        elements_or += [x for x in other._elements if x not in elements_or]
        s = POSet(elements_or, self._leq_func)
        return s

    def __xor__(self, other):
        assert self._leq_func == other.leq_func, \
            'POSet.__xor__ assertion. Compared posets have to have the same leq_func'
        elements_or = [x for x in self._elements if x not in other._elements]
        elements_or += [x for x in other._elements if x not in self._elements]
        s = POSet(elements_or, self._leq_func)
        return s

    def __len__(self):
        return len(self._elements)

    def __delitem__(self, key):
        del self._elements[key]

    def add(self, other):
        self._elements.append(other)

    def remove(self, other):
        self._elements.remove(other)

    def __eq__(self, other):
        return self._leq_func == other._leq_func and self._elements == other._elements
