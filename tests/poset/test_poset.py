from fcapy.poset import POSet
from fcapy import LIB_INSTALLED
import pytest
from copy import deepcopy
import networkx as nx


def test_init():
    s = POSet()
    assert s.elements == []
    assert s._elements_to_index_map == {}

    elements = ['', 'a', 'b', 'ab']
    leq_func = lambda x, y: set(x) & set(y) == set(x)

    for use_cache in [False, True]:
        s = POSet(elements, leq_func, use_cache=use_cache)
        assert s._elements == elements
        assert s._leq_func == leq_func
        assert s._use_cache == use_cache

    s = POSet(elements, leq_func)
    assert s._use_cache
    assert s._cache_leq == {}
    assert s._cache_descendants == {}
    assert s._cache_ancestors == {}
    assert s._cache_children == {}
    assert s._cache_parents == {}
    assert s._elements_to_index_map == {'': 0, 'a': 1, 'b':2, 'ab': 3}


def test_leq_elements():
    elements = ['', 'a', 'b', 'ab']
    leq_func = lambda x, y: set(x) & set(y) == set(x)
    for use_cache in [False, True]:
        s = POSet(elements, leq_func, use_cache=use_cache)
        leq = s.leq_elements(1, 2)
        assert not leq

        leq = s.leq_elements(0, 2)
        assert leq

        leq = s.leq_elements(2, 0)
        assert not leq

        leq = s.leq_elements(2, 2)
        assert leq


def test_fill_up_caches():
    elements = ['', 'a', 'b', 'ab']
    leq_func = lambda x, y: set(x) & set(y) == set(x)
    s = POSet(elements, leq_func, use_cache=False)
    with pytest.raises(AssertionError):
        s.fill_up_caches()

    s = POSet(elements, leq_func, use_cache=True)
    s.fill_up_leq_cache()
    leq_cache_true = {
        (0, 0): True,  (0, 1): True,  (0, 2): True,  (0, 3): True,
        (1, 0): False, (1, 1): True,  (1, 2): False,  (1, 3): True,
        (2, 0): False, (2, 1): False, (2, 2): True,  (2, 3): True,
        (3, 0): False, (3, 1): False, (3, 2): False, (3, 3): True,
    }
    assert s._cache_leq == leq_cache_true

    s.fill_up_descendants_cache()
    subelements_cache_true = {0: set(), 1: {0}, 2: {0}, 3: {0, 1, 2}}
    assert s._cache_descendants == subelements_cache_true

    s.fill_up_ancestors_cache()
    superelements_cache_true = {0: {1, 2, 3}, 1: {3}, 2: {3}, 3: set()}
    assert s._cache_ancestors == superelements_cache_true

    s.fill_up_children_cache()
    dsubelements_cache_true = {0: set(), 1: {0}, 2: {0}, 3: {1, 2}}
    assert s._cache_children == dsubelements_cache_true

    s.fill_up_parents_cache()
    dsupelements_cache_true = {0: {1, 2}, 1: {3}, 2: {3}, 3: set()}
    assert s._cache_parents == dsupelements_cache_true


def test_join_elements_supremum():
    elements = ['a', 'b', 'ab', 'c']
    leq_func = lambda x, y: set(x) & set(y) == set(x)
    s = POSet(elements, leq_func)

    for func in [s.join, s.supremum]:
        join = func([0, 1])
        assert join == 2

        join = func([0, 2])
        assert join == 2

        assert func() is None

        join = func([1, 3])
        assert join is None


def test_meet_elements_infimum():
    elements = ['a', 'b', 'ab', 'ac']
    leq_func = lambda x, y: set(x) & set(y) == set(x)
    s = POSet(elements, leq_func)

    for func in [s.meet, s.infimum]:
        meet = func([2, 3])
        assert meet == 0

        meet = func([0, 2])
        assert meet == 0

        assert func() is None

        meet = func([1, 3])
        assert meet is None


def test_getitem():
    elements = ['', 'a', 'b', 'ab']
    leq_func = lambda x, y: set(x) & set(y) == set(x)
    s = POSet(elements, leq_func)
    assert s[0] == ''
    assert s[1] == 'a'
    assert s[2] == 'b'
    assert s[3] == 'ab'

    assert s[:2] == elements[:2]
    assert s[[1,2,3]] == elements[1:]


