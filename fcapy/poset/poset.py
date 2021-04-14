"""
This module provides a POSet class. It may be considered as the main module (and class) of poset subpackage

POSet (Partially Ordered Set) is a set in which some elements are bigger then other,
some are smaller and some are incomparable
"""
from fcapy.utils.utils import slice_list
from copy import copy
from collections.abc import Collection


class POSet:
    def __init__(self, elements=None, leq_func=None, use_cache: bool = True):
        self._elements = list(elements) if elements is not None else None
        self._leq_func = leq_func

        self._use_cache = use_cache
        if self._use_cache:
            self._cache = {i: {} for i in range(len(elements))} if elements is not None else None
            self.leq_elements = self._leq_elements_cache
        else:
            self.leq_elements = self._leq_elements_nocache

    @property
    def elements(self):
        return self._elements

    @property
    def leq_func(self):
        return self._leq_func

    def super_elements(self, element_index: int):
        el = self._elements[element_index]
        sup_indexes = [i for i, el_comp in enumerate(self._elements)
                       if self.leq_elements(element_index, i) and i != element_index]
        return sup_indexes

    def sub_elements(self, element_index: int):
        el = self._elements[element_index]
        sub_indexes = [i for i, el_comp in enumerate(self._elements)
                       if self.leq_elements(i, element_index) and i != element_index]
        return sub_indexes

    def join_elements(self, element_indexes: Collection = None):
        if element_indexes is None or len(element_indexes)==0:
            element_indexes = list(range(len(self._elements)))

        join_indexes = self.super_elements(element_indexes[0])+[element_indexes[0]]
        for el_i in element_indexes[1:]:
            join_indexes = [idx for idx in self.super_elements(el_i)+[el_i] if idx in join_indexes]

        for el_idx in copy(join_indexes):
            sups_indexes = self.super_elements(el_idx)
            join_indexes = [idx for idx in join_indexes if idx not in sups_indexes]

        return join_indexes[0] if len(join_indexes) == 1 else None

    def meet_elements(self, element_indexes: Collection = None):
        if element_indexes is None or len(element_indexes) == 0:
            element_indexes = list(range(len(self._elements)))

        meet_indexes = self.sub_elements(element_indexes[0])+[element_indexes[0]]
        for el_i in element_indexes[1:]:
            meet_indexes = [idx for idx in self.sub_elements(el_i)+[el_i] if idx in meet_indexes]

        for el_idx in copy(meet_indexes):
            subs_indexes = self.sub_elements(el_idx)
            meet_indexes = [idx for idx in meet_indexes if idx not in subs_indexes]

        return meet_indexes[0] if len(meet_indexes) == 1 else None

    def supremum(self, element_indexes: Collection = None):
        """Alias for `self.join_elements(element_indexes)`"""
        return self.join_elements(element_indexes)

    def infimum(self, element_indexes: Collection = None):
        """Alias for `self.meet_elements(element_indexes)`"""
        return self.meet_elements(element_indexes)

    def leq_elements(self, a_index: int, b_index: int):
        """Placeholder to use instead of either self._leq_elements_nocache(...) or self._leq_elements_cache(...)"""
        raise NotImplementedError

    def _leq_elements_nocache(self, a_index: int, b_index: int):
        return self._leq_func(self._elements[a_index], self._elements[b_index])

    def _leq_elements_cache(self, a_index: int, b_index: int):
        res = self._cache[a_index].get(b_index)
        if res is None:
            res = self._leq_func(self._elements[a_index], self._elements[b_index])
            self._cache[a_index][b_index] = res
        return res

    def __getitem__(self, item: int or slice or Collection):
        return slice_list(self._elements, item) if not isinstance(item, int) else self._elements[item]

    def __and__(self, other):
        """Placeholder to use instead of either self._and_nocache(...) or self._and_cache(...)"""
        if self._use_cache:
            return self._and_cache(other)
        else:
            return self._and_nocache(other)

    def _and_nocache(self, other):
        assert self._leq_func == other.leq_func, \
            'POSet.__and__ assertion. Compared posets have to have the same leq_func'
        elements_and = [x for x in self._elements if x in other._elements]
        s = POSet(elements_and, self._leq_func)
        return s

    def _and_cache(self, other):
        #TODO: Rewrite to use cache

        assert self._leq_func == other.leq_func, \
            'POSet.__and__ assertion. Compared posets have to have the same leq_func'
        elements_and = [x for x in self._elements if x in other._elements]
        s = POSet(elements_and, self._leq_func)
        return s

    def __or__(self, other):
        """Placeholder to use instead of either self._or_nocache(...) or self._or_cache(...)"""
        if self._use_cache:
            return self._or_cache(other)
        else:
            return self._or_nocache(other)

    def _or_nocache(self, other):
        assert self._leq_func == other.leq_func, \
            'POSet.__or__ assertion. Compared posets have to have the same leq_func'
        elements_or = [x for x in self._elements]
        elements_or += [x for x in other._elements if x not in elements_or]
        s = POSet(elements_or, self._leq_func)
        return s

    def _or_cache(self, other):
        #TODO: Rewrite to use cache

        assert self._leq_func == other.leq_func, \
            'POSet.__or__ assertion. Compared posets have to have the same leq_func'
        elements_or = [x for x in self._elements]
        elements_or += [x for x in other._elements if x not in elements_or]
        s = POSet(elements_or, self._leq_func)
        return s

    def __xor__(self, other):
        """Placeholder to use instead of either self._xor_nocache(...) or self._xor_cache(...)"""
        if self._use_cache:
            return self._xor_cache(other)
        else:
            return self._xor_nocache(other)

    def _xor_nocache(self, other):
        assert self._leq_func == other.leq_func, \
            'POSet.__xor__ assertion. Compared posets have to have the same leq_func'
        elements_or = [x for x in self._elements if x not in other._elements]
        elements_or += [x for x in other._elements if x not in self._elements]
        s = POSet(elements_or, self._leq_func)
        return s

    def _xor_cache(self, other):
        #TODO: Rewrite to use cache

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

    def add(self, element):
        self._elements.append(element)

    def remove(self, element):
        self._elements.remove(element)

    def __eq__(self, other):
        return self._leq_func == other._leq_func and self._elements == other._elements

    def fill_up_cache(self):
        assert self._use_cache,\
            "POSet.fill_up_cache assertion. The cache can only be filled up if it is enabled (`POSet.use_cache = True`)"

        for i in range(len(self)):
            for j in range(len(self)):
                if j not in self._cache[i]:
                    self.leq_elements(i, j)
