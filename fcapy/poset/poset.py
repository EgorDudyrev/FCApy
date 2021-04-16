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
            self._cache_superelements = {}

            self.leq_elements = self._leq_elements_cache
            self.sub_elements = self._sub_elements_cache
            self.super_elements = self._super_elements_cache
        else:
            self.leq_elements = self._leq_elements_nocache
            self.sub_elements = self._sub_elements_nocache
            self.super_elements = self._super_elements_cache

    @property
    def elements(self):
        return self._elements

    @property
    def leq_func(self):
        return self._leq_func

    def super_elements(self, element_index: int):
        """Placeholder to use instead of either self._super_elements_nocache(...) or self._super_elements_cache(...)"""
        raise NotImplementedError

    def _super_elements_nocache(self, element_index: int):
        sup_indexes = {i for i, el_comp in enumerate(self._elements)
                       if self.leq_elements(element_index, i) and i != element_index}
        return sup_indexes

    def _super_elements_cache(self, element_index: int):
        res = self._cache_superelements.get(element_index)
        if res is None:
            res = self._super_elements_nocache(element_index)
            self._cache_superelements[element_index] = res
        return res

    def sub_elements(self, element_index: int):
        """Placeholder to use instead of either self._sub_elements_nocache(...) or self._sub_elements_cache(...)"""
        raise NotImplementedError

    def _sub_elements_nocache(self, element_index: int):
        sub_indexes = {i for i, el_comp in enumerate(self._elements)
                       if self.leq_elements(i, element_index) and i != element_index}
        return sub_indexes

    def _sub_elements_cache(self, element_index: int):
        res = self._cache_subelements.get(element_index)
        if res is None:
            res = self._sub_elements_nocache(element_index)
            self._cache_subelements[element_index] = res
        return res

    def direct_super_elements(self, element_index: int):
        superelement_idxs = self.super_elements(element_index)
        for el_idx in list(superelement_idxs):
            if el_idx in superelement_idxs:
                superelement_idxs -= self.super_elements(el_idx)

        return superelement_idxs

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
                                                elements_and)
            s._cache_subelements = self._combine_caches(self._cache_subelements, self._elements,
                                                        other._cache_subelements, other._elements,
                                                        elements_and)
            s._cache_superelements = self._combine_caches(self._cache_superelements, self._elements,
                                                        other._cache_superelements, other._elements,
                                                        elements_and)

        return s

    def __or__(self, other):
        assert self._leq_func == other.leq_func, \
            'POSet.__or__ assertion. Compared posets have to have the same leq_func'
        elements_or = [x for x in self._elements]
        elements_or += [x for x in other._elements if x not in elements_or]

        s = POSet(elements_or, self._leq_func, use_cache=self._use_cache)
        if self._use_cache:
            s._cache_leq = self._combine_caches(self._cache_leq, self._elements, other._cache_leq, other._elements,
                                                elements_or)

            elements_and = [x for x in self._elements if x in other._elements]
            cache_subelements = self._combine_caches(self._cache_subelements, self._elements,
                                                        other._cache_subelements, other._elements,
                                                        elements_or)
            cache_subelements = {idx: subs for idx, subs in cache_subelements.items()
                                 if elements_or[idx] in elements_and}
            s._cache_subelements = cache_subelements

            cache_superelements = self._combine_caches(self._cache_superelements, self._elements,
                                                        other._cache_superelements, other._elements,
                                                        elements_or)
            cache_superelements = {idx: subs for idx, subs in cache_superelements.items()
                                 if elements_or[idx] in elements_and}
            s._cache_superelements = cache_superelements

        return s

    def __xor__(self, other):
        assert self._leq_func == other.leq_func, \
            'POSet.__xor__ assertion. Compared posets have to have the same leq_func'
        elements_xor = [x for x in self._elements if x not in other._elements]
        elements_xor += [x for x in other._elements if x not in self._elements]

        s = POSet(elements_xor, self._leq_func, use_cache=self._use_cache)
        if self._use_cache:
            s._cache_leq = self._combine_caches(self._cache_leq, self._elements, other._cache_leq, other._elements,
                                                elements_xor)

            elements_and = [x for x in self._elements if x in other._elements]
            cache_subelements = self._combine_caches(self._cache_subelements, self._elements,
                                                     other._cache_subelements, other._elements,
                                                     elements_xor)
            cache_subelements = {idx: subs for idx, subs in cache_subelements.items()
                                 if elements_xor[idx] in elements_and}
            s._cache_subelements = cache_subelements

            cache_superelements = self._combine_caches(self._cache_superelements, self._elements,
                                                     other._cache_superelements, other._elements,
                                                     elements_xor)
            cache_superelements = {idx: subs for idx, subs in cache_superelements.items()
                                 if elements_xor[idx] in elements_and}
            s._cache_superelements = cache_superelements

        return s

    def __sub__(self, other):
        assert self._leq_func == other.leq_func, \
            'POSet.__sub__ assertion. Compared posets have to have the same leq_func'
        elements_sub = [x for x in self._elements if x not in other._elements]

        s = POSet(elements_sub, self._leq_func, use_cache=self._use_cache)
        if self._use_cache:
            s._cache_leq = self._combine_caches(self._cache_leq, self._elements,
                                                other._cache_leq, other._elements, elements_sub)
            s._cache_subelements = self._combine_caches(self._cache_subelements, self._elements,
                                                        other._cache_subelements, other._elements,
                                                        elements_sub)
            s._cache_superelements = self._combine_caches(self._cache_superelements, self._elements,
                                                        other._cache_superelements, other._elements,
                                                        elements_sub)
        return s

    @staticmethod
    def _combine_caches(cache_a, elements_a, cache_b, elements_b, elements_combined):
        comb_el_idx_map = {el: idx for idx, el in enumerate(elements_combined)}
        a_idx_comb_idx_map = {idx: comb_el_idx_map[el] for idx, el in enumerate(elements_a) if el in comb_el_idx_map}
        b_idx_comb_idx_map = {idx: comb_el_idx_map[el] for idx, el in enumerate(elements_b) if el in comb_el_idx_map}

        if len(cache_a) > 0:
            key = list(cache_a)[0]
            value = cache_a[key]
        elif len(cache_b) > 0:
            key = list(cache_b)[0]
            value = cache_b[key]
        else:
            # If both caches are empty then the combined cache is empty too
            return {}
        key_type = type(key)
        value_type = type(value)

        def map_key_to_comb(base_key, base_idx_comb_idx_map, key_type):
            if key_type is tuple:
                comb_key = []
                for base_idx in base_key:
                    if base_idx in base_idx_comb_idx_map:
                        comb_key.append(base_idx_comb_idx_map[base_idx])
                    else:
                        comb_key = None
                        break
                else:
                    comb_key = tuple(comb_key)

            elif key_type is int:
                comb_key = base_idx_comb_idx_map.get(base_key)

            else:
                raise TypeError

            return comb_key

        def map_value_to_comb(base_value, base_idx_comb_idx_map, value_type):
            if value_type is bool:
                comb_value = base_value
            elif value_type is set:
                comb_value = {base_idx_comb_idx_map[idx] for idx in base_value if idx in base_idx_comb_idx_map}
            else:
                raise TypeError

            return comb_value

        cache_combined = {}
        for base_cache, base_idx_comb_idx_map in [(cache_a, a_idx_comb_idx_map),
                                                  (cache_b, b_idx_comb_idx_map)]:
            for key, value in base_cache.items():
                comb_key = map_key_to_comb(key, base_idx_comb_idx_map, key_type)
                comb_value = map_value_to_comb(value, base_idx_comb_idx_map, value_type)

                if (comb_key is None) or (comb_value is None):
                    continue

                if (value_type is set) and (comb_key in cache_combined):
                    comb_value |= cache_combined[comb_key]

                cache_combined[comb_key] = comb_value

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
            self._cache_subelements = {decr_idx(idx): {decr_idx(sub_idx) for sub_idx in subs if sub_idx != key}
                               for idx, subs in self._cache_subelements.items()
                               if idx != key}
            self._cache_superelements = {decr_idx(idx): {decr_idx(sup_idx) for sup_idx in sups if sup_idx != key}
                                       for idx, sups in self._cache_superelements.items()
                                       if idx != key}

    def add(self, element):
        self._elements.append(element)
        if self._use_cache:
            self._cache_subelements = {}
            self._cache_superelements = {}

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

    def fill_up_superelements_cache(self):
        assert self._use_cache, \
            "POSet.fill_up_superelements_cache assertion. " \
            "The cache can only be filled up if it is enabled (`POSet.use_cache = True`)"

        for i in range(len(self)):
            self.super_elements(i)

    def fill_up_caches(self):
        self.fill_up_leq_cache()
        self.fill_up_subelements_cache()
        self.fill_up_superelements_cache()