def test_eq():
    elements = ['', 'a', 'b', 'ab']
    leq_func = lambda x, y: set(x) & set(y) == set(x)
    s = POSet(elements, leq_func)

    elements1 = ['a', 'b', 'ab', '']
    leq_func1 = lambda a, b: set(a) & set(b) == set(a)
    other = POSet(elements1, leq_func1)
    assert s == other

    other = POSet(elements[:-1], leq_func)
    assert s != other

    elements_1 = ['', 'a', 'b', 'abc']
    other = POSet(elements_1, leq_func)
    assert s != other

    leq_func_1 = lambda x, y: not(set(x) & set(y) == set(x))
    other = POSet(elements, leq_func_1)
    assert s != other

    other = POSet(elements_1, leq_func_1)
    assert s != other


def test_and():
    elements_1 = ['', 'a', 'b']
    elements_2 = ['a', 'b', 'ab']
    elements_and = ['a', 'b']
    leq_func = lambda x, y: set(x) & set(y) == set(x)

    # Test if intersection operation is working
    for use_cache in [False, True]:
        s1 = POSet(elements_1, leq_func, use_cache=use_cache)
        s2 = POSet(elements_2, leq_func, use_cache=use_cache)
        s_and_true = POSet(elements_and, leq_func, use_cache=use_cache)
        s_and_fact = s1 & s2
        assert s_and_fact == s_and_true

    # Test if cache of intersection is intersection of filled up caches
    s1 = POSet(elements_1, leq_func, use_cache=True)
    s1.fill_up_caches()
    s2 = POSet(elements_2, leq_func, use_cache=True)
    s2.fill_up_caches()
    s_and_true = POSet(elements_and, leq_func)
    s_and_true.fill_up_caches()

    s_and_fact = s1 & s2
    assert s_and_fact == s_and_true
    assert s_and_fact._cache_leq == s_and_true._cache_leq
    assert s_and_fact._cache_descendants == s_and_true._cache_descendants
    assert s_and_fact._cache_ancestors == s_and_true._cache_ancestors
    assert s_and_fact._cache_children == s_and_true._cache_children
    assert s_and_fact._cache_parents == s_and_true._cache_parents

    # Test if cache of intersection is union of caches
    s1 = POSet(elements_1, leq_func, use_cache=True)
    s1.leq_elements(0, 1)
    s2 = POSet(elements_1, leq_func, use_cache=True)
    s2.leq_elements(1, 2)
    s_and_true = POSet(elements_1, leq_func)
    s_and_true.leq_elements(0, 1)
    s_and_true.leq_elements(1, 2)

    s_and_fact = s1 & s2
    assert s_and_fact == s_and_true
    assert s_and_fact._cache_leq == s_and_true._cache_leq
    assert s_and_fact._cache_descendants == s_and_true._cache_descendants
    assert s_and_fact._cache_ancestors == s_and_true._cache_ancestors
    assert s_and_fact._cache_children == s_and_true._cache_children
    assert s_and_fact._cache_parents == s_and_true._cache_parents


def test_or():
    elements_1 = ['', 'a', 'b']
    elements_2 = ['a', 'b', 'ab']
    elements_or = ['', 'a', 'b', 'ab']
    leq_func = lambda x, y: set(x) & set(y) == set(x)

    # Test if union operation is working
    for use_cache in [False, True]:
        s1 = POSet(elements_1, leq_func, use_cache=use_cache)
        s2 = POSet(elements_2, leq_func, use_cache=use_cache)
        s_or_true = POSet(elements_or, leq_func, use_cache=use_cache)
        s_or_fact = s1 | s2
        assert s_or_fact == s_or_true

    # Test if cache of union is (almost) union of filled up caches
    s1 = POSet(elements_1, leq_func, use_cache=True)
    s1.fill_up_caches()
    s2 = POSet(elements_2, leq_func, use_cache=True)
    s2.fill_up_caches()
    s_or_true = POSet(elements_or, leq_func, use_cache=True)
    s_or_true.fill_up_caches()
    del s_or_true._cache_leq[(0, 3)], s_or_true._cache_leq[(3, 0)]
    del s_or_true._cache_descendants[0], s_or_true._cache_descendants[3]
    del s_or_true._cache_ancestors[0], s_or_true._cache_ancestors[3]
    del s_or_true._cache_children[0], s_or_true._cache_children[3]
    del s_or_true._cache_parents[0], s_or_true._cache_parents[3]

    s_or_fact = s1 | s2
    assert s_or_fact == s_or_true
    assert s_or_fact._cache_leq == s_or_true._cache_leq
    assert s_or_fact._cache_descendants == s_or_true._cache_descendants
    assert s_or_fact._cache_ancestors == s_or_true._cache_ancestors
    assert s_or_fact._cache_children == s_or_true._cache_children
    assert s_or_fact._cache_parents == s_or_true._cache_parents


