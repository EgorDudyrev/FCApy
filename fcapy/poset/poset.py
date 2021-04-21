"""
This module provides a POSet class. It may be considered as the main module (and class) of poset subpackage

POSet (Partially Ordered Set) is a set in which some elements are bigger then other,
some are smaller and some are incomparable
"""
from fcapy.utils.utils import slice_list
from copy import copy
from collections.abc import Collection
import dis


class POSet:
    def __init__(self, elements=None, leq_func=None, use_cache: bool = True):
        if elements is not None:
            self._elements = list(elements)
            self._elements_to_index_map = {el: idx for idx, el in enumerate(self._elements)}
        else:
            self._elements = None
            self._elements_to_index_map = {}

        self._leq_func = leq_func

        self._use_cache = use_cache
        if self._use_cache:
            self._cache_leq = {}
            self._cache_subelements = {}
            self._cache_superelements = {}
            self._cache_direct_subelements = {}
            self._cache_direct_superelements = {}

            self.leq_elements = self._leq_elements_cache
            self.sub_elements = self._sub_elements_cache
            self.super_elements = self._super_elements_cache
            self.direct_sub_elements = self._direct_sub_elements_cache
            self.direct_super_elements = self._direct_super_elements_cache
        else:
            self.leq_elements = self._leq_elements_nocache
            self.sub_elements = self._sub_elements_nocache
            self.super_elements = self._super_elements_nocache
            self.direct_sub_elements = self._direct_sub_elements_nocache
            self.direct_super_elements = self._direct_super_elements_nocache

    @property
    def elements(self):
        return self._elements

    @property
    def leq_func(self):
        return self._leq_func

    def index(self, element):
        return self._elements_to_index_map[element]

    @property
    def direct_super_elements_dict(self):
        return {el_i: self.direct_super_elements(el_i) for el_i in range(len(self))}

    @property
    def super_elements_dict(self):
        return {el_i: self.super_elements(el_i) for el_i in range(len(self))}

    @property
    def direct_sub_elements_dict(self):
        return {el_i: self.direct_sub_elements(el_i) for el_i in range(len(self))}

    @property
    def sub_elements_dict(self):
        return {el_i: self.sub_elements(el_i) for el_i in range(len(self))}
    
    @property
    def top_elements(self):
        return [el_i for el_i in range(len(self)) if len(self.super_elements(el_i)) == 0]
    
    @property
    def bottom_elements(self):
        return [el_i for el_i in range(len(self)) if len(self.sub_elements(el_i)) == 0]

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
            self._cache_superelements[element_index] = frozenset(res)
        return set(res)

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
            self._cache_subelements[element_index] = frozenset(res)
        return set(res)

    def direct_super_elements(self, element_index: int):
        """Placeholder to use instead of self._direct_super_elements_nocache(.) or self._direct_super_elements_cache(.)"""

    def _direct_super_elements_nocache(self, element_index: int):
        superelement_idxs = self.super_elements(element_index)
        for el_idx in list(superelement_idxs):
            if el_idx in superelement_idxs:
                superelement_idxs -= self.super_elements(el_idx)

        return superelement_idxs

    def _direct_super_elements_cache(self, element_index: int):
        res = self._cache_direct_superelements.get(element_index)
        if res is None:
            res = self._direct_super_elements_nocache(element_index)
            self._cache_direct_superelements[element_index] = frozenset(res)
        return set(res)

    def direct_sub_elements(self, element_index: int):
        """Placeholder to use instead of self._direct_sub_elements_nocache(.) or self._direct_sub_elements_cache(.)"""

    def _direct_sub_elements_nocache(self, element_index: int):
        subelement_idxs = self.sub_elements(element_index)
        for el_idx in list(subelement_idxs):
            if el_idx in subelement_idxs:
                subelement_idxs -= self.sub_elements(el_idx)

        return subelement_idxs

    def _direct_sub_elements_cache(self, element_index: int):
        res = self._cache_direct_subelements.get(element_index)
        if res is None:
            res = self._direct_sub_elements_nocache(element_index)
            self._cache_direct_subelements[element_index] = frozenset(res)
        return set(res)

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
            self._combine_multiple_caches(other, s, drop_notcommon_elements=False)

        return s

    def __or__(self, other):
        assert self._leq_func == other.leq_func, \
            'POSet.__or__ assertion. Compared posets have to have the same leq_func'
        elements_or = [x for x in self._elements]
        elements_or += [x for x in other._elements if x not in elements_or]

        s = POSet(elements_or, self._leq_func, use_cache=self._use_cache)
        if self._use_cache:
            self._combine_multiple_caches(other, s, drop_notcommon_elements=True)

        return s

    def __xor__(self, other):
        assert self._leq_func == other.leq_func, \
            'POSet.__xor__ assertion. Compared posets have to have the same leq_func'
        elements_xor = [x for x in self._elements if x not in other._elements]
        elements_xor += [x for x in other._elements if x not in self._elements]

        s = POSet(elements_xor, self._leq_func, use_cache=self._use_cache)
        if self._use_cache:
            self._combine_multiple_caches(other, s, drop_notcommon_elements=True)

        return s

    def __sub__(self, other):
        assert self._leq_func == other.leq_func, \
            'POSet.__sub__ assertion. Compared posets have to have the same leq_func'
        elements_sub = [x for x in self._elements if x not in other._elements]

        s = POSet(elements_sub, self._leq_func, use_cache=self._use_cache)
        if self._use_cache:
            self._combine_multiple_caches(other, s, drop_notcommon_elements=False)

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
            elif value_type in {set, frozenset}:
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

                if (value_type in {set, frozenset}) and (comb_key in cache_combined):
                    comb_value |= cache_combined[comb_key]

                cache_combined[comb_key] = comb_value

        return cache_combined

    def _combine_multiple_caches(self, other, poset_combined, drop_notcommon_elements: bool):
        elements_and = {x for x in self._elements if x in other._elements}
        cache_names = ['_cache_leq', '_cache_subelements', '_cache_superelements',
                       '_cache_direct_subelements', '_cache_direct_superelements']

        for cache_name in cache_names:
            cache_comb = self._combine_caches(
                self.__dict__[cache_name], self._elements,
                other.__dict__[cache_name], other._elements,
                poset_combined._elements)

            if drop_notcommon_elements and ('superelements' in cache_name or 'subelements' in cache_name):
                for idx in list(cache_comb):
                    if poset_combined._elements[idx] not in elements_and:
                        del cache_comb[idx]

            poset_combined.__dict__[cache_name] = cache_comb

    def __len__(self):
        return len(self._elements)

    def __delitem__(self, key):
        del self._elements_to_index_map[self._elements[key]]
        del self._elements[key]

        def decr_idx(idx, threshold):
            return idx - 1 if idx > threshold else idx

        self._elements_to_index_map = {el: decr_idx(idx, key) for el, idx in self._elements_to_index_map.items()}

        if self._use_cache:

            def decrement_dict(dct, threshold):
                if len(dct) == 0:
                    return {}

                dct_decr = {}

                k, v = dct.popitem()
                k_tuple_flag, k_int_flag = isinstance(k, tuple), isinstance(k, int)
                v_set_flag, v_bool_flag = isinstance(v, (set, frozenset)), isinstance(v, bool)
                dct[k] = v

                for k, v in dct.items():
                    if (k_tuple_flag and threshold in k)\
                            or (k_int_flag and threshold == k):
                        continue

                    if k_tuple_flag:
                        k_decr = tuple([decr_idx(idx, threshold) for idx in k])
                    elif k_int_flag:
                        k_decr = decr_idx(k, threshold)
                    else:
                        raise ValueError

                    if v_set_flag:
                        v_decr = {decr_idx(idx, threshold) for idx in v if idx != threshold}
                    elif v_bool_flag:
                        v_decr = v
                    else:
                        raise ValueError

                    dct_decr[k_decr] = v_decr
                return dct_decr

            self._cache_leq = decrement_dict(self._cache_leq, key)

            for el_i_sup in self._cache_superelements.get(key, []):
                if el_i_sup in self._cache_subelements:
                    self._cache_subelements[el_i_sup] |= self._cache_subelements.get(key, set())
            for el_i_sub in self._cache_subelements.get(key, []):
                if el_i_sub in self._cache_superelements:
                    self._cache_superelements[el_i_sub] |= self._cache_superelements.get(key, set())

