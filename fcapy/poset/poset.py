"""
This module provides a POSet class. It may be considered as the main module (and class) of poset subpackage

POSet (Partially Ordered Set) is a set in which some elements are bigger then other,
some are smaller and some are incomparable
"""
from typing import List, Dict, Tuple, Callable, Any, FrozenSet, Optional, Collection, Set

from fcapy.utils.utils import slice_list
from fcapy import LIB_INSTALLED
from copy import copy, deepcopy


class POSet:
    """A class to represent a Partially Ordered Set (POSet)

    A POSet (Partially Ordered Set) is a set in which some elements are bigger than the others,
    some are smaller, and some are incomparable.

    Example
    -------
    A set of elements = [set(), {'a'}, {'b'}] with defined leq (less or equal) function = lambda a,b: a in b
    is a POSet.

    set() in {'a'} = True  <=>  set()<={'a'}  <=> element #0 is smaller than element #1
    set() in {'b'} = True  <=>  set()<={'b'}  <=> element #0 is smaller than element #2
    {'a'} in {'b'} = False and {'b'} in {'a'} = False  <=>  ({'a'} not <= {'b'}) and ({'b'} not <= {'a'})
    <=> element #1 and element #2 are incomparable

    """
    def __init__(
            self,
            elements: Collection[Any] = None,
            leq_func: Callable[[Any, Any], bool] = lambda a, b: a <= b,
            use_cache: bool = True, children_dict: Dict[int, Tuple[int, ...]] = None
    ):
        """Construct a POSet based on a set of ``elements`` and ``leq_func`` defined on this set

        Parameters
        ----------
        elements : `list`
            A set of elements of POSet of any kind
        leq_func : `function` (a,b)-> True or False
            A function to compare whether element ``a` from the POSet is smaller than ``b`` or not
        use_cache : `bool`
            A flag whether to save for the output of leq_func and other computations in the cache or not
        children_dict: `dict` of type {``element_i``: indexes of the biggest elements smaller than ``element_i``}
            (optional) A dictionary that contains the precomputed relation
            representing the biggest elements smaller than an element
        """
        if elements is not None:
            self._elements = list(elements)
            self._elements_to_index_map = {el: idx for idx, el in enumerate(self._elements)}
        else:
            self._elements = []
            self._elements_to_index_map = {}

        self._leq_func = leq_func

        self._use_cache = use_cache
        if self._use_cache:
            if children_dict is not None:
                children_dict = deepcopy(children_dict)
                descendants_dict = self._closed_relation_cache_by_direct_cache(children_dict)
                parents_dict = self._transpose_hierarchy(children_dict)
                ancestors_dict = self._transpose_hierarchy(descendants_dict)
                leq_dict = {}
                if len(elements) < 10:
                    for el_i, subels_i in descendants_dict.items():
                        for el_i_1 in range(len(self._elements)):
                            leq_dict[(el_i_1, el_i)] = el_i_1 in subels_i
            else:  # if children_dict is None, initialize caches as empty
                leq_dict, children_dict, descendants_dict, parents_dict, ancestors_dict =\
                    {}, {}, {}, {}, {}

            self._cache_leq = leq_dict
            self._cache_descendants = descendants_dict
            self._cache_ancestors = ancestors_dict
            self._cache_children = {k: frozenset(children) for k, children in children_dict.items()}
            self._cache_parents = parents_dict

            self.leq_elements = self._leq_elements_cache
            self.descendants = self._descendants_cache
            self.ancestors = self._ancestors_cache
            self.children = self._children_cache
            self.parents = self._parents_cache

    @property
    def elements(self) -> List[Any]:
        """A list of elements of the POSet"""
        return self._elements

    @property
    def leq_func(self) -> Callable[[Any, Any], bool]:
        """A function to compare whether element ``a` from the POSet is smaller than ``b`` or not"""
        return self._leq_func

    def index(self, element: Any) -> int:
        """Returns an index of the ``element`` in the list of ``POSet.elements``"""
        return self._elements_to_index_map[element]

    @property
    def parents_dict(self) -> Dict[int, FrozenSet[int]]:
        """A dictionary of kind {`element_idx`: `list`[indexes of the smallest elements bigger than `element_idx`]"""
        return {el_i: self.parents(el_i) for el_i in range(len(self))}

    @property
    def ancestors_dict(self) -> Dict[int, FrozenSet[int]]:
        """A dictionary of kind {`element_idx`: `list`[indexes of all elements bigger than `element_idx`]"""
        return {el_i: self.ancestors(el_i) for el_i in range(len(self))}

    @property
    def children_dict(self) -> Dict[int, FrozenSet[int]]:
        """A dictionary of kind {`element_idx`: `list`[indexes of the biggest elements smaller than `element_idx`]"""
        return {el_i: self.children(el_i) for el_i in range(len(self))}

    @property
    def descendants_dict(self) -> Dict[int, FrozenSet[int]]:
        """A dictionary of kind {`element_idx`: `list`[indexes of all elements smaller than `element_idx`]"""
        return {el_i: self.descendants(el_i) for el_i in range(len(self))}

    def ancestors(self, element_index: int) -> FrozenSet[int]:
        """Return a set of indexes of elements of POSet bigger than element #``element_index``"""
        return self._ancestors_nocache(element_index)

    def _ancestors_nocache(self, element_index: int) -> FrozenSet[int]:
        """Return a set of indexes of elements of POSet bigger than element #``element_index`` (without using cache)"""
        sup_indexes = {i for i in range(len(self)) if self.leq_elements(element_index, i) and i != element_index}
        return frozenset(sup_indexes)

    def _ancestors_cache(self, element_index: int) -> FrozenSet[int]:
        """Return a set of indexes of elements of POSet bigger than element #``element_index`` (using cache)"""
        res = self._cache_ancestors.get(element_index)
        if res is None:
            res = self._ancestors_nocache(element_index)
            self._cache_ancestors[element_index] = frozenset(res)
        return frozenset(res)

    def descendants(self, element_index: int) -> FrozenSet[int]:
        """Return a set of indexes of elements of POSet smaller than element #``element_index``"""
        return self._descendants_nocache(element_index)

    def _descendants_nocache(self, element_index: int) -> FrozenSet[int]:
        """Return a set of indexes of elements of POSet smaller than element #``element_index`` (without using cache)"""
        sub_indexes = {i for i in range(len(self)) if self.leq_elements(i, element_index) and i != element_index}
        return frozenset(sub_indexes)

    def _descendants_cache(self, element_index: int) -> FrozenSet[int]:
        """Return a set of indexes of elements of POSet smaller than element #``element_index`` (using cache)"""
        res = self._cache_descendants.get(element_index)
        if res is None:
            res = self._descendants_nocache(element_index)
            self._cache_descendants[element_index] = frozenset(res)
        return frozenset(res)

    def parents(self, element_index: int) -> FrozenSet[int]:
        """Return a set of indexes of the smallest elements bigger than #``element_index``

        Element ``a`` is a direct super element of element ``b`` if ``a``>``b``
        and there is no element ``c`` such that ``a``>``c``>``b``
        """
        return self._parents_nocache(element_index)

    def _parents_nocache(self, element_index: int) -> FrozenSet[int]:
        """Return a set of indexes of the smallest elements bigger than ``element_index`` (w/out using cache)"""
        superelement_idxs = self.ancestors(element_index)
        for el_idx in list(superelement_idxs):
            if el_idx in superelement_idxs:
                superelement_idxs -= self.ancestors(el_idx)

        return frozenset(superelement_idxs)

    def _parents_cache(self, element_index: int) -> FrozenSet[int]:
        """Return a set of indexes of the smallest elements bigger than ``element_index`` (using cache)"""
        res = self._cache_parents.get(element_index)
        if res is None:
            res = self._parents_nocache(element_index)
            self._cache_parents[element_index] = frozenset(res)
        return frozenset(res)

    def children(self, element_index: int) -> FrozenSet[int]:
        """Return a set of indexes of the biggest elements smaller than #``element_index``

        Element ``a`` is a direct sub element of element ``b`` if ``a``<``b``
        and there is no element ``c`` such that ``a``<``c``<``b``
        """
        return self._children_nocache(element_index)

    def _children_nocache(self, element_index: int) -> FrozenSet[int]:
        """Return a set of indexes of the biggest elements smaller than ``element_index`` (w/out using cache)"""
        subelement_idxs = self.descendants(element_index)
        for el_idx in list(subelement_idxs):
            if el_idx in subelement_idxs:
                subelement_idxs -= self.descendants(el_idx)

        return subelement_idxs

    def _children_cache(self, element_index: int) -> FrozenSet[int]:
        """Return a set of indexes of the biggest elements smaller than ``element_index`` (using cache)"""
        res = self._cache_children.get(element_index)
        if res is None:
            res = self._children_nocache(element_index)
            self._cache_children[element_index] = frozenset(res)
        return frozenset(res)

    @property
    def tops(self) -> List[int]:
        """A list of the top (the biggest) elements in a POSet"""
        return [el_i for el_i in range(len(self)) if len(self.ancestors(el_i)) == 0]

    @property
    def bottoms(self) -> List[int]:
        """A list of the bottom (the smallest) elements in a POSet"""
        return [el_i for el_i in range(len(self)) if len(self.descendants(el_i)) == 0]

    def join(self, element_indexes: Collection[int] = None) -> Optional[int]:
        """Return the smallest element from POSet bigger than all elements from ``element_indexes``"""
        if element_indexes is None or len(element_indexes) == 0:
            element_indexes = list(range(len(self._elements)))

        join_indexes = self.ancestors(element_indexes[0]) | {element_indexes[0]}
        for el_idx in element_indexes[1:]:
            join_indexes &= self.ancestors(el_idx) | {el_idx}

        for el_idx in copy(join_indexes):
            join_indexes -= self.ancestors(el_idx)

        join_idx = list(join_indexes)[0] if len(join_indexes) == 1 else None
        return join_idx

    def meet(self, element_indexes: Collection[int] = None) -> Optional[int]:
        """Return the biggest element from POSet smaller than all elements from ``element_indexes``"""
        if element_indexes is None or len(element_indexes) == 0:
            element_indexes = list(range(len(self)))

        meet_indexes = self.descendants(element_indexes[0]) | {element_indexes[0]}
        for el_idx in element_indexes[1:]:
            meet_indexes &= self.descendants(el_idx) | {el_idx}

        for el_idx in copy(meet_indexes):
            meet_indexes -= self.descendants(el_idx)

        meet_idx = list(meet_indexes)[0] if len(meet_indexes) == 1 else None
        return meet_idx

    def supremum(self, element_indexes: Collection[int] = None) -> Optional[int]:
        """Alias for `self.join(element_indexes)`"""
        return self.join(element_indexes)

    def infimum(self, element_indexes: Collection[int] = None) -> Optional[int]:
        """Alias for `self.meet(element_indexes)`"""
        return self.meet(element_indexes)

    def leq_elements(self, a_index: int, b_index: int) -> bool:
        """Compare two elements of POSet by their indexes"""
        return self._leq_elements_nocache(a_index, b_index)

    def _leq_elements_nocache(self, a_index: int, b_index: int) -> bool:
        """Compare two elements of POSet by their indexes (without using cache)"""
        return self._leq_func(self._elements[a_index], self._elements[b_index])

    def _leq_elements_cache(self, a_index: int, b_index: int) -> bool:
        """Compare two elements of POSet by their indexes (using cache)"""
        key = (a_index, b_index)
        if key in self._cache_leq:
            res = self._cache_leq[key]
        elif b_index in self._cache_descendants:
            res = a_index in self._cache_descendants[b_index]
        elif a_index in self._cache_ancestors:
            res = b_index in self._cache_ancestors[a_index]
        else:
            res = self._leq_elements_nocache(a_index, b_index)
            self._cache_leq[key] = res
        return res

    def __getitem__(self, item: int or slice or Collection) -> Any:
        return slice_list(self.elements, item) if not isinstance(item, int) else self.elements[item]

    def __and__(self, other: 'POSet'):
        assert self._leq_func == other.leq_func, \
            'POSet.__and__ assertion. Compared posets have to have the same leq_func'
        elements_and = [x for x in self._elements if x in other._elements]

        s = POSet(elements_and, self._leq_func, use_cache=self._use_cache)
        if self._use_cache:
            self._combine_multiple_caches(other, s, drop_notcommon_elements=False)

        return s

    def __or__(self, other: 'POSet'):
        assert self._leq_func == other.leq_func, \
            'POSet.__or__ assertion. Compared posets have to have the same leq_func'
        elements_or = [x for x in self._elements]  # Using lists to keep the elements indices kind of the same
        elements_or += [x for x in other._elements if x not in elements_or]

        s = POSet(elements_or, self._leq_func, use_cache=self._use_cache)
        if self._use_cache:
            self._combine_multiple_caches(other, s, drop_notcommon_elements=True)

        return s

    def __xor__(self, other: 'POSet'):
        assert self._leq_func == other.leq_func, \
            'POSet.__xor__ assertion. Compared posets have to have the same leq_func'
        elements_xor = [x for x in self._elements if x not in other._elements]
        elements_xor += [x for x in other._elements if x not in self._elements]

        s = POSet(elements_xor, self._leq_func, use_cache=self._use_cache)
        if self._use_cache:
            self._combine_multiple_caches(other, s, drop_notcommon_elements=True)

        return s

    def __sub__(self, other: 'POSet'):
        assert self._leq_func == other.leq_func, \
            'POSet.__sub__ assertion. Compared posets have to have the same leq_func'
        elements_sub = [x for x in self._elements if x not in other._elements]

        s = POSet(elements_sub, self._leq_func, use_cache=self._use_cache)
        if self._use_cache:
            self._combine_multiple_caches(other, s, drop_notcommon_elements=False)

        return s

    @staticmethod
    def _combine_caches(cache_a, elements_a, cache_b, elements_b, elements_combined):
        """Combine caches of two POSets into one big cache

        Parameters
        ----------
        cache_a : dict
            A cache from POSet A (ex. A._cache_leq, A._cache_subconcepts)
        elements_a : list
            A list of elements from POSet A
        cache_b : dict
            A cache from POSet B (ex. B._cache_leq, B._cache_subconcepts)
        elements_b : list
            A list of elements from POSet B
        elements_combined : list
            A list of elements to keep in combined cache

        Returns
        -------
        cache_combined : dict
        """
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

    def _combine_multiple_caches(self, other: 'POSet', poset_combined: 'POSet', drop_notcommon_elements: bool):
        """Combine all the caches of the self POSet and ``other`` POSet at once and save them to ``poset_combined``"""
        elements_and = {x for x in self._elements if x in other._elements}
        cache_names = ['_cache_leq', '_cache_descendants', '_cache_ancestors',
                       '_cache_children', '_cache_parents']

        for cache_name in cache_names:
            cache_comb = self._combine_caches(
                self.__dict__[cache_name], self._elements,
                other.__dict__[cache_name], other._elements,
                poset_combined._elements
            )

            if drop_notcommon_elements and cache_name in cache_names[1:5]:
                for idx in list(cache_comb):
                    if poset_combined._elements[idx] not in elements_and:
                        del cache_comb[idx]

            poset_combined.__dict__[cache_name] = cache_comb

    def __len__(self):
        return len(self._elements)

    def __contains__(self, item):
        return item in self._elements_to_index_map

    def __delitem__(self, key):
        del self._elements_to_index_map[self._elements[key]]
        del self._elements[key]

        def decr_idx(idx, threshold):
            return idx - 1 if idx > threshold else idx

        self._elements_to_index_map = {el: decr_idx(idx, key) for el, idx in self._elements_to_index_map.items()}

        if self._use_cache:
            def reconnect_relatives(item):
                relatives = []
                for i, rels in enumerate(['ancestors', 'descendants', 'parents', 'children']):
                    dct = self.__dict__['_cache_'+rels]
                    if item in dct:
                        relatives.append(dct[item])
                        del dct[item]
                    else:
                        relatives.append(set())
                ancestors, descendants, parents, children = relatives

                for parent in parents:
                    if parent not in self._cache_children:
                        continue
                    new_children = (self._cache_children[parent] | children) - {item}
                    for new_child in list(new_children):
                        new_children -= self._cache_descendants[new_child]
                    self._cache_children[parent] = frozenset(new_children)

                for child in children:
                    if child not in self._cache_parents:
                        continue
                    new_parents = (self._cache_parents[child] | parents) - {item}
                    for new_parent in list(new_parents):
                        new_parents -= self._cache_ancestors[new_parent]
                    self._cache_parents[child] = frozenset(new_parents)

                for ancestor in ancestors:
                    if ancestor not in self._cache_descendants:
                        continue
                    self._cache_descendants[ancestor] = self._cache_descendants[ancestor] - {item}

                for descendant in descendants:
                    if descendant not in self._cache_ancestors:
                        continue
                    self._cache_ancestors[descendant] = self._cache_ancestors[descendant] - {item}

            def decrement_dict(dct, threshold):
                if len(dct) == 0:
                    return {}

                dct_decr = {}

                k, v = dct.popitem()
                k_tuple_flag, k_int_flag = isinstance(k, tuple), isinstance(k, int)
                v_set_flag, v_bool_flag = isinstance(v, (set, frozenset)), isinstance(v, bool)
                dct[k] = v

                for k, v in dct.items():
                    if (k_tuple_flag and threshold in k) \
                            or (k_int_flag and threshold == k):
                        continue

                    if k_tuple_flag:
                        k_decr = tuple([decr_idx(idx, threshold) for idx in k])
                    elif k_int_flag:
                        k_decr = decr_idx(k, threshold)
                    else:
                        raise ValueError

                    if v_set_flag:
                        v_decr = frozenset({decr_idx(idx, threshold) for idx in v if idx != threshold})
                    elif v_bool_flag:
                        v_decr = v
                    else:
                        raise ValueError

                    dct_decr[k_decr] = v_decr
                return dct_decr

            reconnect_relatives(key)
            for dict_name in ['leq', 'descendants', 'ancestors', 'children', 'parents']:
                self.__dict__["_cache_"+dict_name] = decrement_dict(self.__dict__["_cache_"+dict_name], key)

    def add(self, element: Any, fill_up_cache: bool = True):
        """Add an ``element`` to POSet. Automatically fill up the comparison caches if needed"""
        if element in self._elements_to_index_map:
            return

        el_i_new = len(self._elements)
        if self._use_cache:
            if fill_up_cache:
                self._cache_leq[(el_i_new, el_i_new)] = True

                self._cache_children[el_i_new], self._cache_descendants[el_i_new] = self.trace_element(element, 'up')
                self._cache_parents[el_i_new], self._cache_ancestors[el_i_new] = self.trace_element(element, 'down')

                for el_i in range(el_i_new):  # iterate through all old elements:
                    if el_i in self._cache_descendants[el_i_new]:  # elements, that are smaller than the new element
                        self._cache_ancestors[el_i] = self._cache_ancestors[el_i] | {el_i_new}
                        self._cache_leq[(el_i, el_i_new)] = True
                        self._cache_leq[(el_i_new, el_i)] = False

                        if el_i in self._cache_children[el_i_new]:
                            self._cache_parents[el_i] = \
                                {el_i_new} | (self._cache_parents[el_i] - self._cache_ancestors[el_i_new])

                        continue

                    if el_i in self._cache_ancestors[el_i_new]:  # elements, that are bigger than the new element
                        self._cache_descendants[el_i] = self._cache_descendants[el_i] | {el_i_new}
                        self._cache_leq[(el_i, el_i_new)] = False
                        self._cache_leq[(el_i_new, el_i)] = True

                        if el_i in self._cache_parents[el_i_new]:
                            self._cache_children[el_i] = \
                                {el_i_new} | (self._cache_children[el_i] - self._cache_descendants[el_i_new])
                        continue

                    # el_i and el_i_new are incomparable
                    self._cache_leq[(el_i, el_i_new)] = False
                    self._cache_leq[(el_i_new, el_i)] = False

            else:
                self._cache_descendants = {}
                self._cache_ancestors = {}
                self._cache_children = {}
                self._cache_parents = {}

        self._elements.append(element)
        self._elements_to_index_map[element] = el_i_new

    def remove(self, element: Any):
        """Remove an ``element`` from POSet"""
        idx = self.index(element)
        del self[idx]

    def __eq__(self, other: 'POSet'):
        # Test if two POSets contain the same elements
        same_elements = set(self._elements) == set(other._elements)
        if not same_elements:
            return False

        # Empirically test is two POSets have the same leq_func
        # (i.e. corresponding elements have the same set of corresponding subelements)
        self_i_other_i_map = {self_i: other.index(el) for self_i, el in enumerate(self._elements)}
        other_i_self_i_map = {other_i: self_i for self_i, other_i in self_i_other_i_map.items()}
        for self_i, el in enumerate(self._elements):
            self_subs = self.descendants(self_i)
            other_subs = other.descendants(self_i_other_i_map[self_i])
            other_subs = {other_i_self_i_map[other_i] for other_i in other_subs}
            if self_subs != other_subs:
                return False
        return True

    def fill_up_leq_cache(self):
        """Compare all the elements of POSet at once"""
        assert self._use_cache,\
            "POSet.fill_up_leq_cache assertion. " \
            "The cache can only be filled up if it is enabled (`POSet.use_cache = True`)"

        for i in range(len(self)):
            for j in range(len(self)):
                if (i, j) not in self._cache_leq:
                    self.leq_elements(i, j)

    def fill_up_descendants_cache(self):
        """Compute all descendants of each element in a POSet"""
        assert self._use_cache, \
            "POSet.fill_up_descendants_cache assertion. " \
            "The cache can only be filled up if it is enabled (`POSet.use_cache = True`)"

        for i in range(len(self)):
            self.descendants(i)

    def fill_up_ancestors_cache(self):
        """Compute all ancestors of each element in a POSet"""
        assert self._use_cache, \
            "POSet.fill_up_ancestors_cache assertion. " \
            "The cache can only be filled up if it is enabled (`POSet.use_cache = True`)"

        for i in range(len(self)):
            self.ancestors(i)

    def fill_up_children_cache(self):
        """Compute children of each element in a POSet"""
        assert self._use_cache, \
            "POSet.fill_up_children_cache assertion. " \
            "The cache can only be filled up if it is enabled (`POSet.use_cache = True`)"

        for i in range(len(self)):
            self.children(i)

    def fill_up_parents_cache(self):
        """Compute parents of each element in a POSet"""
        assert self._use_cache, \
            "POSet.fill_up_parents_cache assertion. " \
            "The cache can only be filled up if it is enabled (`POSet.use_cache = True`)"

        for i in range(len(self)):
            self.parents(i)

    def fill_up_caches(self):
        """Fill up each cache of POSet"""
        self.fill_up_leq_cache()
        self.fill_up_descendants_cache()
        self.fill_up_ancestors_cache()
        self.fill_up_children_cache()
        self.fill_up_parents_cache()

    def trace_element(self, element: Any, direction: str) -> Tuple[Set[int], Set[int]]:
        """Get the sets of descendants and children (or ancestors and parents) of an ``element`` in the POSet

        Parameters
        ----------
        element :
            An element to compare POSet elements with (not necessary from the POSet itself)
        direction : {'up', 'down'}
            If set 'up' then compute all (and direct) descendants of an ``element``,
            if set 'down' then compute all (and direct) ancestors of an ``element``

        Returns
        -------
        final_elements : set
            A set of children (or parents) of ``element`` in the POSet
        traced_elements : set
            A set of descendants (or ancestors) of ``element`` in the POSet
        """
        if direction == 'down':
            start_elements = self.tops
            compare_func = self._leq_func
            next_elements_func = self.children
        elif direction == 'up':
            start_elements = self.bottoms
            compare_func = lambda a, b: self._leq_func(b, a)
            next_elements_func = self.parents
        else:
            raise ValueError('``direction`` value should be either "up" or "down"')

        return self._trace_elements_both_directions(element, start_elements, compare_func, next_elements_func)

    def _trace_elements_both_directions(self, element, start_elements, compare_func, next_elements_func) \
            -> Tuple[Set[int], Set[int]]:
        """Get the sets of all the final and traced elements compared with ``element`` by ``compare_func``"""
        traced_elements, final_elements = set(), set()

        elements_to_visit = [el_i for el_i in start_elements if compare_func(element, self._elements[el_i])]

        while len(elements_to_visit) > 0:
            el_i = elements_to_visit.pop(0)
            traced_elements.add(el_i)

            next_elements = {el_i_next for el_i_next in next_elements_func(el_i)
                             if compare_func(element, self._elements[el_i_next])}

            if len(next_elements) > 0:
                elements_to_visit += list(next_elements - traced_elements - set(elements_to_visit))
            else:
                final_elements.add(el_i)

        return final_elements, traced_elements

    @classmethod
    def _closed_relation_cache_by_direct_cache(cls, direct_relation_cache):
        """Compute the cache of a "closed" relation given only "direct" one

        (ex. _cache_parents -> _cache_ancestors)"""
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
        """Compute the cache of "direct" relation given only the "closed" one

        (ex. _cache_ancestors -> _cache_parents)
        """
        direct_relation_cache = {}
        for el_i, elems_rel_all in closed_relation_cache.items():
            direct_relation_cache[el_i] = elems_rel_all.copy()
            for el_i_rel in elems_rel_all:
                direct_relation_cache[el_i] -= closed_relation_cache[el_i_rel]

        direct_relation_cache = {k: frozenset(vs) for k, vs in direct_relation_cache.items()}
        return direct_relation_cache

    @staticmethod
    def _transpose_hierarchy(hierarchy_dict: Dict[int, Collection[int]]) -> Dict[int, FrozenSet[int]]:
        """Return transposed hierarchy of elements (i.e. turn ancestors into descendants and vice versa)

        Parameters
        ----------
        hierarchy_dict: `dict` of type {`int`: `list` of `int`}
            Ancestors or descendants of POSet

        Returns
        -------
        new_dict: `dict` of type {`int`: `FrozenSet` of `int`}
            Ancestors if descendants are given, descendants if ancestors are given
        """
        new_dict = {}
        for k, vs in hierarchy_dict.items():
            if k not in new_dict:
                new_dict[k] = set()
            for v in vs:
                new_dict[v] = new_dict.get(v, set()) | {k}
        new_dict = {k: frozenset(vs) for k, vs in new_dict.items()}
        return new_dict

    def to_networkx(self, direction: str or None = 'down'):
        """Construct networkx.Graph (or DiGraph) based on POSet relations and ``direction``"""
        return self._to_networkx(direction, 'element')

    def _to_networkx(self, direction, element_attr_name):
        if not LIB_INSTALLED['networkx']:
            class_name = self.__class__.__name__
            msg = f"Networkx package should be installed in order to convert {class_name} to networkx graph"
            raise ModuleNotFoundError(msg)

        import networkx as nx
        if direction == 'up':
            G = nx.DiGraph(self.parents_dict)
        elif direction == 'down':
            G = nx.DiGraph(self.children_dict)
        elif direction is None:
            G = nx.Graph(self.children_dict)
        else:
            raise ValueError("Unknown value for graph ``direction``. Possible values are {'up', 'down', None} ")

        nx.set_node_attributes(G, dict(enumerate(self.elements)), element_attr_name)
        return G

    def _update_element(self, old_element, new_element):
        """Replace ``old_element`` by ``new_element``. It's assumed both elements have the same position in hierarchy"""
        idx = self.index(old_element)
        self._elements[idx] = new_element
        del self._elements_to_index_map[old_element]
        self._elements_to_index_map[new_element] = idx