def test_xor():
    elements_1 = ['', 'a', 'b']
    elements_2 = ['a', 'b', 'ab']
    elements_xor = ['', 'ab']
    leq_func = lambda x,y: set(x) & set(y) == set(x)

    # Test if xor operation is working
    for use_cache in [False, True]:
        s1 = POSet(elements_1, leq_func, use_cache=use_cache)
        s2 = POSet(elements_2, leq_func, use_cache=use_cache)
        s_xor_true = POSet(elements_xor, leq_func, use_cache=use_cache)
        s_xor_fact = s1 ^ s2
        assert s_xor_fact == s_xor_true

    # Test if cache of xor is xor of filled up caches
    s1 = POSet(elements_1, leq_func, use_cache=True)
    s1.fill_up_caches()
    s2 = POSet(elements_2, leq_func, use_cache=True)
    s2.fill_up_caches()
    s_xor_true = POSet(elements_xor, leq_func, use_cache=True)
    s_xor_true.fill_up_caches()
    del s_xor_true._cache_leq[(0, 1)], s_xor_true._cache_leq[(1, 0)]
    s_xor_true._cache_descendants = {}
    s_xor_true._cache_ancestors = {}
    s_xor_true._cache_children = {}
    s_xor_true._cache_parents = {}

    s_xor_fact = s1 ^ s2
    assert s_xor_fact == s_xor_true
    assert s_xor_fact._cache_leq == s_xor_true._cache_leq
    assert s_xor_fact._cache_descendants == s_xor_true._cache_descendants
    assert s_xor_fact._cache_ancestors == s_xor_true._cache_ancestors
    assert s_xor_fact._cache_children == s_xor_fact._cache_children
    assert s_xor_fact._cache_parents == s_xor_fact._cache_parents


def test_subtraction():
    elements_1 = ['', 'a', 'b']
    elements_2 = ['', 'ab']
    elements_sub = ['a', 'b']
    leq_func = lambda x,y: set(x) & set(y) == set(x)

    # Test if subtraction operation is working
    for use_cache in [False, True]:
        s1 = POSet(elements_1, leq_func, use_cache=use_cache)
        s2 = POSet(elements_2, leq_func, use_cache=use_cache)
        s_sub_true = POSet(elements_sub, leq_func, use_cache=use_cache)
        s_sub_fact = s1 - s2
        assert s_sub_fact == s_sub_true

    # Test if cache of subtraction is subtraction of filled up caches
    s1 = POSet(elements_1, leq_func, use_cache=True)
    s1.fill_up_caches()
    s2 = POSet(elements_2, leq_func, use_cache=True)
    s2.fill_up_caches()
    s_sub_true = POSet(elements_sub, leq_func, use_cache=True)
    s_sub_true.fill_up_caches()

    s_sub_fact = s1 - s2
    assert s_sub_fact == s_sub_true
    assert s_sub_fact._cache_leq == s_sub_true._cache_leq
    assert s_sub_fact._cache_descendants == s_sub_true._cache_descendants
    assert s_sub_fact._cache_ancestors == s_sub_true._cache_ancestors
    assert s_sub_fact._cache_children == s_sub_true._cache_children
    assert s_sub_fact._cache_parents == s_sub_true._cache_parents


def test_len():
    elements = ['', 'a', 'b', 'ab']
    leq_func = lambda x,y: set(x) & set(y) == set(x)
    s = POSet(elements, leq_func)
    assert len(s) == len(elements)


