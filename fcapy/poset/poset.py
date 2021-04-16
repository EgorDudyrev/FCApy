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
            self._cache_leq = {}
            self._cache_subelements = {}

            self.leq_elements = self._leq_elements_cache
            self.sub_elements = self._sub_elements_cache
        else:
            self.leq_elements = self._leq_elements_nocache
            self.sub_elements = self._sub_elements_nocache

    @property
    def elements(self):
        return self._elements

    @property
    def leq_func(self):
        return self._leq_func

    def super_elements(self, element_index: int):
        el = self._elements[element_index]
        sup_indexes = {i for i, el_comp in enumerate(self._elements)
                       if self.leq_elements(element_index, i) and i != element_index}
        return sup_indexes

    def sub_elements(self, element_index: int):
        """Placeholder to use instead of either self._sub_elements_nocache(...) or self._sub_elements_cache(...)"""
        raise NotImplementedError

    def _sub_elements_nocache(self, element_index: int):
        el = self._elements[element_index]
        sub_indexes = {i for i, el_comp in enumerate(self._elements)
                       if self.leq_elements(i, element_index) and i != element_index}
        return sub_indexes

    def _sub_elements_cache(self, element_index: int):
        res = self._cache_subelements.get(element_index)
        if res is None:
            res = self._sub_elements_nocache(element_index)
            self._cache_subelements[element_index] = res
        return res

    def join_elements(self, element_indexes: Collection = None):
        if element_indexes is None or len(element_indexes)==0:
            element_indexes = list(range(len(self._elements)))

        join_indexes = self.super_elements(element_indexes[0]) | {element_indexes[0]}
        for el_idx in element_indexes[1:]:
            join_indexes &= self.super_elements(el_idx)|{el_idx}

        for el_idx in copy(join_indexes):
            join_indexes -= self.super_elements(el_idx)

        return join_indexes.pop() if len(join_indexes) == 1 else None

    def meet_elements(self, element_indexes: Collection = None):
        if element_indexes is None or len(element_indexes) == 0:
            element_indexes = list(range(len(self._elements)))

        meet_indexes = self.sub_elements(element_indexes[0]) | {element_indexes[0]}
        for el_idx in element_indexes[1:]:
            meet_indexes &= self.sub_elements(el_idx)|{el_idx}

        for el_idx in copy(meet_indexes):
            meet_indexes -= self.sub_elements(el_idx)

        return meet_indexes.pop() if len(meet_indexes) == 1 else None

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
        key = (a_index, b_index)
        if key in self._cache_leq:
            res = self._cache_leq[key]
        else:
            res = self._leq_elements_nocache(a_index, b_index)
            self._cache_leq[key] = res
        return res

    def __getitem__(self, item: int or slice or Collection):
        return slice_list(self._elements, item) if not isinstance(item, int) else self._elements[item]

    def __and__(self, other):
        assert self._leq_func == other.leq_func, \
            'POSet.__and__ assertion. Compared posets have to have the same leq_func'
        elements_and = [x for x in self._elements if x in other._elements]

        s = POSet(elements_and, self._leq_func, use_cache=self._use_cache)
        if self._use_cache:
            s._cache_leq = self._combine_caches(self._cache_leq, self._elements, other._cache_leq, other._elements,
                                                elements_and, dict)
            s._cache_subelements = self._combine_caches(self._cache_subelements, self._elements,
                                                        other._cache_subelements, other._elements,
                                                        elements_and, set)

        return s

    def __or__(self, other):
        assert self._leq_func == other.leq_func, \
            'POSet.__or__ assertion. Compared posets have to have the same leq_func'
        elements_or = [x for x in self._elements]
        elements_or += [x for x in other._elements if x not in elements_or]

        s = POSet(elements_or, self._leq_func, use_cache=self._use_cache)
        if self._use_cache:
            s._cache_leq = self._combine_caches(self._cache_leq, self._elements, other._cache_leq, other._elements,
                                                elements_or, dict)
        return s

    def __xor__(self, other):
        assert self._leq_func == other.leq_func, \
            'POSet.__xor__ assertion. Compared posets have to have the same leq_func'
        elements_xor = [x for x in self._elements if x not in other._elements]
        elements_xor += [x for x in other._elements if x not in self._elements]

        s = POSet(elements_xor, self._leq_func, use_cache=self._use_cache)
        if self._use_cache:
            s._cache_leq = self._combine_caches(self._cache_leq, self._elements, other._cache_leq, other._elements,
                                                elements_xor, dict)
            s._cache_subelements = self._combine_caches(self._cache_subelements, self._elements,
                                                        other._cache_subelements, other._elements,
                                                        elements_xor, set)
        return s

    def __sub__(self, other):
        assert self._leq_func == other.leq_func, \
            'POSet.__sub__ assertion. Compared posets have to have the same leq_func'
        elements_sub = [x for x in self._elements if x not in other._elements]

        s = POSet(elements_sub, self._leq_func, use_cache=self._use_cache)
        if self._use_cache:
            s._cache_leq = self._combine_caches(self._cache_leq, self._elements,
                                                other._cache_leq, other._elements, elements_sub, dict)
            s._cache_subelements = self._combine_caches(self._cache_subelements, self._elements,
                                                        other._cache_subelements, other._elements,
                                                        elements_sub, set)
        return s

    @staticmethod
    def _combine_caches(cache_a, elements_a, cache_b, elements_b, elements_combined, cache_element_type):
        def map_cache_to_comb_element(
                cache_base, elements_base, el_idx_map_base,
                el_comb, elements_comb, el_idx_map_comb,
                cache_element_type
        ):
            if cache_element_type is dict:
                if el_comb in el_idx_map_base:
                    idx_base = el_idx_map_base[el_comb]
                    cache_comb = {}
                    for idx, rel in cache_base[idx_base].items():
                        el_base = elements_base[idx]
                        if el_base in elements_comb:
                            idx_comb = el_idx_map_comb[el_base]
                            cache_comb[idx_comb] = rel
                else:
                    cache_comb = {}

            elif cache_element_type is set:
                if el_comb in el_idx_map_base:
                    idx_base = el_idx_map_base[el_comb]
                    cache_comb = {el_idx_map_comb[elements_base[idx]] for idx in cache_base[idx_base]}
                else:
                    cache_comb = set()

            else:
                raise NotImplementedError

            return cache_comb

        a_el_idx_map = {el: idx for idx, el in enumerate(elements_a)}
        b_el_idx_map = {el: idx for idx, el in enumerate(elements_b)}
        comb_el_idx_map = {el: idx for idx, el in enumerate(elements_combined)}

        cache_combined = {}
        for idx_comb, el_comb in enumerate(elements_combined):
            cached_a = map_cache_to_comb_element(cache_a, elements_a, a_el_idx_map,
                                                 el_comb, elements_combined, comb_el_idx_map,
                                                 cache_element_type)
            cached_b = map_cache_to_comb_element(cache_b, elements_b, b_el_idx_map,
                                                 el_comb, elements_combined, comb_el_idx_map,
                                                 cache_element_type)

            if cache_element_type is dict:
                cached_comb = cached_a
                for idx, rel in cached_b.items():
                    cached_comb[idx] = rel
            elif cache_element_type is set:
                cached_comb = cached_a | cached_b
            else:
                raise NotImplementedError

            cache_combined[idx_comb] = cached_comb

        return cache_combined

    def __len__(self):
        return len(self._elements)

    def __delitem__(self, key):
        del self._elements[key]

        def decr_idx(idx):
            return idx-1 if idx > key else idx

        if self._use_cache:
            self._cache_leq = {(decr_idx(a_idx), decr_idx(b_idx)): rel
                               for (a_idx, b_idx), rel in self._cache_leq.items()
                               if a_idx != key and b_idx != key}

    def add(self, element):
        self._elements.append(element)
        if self._use_cache:
            new_idx = len(self._elements) -1
            #self._cache_leq[new_idx] = {}
            #self._cache_subelements[new_idx] = None

    def remove(self, element):
        idx = [idx for idx, el in enumerate(self._elements) if el == element][0]
        del self[idx]

    def __eq__(self, other):
        return self._leq_func == other._leq_func and self._elements == other._elements

    def fill_up_leq_cache(self):
        assert self._use_cache,\
            "POSet.fill_up_leq_cache assertion. " \
            "The cache can only be filled up if it is enabled (`POSet.use_cache = True`)"

        for i in range(len(self)):
            for j in range(len(self)):
                if (i, j) not in self._cache_leq:
                    self.leq_elements(i, j)

    def fill_up_subelements_cache(self):
        assert self._use_cache, \
            "POSet.fill_up_subelements_cache assertion. " \
            "The cache can only be filled up if it is enabled (`POSet.use_cache = True`)"

        for i in range(len(self)):
            self.sub_elements(i)

    def fill_up_caches(self):
        self.fill_up_leq_cache()
        self.fill_up_subelements_cache()