#            for el_i_dsup in self._cache_direct_superelements.get(key, []):
#                if el_i_dsup in self._cache_direct_subelements:
#                    self._cache_direct_subelements[el_i_dsup] |= self._cache_direct_subelements.get(key,set())
#            for el_i_dsub in self._cache_direct_subelements.get(key, []):
#                if el_i_dsub in self._cache_direct_superelements:
#                    self._cache_direct_superelements[el_i_dsub] |= self._cache_direct_superelements.get(key, set())

            self._cache_subelements = decrement_dict(self._cache_subelements, key)
            self._cache_superelements = decrement_dict(self._cache_superelements, key)
#            self._cache_direct_subelements = decrement_dict(self._cache_direct_subelements, key)
#            self._cache_direct_superelements = decrement_dict(self._cache_direct_superelements, key)
            self._cache_direct_subelements = self._direct_relation_cache_by_closed_cache(self._cache_subelements)
            self._cache_direct_superelements = self._direct_relation_cache_by_closed_cache(self._cache_superelements)

    def add(self, element):
        if element in self._elements_to_index_map:
            return

        self._elements_to_index_map[element] = len(self._elements)
        self._elements.append(element)
        if self._use_cache:
            self._cache_subelements = {}
            self._cache_superelements = {}
            self._cache_direct_subelements = {}
            self._cache_direct_superelements = {}

    def remove(self, element):
        idx = [idx for idx, el in enumerate(self._elements) if el == element][0]
        del self[idx]

    def __eq__(self, other):
        same_elements = set(self._elements) == set(other._elements)
        if not same_elements:
            return False
        self_i_other_i_map = {self_i: other.index(el) for self_i, el in enumerate(self._elements)}
        other_i_self_i_map = {other_i: self_i for self_i, other_i in self_i_other_i_map.items()}
        for self_i, el in enumerate(self._elements):
            self_subs = self.sub_elements(self_i)
            other_subs = other.sub_elements(self_i_other_i_map[self_i])
            other_subs = {other_i_self_i_map[other_i] for other_i in other_subs}
            if self_subs != other_subs:
                return False
        return True

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

    def fill_up_direct_subelements_cache(self):
        assert self._use_cache, \
            "POSet.fill_up_direct_subelements_cache assertion. " \
            "The cache can only be filled up if it is enabled (`POSet.use_cache = True`)"

        for i in range(len(self)):
            self.direct_sub_elements(i)

    def fill_up_direct_superelements_cache(self):
        assert self._use_cache, \
            "POSet.fill_up_direct_superelements_cache assertion. " \
            "The cache can only be filled up if it is enabled (`POSet.use_cache = True`)"

        for i in range(len(self)):
            self.direct_super_elements(i)

    def fill_up_caches(self):
        self.fill_up_leq_cache()
        self.fill_up_subelements_cache()
        self.fill_up_superelements_cache()
        self.fill_up_direct_subelements_cache()
        self.fill_up_direct_superelements_cache()

    @classmethod
    def _closed_relation_cache_by_direct_cache(cls, direct_relation_cache):
        direct_cache_trans = cls._transpose_hierarchy(direct_relation_cache)
        elements_to_visit = [el_i for el_i, subelems in direct_relation_cache.items() if len(subelems) == 0]
        elements_visited = set()
        closed_cache = {}
        while len(elements_to_visit) > 0:
            for i, el_i in enumerate(elements_to_visit):
                if direct_relation_cache[el_i] & elements_visited == direct_relation_cache[el_i]:
                    idx = i
                    break
            el_i = elements_to_visit.pop(idx)

            direct_rels = direct_relation_cache[el_i]

            closed_cache[el_i] = direct_rels.copy()
            for el_i_rel in direct_rels:
                closed_cache[el_i] |= closed_cache[el_i_rel]

            elements_to_visit += list(direct_cache_trans[el_i])
            elements_visited.add(el_i)
        closed_cache = {k: frozenset(vs) for k, vs in closed_cache.items()}
        return closed_cache

    @classmethod
    def _direct_relation_cache_by_closed_cache(cls, closed_relation_cache):
        direct_relation_cache = {}
        for el_i, elems_rel_all in closed_relation_cache.items():
            direct_relation_cache[el_i] = elems_rel_all.copy()
            for el_i_rel in elems_rel_all:
                direct_relation_cache[el_i] -= closed_relation_cache[el_i_rel]

        direct_relation_cache = {k: frozenset(vs) for k, vs in direct_relation_cache.items()}
        return direct_relation_cache

    @staticmethod
    def _transpose_hierarchy(hierarchy_dict):
        """Return transposed hierarchy of elements (i.e. turn superelements into subelements and vice versa)

        Parameters
        ----------
        hierarchy_dict: `dict` of type {`int`: `list` of `int`}
            Superelements or subelements of POSet

        Returns
        -------
        new_dict: `dict` of type {`int`: `list` of `int`}
            Superelements if subelements are given, subelements if superelements are given
        """
        new_dict = {}
        for k, vs in hierarchy_dict.items():
            if k not in new_dict:
                new_dict[k] = set()
            for v in vs:
                new_dict[v] = new_dict.get(v, set()) | {k}
        return new_dict