def test_delitem():
    elements = ['', 'a', 'b', 'ab']
    del_i = 1
    elements_del = [el for i, el in enumerate(elements) if i != del_i]
    leq_func = lambda x, y: set(x) & set(y) == set(x)

    # Test if delitem operation is working
    for use_cache in [False, True]:
        s = POSet(elements, leq_func, use_cache=use_cache)
        s_del_true = POSet(elements_del, leq_func, use_cache=use_cache)
        del s[del_i]
        assert s == s_del_true

    # Test if cache is changed correctly after removing an element
    s = POSet(elements, leq_func, use_cache=True)
    s_del_true = POSet(elements_del, leq_func, use_cache=True)
    s.fill_up_caches()
    s_del_true.fill_up_caches()

    del s[del_i]
    assert s == s_del_true
    assert s._cache_leq == s_del_true._cache_leq
    assert s._cache_descendants == s_del_true._cache_descendants
    assert s._cache_ancestors == s_del_true._cache_ancestors
    assert s._cache_children == s_del_true._cache_children
    assert s._cache_parents == s_del_true._cache_parents


def test_add():
    elements = ['', 'b', 'ab']
    elements_add = ['', 'b', 'ab', 'a']
    new_element = 'a'
    leq_func = lambda x, y: set(x) & set(y) == set(x)

    # Test if add operation is working
    for use_cache in [False, True]:
        s = POSet(elements, leq_func, use_cache=use_cache)
        s.add(new_element)
        s_add_true = POSet(elements_add, leq_func, use_cache=use_cache)
        assert s == s_add_true

    # Test if cache is not changed after adding new element
    s_add_true = POSet(elements_add, leq_func, use_cache=True)
    s_add_true.fill_up_caches()

    s = POSet(elements, leq_func, use_cache=True)
    s.fill_up_caches()
    cache_true = deepcopy(s._cache_leq)
    s.add(new_element, fill_up_cache=False)
    assert s._cache_leq == cache_true
    assert all([s.elements[s.index(el)] == el for el in s.elements])

    s = POSet(elements, leq_func, use_cache=True)
    s.fill_up_caches()
    s.add(new_element, fill_up_cache=True)
    assert s == s_add_true
    assert s._cache_leq == s_add_true._cache_leq
    assert s._cache_descendants == s_add_true._cache_descendants
    assert s._cache_ancestors == s_add_true._cache_ancestors
    assert s._cache_children == s_add_true._cache_children
    assert s._cache_parents == s_add_true._cache_parents
    assert all([s.elements[s.index(el)] == el for el in s.elements])

    s = POSet(['', 'ab'], leq_func)
    s.fill_up_caches()
    s_add_true = POSet(['', 'ab', 'a'], leq_func)
    s_add_true.fill_up_caches()

    s.add('a')
    assert s == s_add_true
    assert s._cache_leq == s_add_true._cache_leq
    assert s._cache_descendants == s_add_true._cache_descendants
    assert s._cache_ancestors == s_add_true._cache_ancestors
    assert s._cache_children == s_add_true._cache_children
    assert s._cache_parents == s_add_true._cache_parents
    assert all([s.elements[s.index(el)] == el for el in s.elements])


def test_remove():
    elements = ['', 'a', 'b', 'ab']
    remove_i = 1
    elements_remove = [el for i, el in enumerate(elements) if i != remove_i]
    leq_func = lambda x,y: set(x) & set(y) == set(x)

    # Test if delitem operation is working
    for use_cache in [False, True]:
        s = POSet(elements, leq_func, use_cache=use_cache)
        s_remove_true = POSet(elements_remove, leq_func, use_cache=use_cache)
        s.remove(elements[remove_i])
        assert s == s_remove_true

    # Test if cache is changed correctly after removing an element
    s = POSet(elements, leq_func, use_cache=True)
    s_remove_true = POSet(elements_remove, leq_func, use_cache=True)
    s.fill_up_caches()
    s_remove_true.fill_up_caches()

    s.remove(elements[remove_i])
    assert s == s_remove_true
    assert s._cache_leq == s_remove_true._cache_leq
    assert s._cache_descendants == s_remove_true._cache_descendants
    assert s._cache_ancestors == s_remove_true._cache_ancestors
    assert s._cache_children == s_remove_true._cache_children
    assert s._cache_parents == s_remove_true._cache_parents
    assert all([s.elements[s.index(el)] == el for el in s.elements])

    # Test if cache is changed correctly after removing an element (another case)
    s = POSet(['', 'a', 'ab'], leq_func, use_cache=True)
    s_remove_true = POSet(['', 'ab'], leq_func, use_cache=True)
    s.fill_up_caches()
    s_remove_true.fill_up_caches()

    s.remove('a')
    assert s == s_remove_true
    assert s._cache_leq == s_remove_true._cache_leq
    assert s._cache_descendants == s_remove_true._cache_descendants
    assert s._cache_ancestors == s_remove_true._cache_ancestors
    assert s._cache_children == s_remove_true._cache_children
    assert s._cache_parents == s_remove_true._cache_parents
    assert all([s.elements[s.index(el)] == el for el in s.elements])


def test_super_elements():
    elements = ['', 'a', 'b', 'ab']
    leq_func = lambda x,y: set(x) & set(y) == set(x)
    s = POSet(elements, leq_func)
    sups_true = {0: {1, 2, 3}, 1: {3}, 2: {3}, 3: set()}

    sups_fact = {idx: s.ancestors(idx) for idx in range(len(elements))}
    assert sups_fact == sups_true
    assert s.ancestors_dict == sups_true


def test_sub_elements():
    elements = ['', 'a', 'b', 'ab', 'c']
    leq_func = lambda x,y: set(x) & set(y) == set(x)
    s = POSet(elements, leq_func)
    subs_true = {0: set(), 1: {0}, 2: {0}, 3: {0, 1, 2}, 4: {0}}

    subs_fact = {idx: s.descendants(idx) for idx in range(len(elements))}
    assert subs_fact == subs_true
    assert s.descendants_dict == subs_true


def test_direct_super_elements():
    elements = ['', 'a', 'b', 'ab']
    leq_func = lambda x,y: set(x) & set(y) == set(x)
    s = POSet(elements, leq_func)
    dsups_true = {0: {1, 2}, 1: {3}, 2: {3}, 3: set()}

    dsups_fact = {idx: s.parents(idx) for idx in range(len(elements))}
    assert dsups_fact == dsups_true
    assert s.parents_dict == dsups_true


def test_direct_sub_elements():
    elements = ['', 'a', 'b', 'ab', 'c']
    leq_func = lambda x,y: set(x) & set(y) == set(x)
    s = POSet(elements, leq_func)
    dsubs_true = {0: set(), 1: {0}, 2: {0}, 3: {1, 2}, 4: {0}}

    dsubs_fact = {idx: s.children(idx) for idx in range(len(elements))}
    assert dsubs_fact == dsubs_true
    assert s.children_dict == dsubs_true


def test_closed_cache_by_direct_cache():
    elements = ['', 'a', 'b', 'ab', 'c']
    leq_func = lambda x,y: set(x) & set(y) == set(x)
    s = POSet(elements, leq_func)
    s.fill_up_caches()

    closed_subelements_cache = s._closed_relation_cache_by_direct_cache(s._cache_children)
    assert closed_subelements_cache == s._cache_descendants

    closed_superelements_cache = s._closed_relation_cache_by_direct_cache(s._cache_parents)
    assert closed_superelements_cache == s._cache_ancestors


def test_direct_cache_by_closed_cache():
    elements = ['', 'a', 'b', 'ab', 'c']
    leq_func = lambda x,y: set(x) & set(y) == set(x)
    s = POSet(elements, leq_func)
    s.fill_up_caches()

    direct_subelements_cache = s._direct_relation_cache_by_closed_cache(s._cache_descendants)
    assert direct_subelements_cache == s._cache_children

    direct_superelements_cache = s._direct_relation_cache_by_closed_cache(s._cache_ancestors)
    assert direct_superelements_cache == s._cache_parents


def test_index():
    elements = ['', 'a', 'b', 'ab', 'c']
    leq_func = lambda x,y: set(x) & set(y) == set(x)
    s = POSet(elements, leq_func)

    assert all([s.elements[s.index(el)] == el for el in s.elements])
    assert max(s._elements_to_index_map.values()) == len(s.elements)-1

    s.add('d')
    assert all([s.elements[s.index(el)] == el for el in s.elements])
    assert max(s._elements_to_index_map.values()) == len(s.elements) - 1

    s.remove('b')
    assert all([s.elements[s.index(el)] == el for el in s.elements])
    assert max(s._elements_to_index_map.values()) == len(s.elements) - 1

    s1 = POSet(elements[:4], leq_func)
    s2 = POSet(elements[3:], leq_func)
    s_and = s1 & s2
    assert all([s_and.elements[s_and.index(el)] == el for el in s_and.elements])
    assert max(s_and._elements_to_index_map.values()) == len(s_and.elements) - 1
    s_or = s1 | s2
    assert all([s_or.elements[s_or.index(el)] == el for el in s_or.elements])
    assert max(s_or._elements_to_index_map.values()) == len(s_or.elements) - 1
    s_xor = s1 ^ s2
    assert all([s_xor.elements[s_xor.index(el)] == el for el in s_xor.elements])
    assert max(s_xor._elements_to_index_map.values()) == len(s_xor.elements) - 1


def test_top_bottom_elements():
    elements = ['', 'a', 'b', 'ab', 'c']
    leq_func = lambda x,y: set(x) & set(y) == set(x)
    s = POSet(elements, leq_func)

    top_elements_true = [3, 4]
    bottom_elements_true = [0]
    assert s.tops == top_elements_true
    assert s.bottoms == bottom_elements_true


def test_trace_element():
    elements = ['a', 'ab', 'c', 'abc']
    leq_func = lambda x,y: set(x) & set(y) == set(x)
    s = POSet(elements, leq_func)

    final_down_elems_true = {
        '': {0, 2},
        'abcd': set(),
        'ac': {3},
        'ab': {1},
    }
    traced_down_elems_true = {
        '': {3, 1, 0, 2},
        'abcd': set(),
        'ac': {3},
        'ab': {3, 1},
    }
    final_up_elems_true = {
        '': set(),
        'abcd': {3},
        'ac': {0, 2},
        'ab': {1}
    }
    traced_up_elems_true = {
        '': set(),
        'abcd': {0, 2, 1, 3},
        'ac': {0, 2},
        'ab': {0, 1},
    }
    for el in final_down_elems_true.keys():
        final_down_elems, traced_down_elems = s.trace_element(el, 'down')
        assert final_down_elems == final_down_elems_true[el], f'Error at element "{el}" when tracing down'
        assert traced_down_elems == traced_down_elems_true[el], f'Error at element "{el}" when tracing down'

        final_up_elems, traced_up_elems = s.trace_element(el, 'up')
        assert final_up_elems == final_up_elems_true[el], f'Error at element "{el}" when tracing up'
        assert traced_up_elems == traced_up_elems_true[el], f'Error at element "{el}" when tracing up'

    with pytest.raises(ValueError):
        s.trace_element('element', 'ThEdIrEcTiOn')


def test_to_networkx():
    elements = ['', 'a', 'b', 'ab', 'c']
    leq_func = lambda x, y: set(x) & set(y) == set(x)
    s = POSet(elements, leq_func)

    dsubs_dict = {0: set(), 1: {0}, 2: {0}, 3: {1, 2}, 4: {0}}
    dsups_dict = {0: {1, 2, 4}, 1: {3}, 2: {3}, 3: set(), 4: set()}

    def are_equal_graphs(G1, G2):
        same_adjs = (nx.to_numpy_array(G1) == nx.to_numpy_array(G2)).all()
        if not same_adjs:
            return False

        same_attrs = all([G1.nodes[n_i] == G2.nodes[n_i] for n_i in G1.nodes])
        return same_attrs

    G_down = nx.DiGraph(dsubs_dict)
    nx.set_node_attributes(G_down, dict(enumerate(elements)), 'element')
    assert are_equal_graphs(s.to_networkx('down'), G_down)
    G_up = nx.DiGraph(dsups_dict)
    nx.set_node_attributes(G_up, dict(enumerate(elements)), 'element')
    assert are_equal_graphs(s.to_networkx('up'), G_up)
    G_none = nx.Graph(dsubs_dict)
    nx.set_node_attributes(G_none, dict(enumerate(elements)), 'element')
    assert are_equal_graphs(s.to_networkx(None), G_none)

    with pytest.raises(ValueError):
        s.to_networkx('ThEdIrEcTiOn')

    LIB_INSTALLED['networkx'] = False
    with pytest.raises(ModuleNotFoundError):
        s.to_networkx('down')
    LIB_INSTALLED['networkx'] = True
