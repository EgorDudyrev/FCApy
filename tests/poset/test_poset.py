from fcapy.poset import POSet
import pytest
from copy import deepcopy


def test_init():
    s = POSet()

    elements = ['', 'a', 'b', 'ab']
    leq_func = lambda x,y: x in y

    for use_cache in [False, True]:
        s = POSet(elements, leq_func, use_cache=use_cache)
        assert s._elements == elements
        assert s._leq_func == leq_func
        assert s._use_cache == use_cache

    s = POSet(elements, leq_func)
    assert s._use_cache
    assert s._cache_leq == {}
    assert s._cache_subelements == {}
    assert s._cache_superelements == {}
    assert s._cache_direct_subelements == {}
    assert s._cache_direct_superelements == {}


def test_leq_elements():
    elements = ['', 'a', 'b', 'ab']
    leq_func = lambda x, y: x in y
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
    leq_func = lambda x, y: x in y
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

    s.fill_up_subelements_cache()
    subelements_cache_true = {0: set(), 1: {0}, 2: {0}, 3: {0, 1, 2}}
    assert s._cache_subelements == subelements_cache_true

    s.fill_up_superelements_cache()
    superelements_cache_true = {0: {1, 2, 3}, 1: {3}, 2: {3}, 3: set()}
    assert s._cache_superelements == superelements_cache_true

    s.fill_up_direct_subelements_cache()
    dsubelements_cache_true = {0: set(), 1: {0}, 2: {0}, 3: {1, 2}}
    assert s._cache_direct_subelements == dsubelements_cache_true

    s.fill_up_direct_superelements_cache()
    dsupelements_cache_true = {0: {1, 2}, 1: {3}, 2: {3}, 3: set()}
    assert s._cache_direct_superelements == dsupelements_cache_true


def test_join_elements_supremum():
    elements = ['a', 'b', 'ab', 'c']
    leq_func = lambda x, y: x in y
    s = POSet(elements, leq_func)

    for func in [s.join_elements, s.supremum]:
        join = func([0, 1])
        assert join == 2

        join = func([0, 2])
        assert join == 2

        assert func() is None

        join = func([1, 3])
        assert join is None


def test_meet_elements_infimum():
    elements = ['a', 'b', 'ab', 'ac']
    leq_func = lambda x, y: x in y
    s = POSet(elements, leq_func)

    for func in [s.meet_elements, s.infimum]:
        meet = func([2, 3])
        assert meet == 0

        meet = func([0, 2])
        assert meet == 0

        assert func() is None

        meet = func([1, 3])
        assert meet is None


def test_getitem():
    elements = ['', 'a', 'b', 'ab']
    leq_func = lambda x, y: x in y
    s = POSet(elements, leq_func)
    assert s[0] == ''
    assert s[1] == 'a'
    assert s[2] == 'b'
    assert s[3] == 'ab'

    assert s[:2] == elements[:2]
    assert s[[1,2,3]] == elements[1:]


def test_eq():
    elements = ['', 'a', 'b', 'ab']
    leq_func = lambda x, y: x in y
    s = POSet(elements, leq_func)
    other = POSet(elements, leq_func)
    assert s == other

    other = POSet(elements[:-1], leq_func)
    assert s != other

    elements_1 = ['', 'a', 'b', 'abc']
    other = POSet(elements_1, leq_func)
    assert s != other

    leq_func_1 = lambda x, y: not x  in y
    other = POSet(elements, leq_func_1)
    assert s != other

    other = POSet(elements_1, leq_func_1)
    assert s != other


def test_and():
    elements_1 = ['', 'a', 'b']
    elements_2 = ['a', 'b', 'ab']
    elements_and = ['a', 'b']
    leq_func = lambda x, y: x in y

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
    assert s_and_fact._cache_subelements == s_and_true._cache_subelements
    assert s_and_fact._cache_superelements == s_and_true._cache_superelements
    assert s_and_fact._cache_direct_subelements == s_and_true._cache_direct_subelements
    assert s_and_fact._cache_direct_superelements == s_and_true._cache_direct_superelements

    # Test if cache of intersection is union of caches
    s1 = POSet(elements_1, leq_func, use_cache=True)
    s1.leq_elements(0, 1)
    s2 = POSet(elements_1, leq_func, use_cache=True)
    s2.leq_elements(1, 2)
    s_and_true = POSet(elements_1, leq_func)
    s_and_true.leq_elements(0,1)
    s_and_true.leq_elements(1,2)

    s_and_fact = s1 & s2
    assert s_and_fact == s_and_true
    assert s_and_fact._cache_leq == s_and_true._cache_leq
    assert s_and_fact._cache_subelements == s_and_true._cache_subelements
    assert s_and_fact._cache_superelements == s_and_true._cache_superelements
    assert s_and_fact._cache_direct_subelements == s_and_true._cache_direct_subelements
    assert s_and_fact._cache_direct_superelements == s_and_true._cache_direct_superelements


def test_or():
    elements_1 = ['', 'a', 'b']
    elements_2 = ['a', 'b', 'ab']
    elements_or = ['', 'a', 'b', 'ab']
    leq_func = lambda x, y: x in y

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
    del s_or_true._cache_subelements[0], s_or_true._cache_subelements[3]
    del s_or_true._cache_superelements[0], s_or_true._cache_superelements[3]
    del s_or_true._cache_direct_subelements[0], s_or_true._cache_direct_subelements[3]
    del s_or_true._cache_direct_superelements[0], s_or_true._cache_direct_superelements[3]

    s_or_fact = s1 | s2
    assert s_or_fact == s_or_true
    assert s_or_fact._cache_leq == s_or_true._cache_leq
    assert s_or_fact._cache_subelements == s_or_true._cache_subelements
    assert s_or_fact._cache_superelements == s_or_true._cache_superelements
    assert s_or_fact._cache_direct_subelements == s_or_true._cache_direct_subelements
    assert s_or_fact._cache_direct_superelements == s_or_true._cache_direct_superelements


def test_xor():
    elements_1 = ['', 'a', 'b']
    elements_2 = ['a', 'b', 'ab']
    elements_xor = ['', 'ab']
    leq_func = lambda x, y: x in y

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
    s_xor_true._cache_subelements = {}
    s_xor_true._cache_superelements = {}
    s_xor_true._cache_direct_subelements = {}
    s_xor_true._cache_direct_superelements = {}

    s_xor_fact = s1 ^ s2
    assert s_xor_fact == s_xor_true
    assert s_xor_fact._cache_leq == s_xor_true._cache_leq
    assert s_xor_fact._cache_subelements == s_xor_true._cache_subelements
    assert s_xor_fact._cache_superelements == s_xor_true._cache_superelements
    assert s_xor_fact._cache_direct_subelements == s_xor_fact._cache_direct_subelements
    assert s_xor_fact._cache_direct_superelements == s_xor_fact._cache_direct_superelements


def test_subtraction():
    elements_1 = ['', 'a', 'b']
    elements_2 = ['', 'ab']
    elements_sub = ['a', 'b']
    leq_func = lambda x, y: x in y

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
    assert s_sub_fact._cache_subelements == s_sub_true._cache_subelements
    assert s_sub_fact._cache_superelements == s_sub_true._cache_superelements
    assert s_sub_fact._cache_direct_subelements == s_sub_true._cache_direct_subelements
    assert s_sub_fact._cache_direct_superelements == s_sub_true._cache_direct_superelements


def test_len():
    elements = ['', 'a', 'b', 'ab']
    leq_func = lambda x, y: x in y
    s = POSet(elements, leq_func)
    assert len(s) == len(elements)


def test_delitem():
    elements = ['', 'a', 'b', 'ab']
    del_i = 1
    elements_del = [el for i, el in enumerate(elements) if i != del_i]
    leq_func = lambda x, y: x in y

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
    assert s._cache_subelements == s_del_true._cache_subelements
    assert s._cache_superelements == s_del_true._cache_superelements
    assert s._cache_direct_subelements == s_del_true._cache_direct_subelements
    assert s._cache_direct_superelements == s_del_true._cache_direct_superelements


def test_add():
    elements = ['', 'b', 'ab']
    elements_add = ['', 'b', 'ab', 'a']
    new_element = 'a'
    leq_func = lambda x, y: x in y

    # Test if add operation is working
    for use_cache in [False, True]:
        s = POSet(elements, leq_func, use_cache=use_cache)
        s.add(new_element)
        s_add_true = POSet(elements_add, leq_func, use_cache=use_cache)
        assert s == s_add_true

    # Test if cache is not changed after adding new element
    s = POSet(elements, leq_func, use_cache=True)
    s_add_true = POSet(elements_add, leq_func, use_cache=True)
    s.fill_up_caches()
    s_add_true.fill_up_caches()

    cache_true = deepcopy(s._cache_leq)
    #cache_true[len(elements)-1] = {}

    s.add(new_element)
    assert s._cache_leq == cache_true
    s.fill_up_caches()
    assert s == s_add_true
    assert s._cache_leq == s_add_true._cache_leq
    assert s._cache_subelements == s_add_true._cache_subelements
    assert s._cache_superelements == s_add_true._cache_superelements
    assert s._cache_direct_subelements == s_add_true._cache_direct_subelements
    assert s._cache_direct_superelements == s_add_true._cache_direct_superelements


def test_remove():
    elements = ['', 'a', 'b', 'ab']
    remove_i = 1
    elements_remove = [el for i, el in enumerate(elements) if i != remove_i]
    leq_func = lambda x, y: x in y

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
    assert s._cache_subelements == s_remove_true._cache_subelements
    assert s._cache_superelements == s_remove_true._cache_superelements
    assert s._cache_direct_subelements == s_remove_true._cache_direct_subelements
    assert s._cache_direct_superelements == s_remove_true._cache_direct_superelements


def test_super_elements():
    elements = ['', 'a', 'b', 'ab']
    leq_func = lambda x, y: x in y
    s = POSet(elements, leq_func)
    sups_true = {0: {1, 2, 3}, 1: {3}, 2: {3}, 3: set()}

    sups_fact = {idx: s.super_elements(idx) for idx in range(len(elements))}
    assert sups_fact == sups_true


def test_sub_elements():
    elements = ['', 'a', 'b', 'ab']
    leq_func = lambda x, y: x in y
    s = POSet(elements, leq_func)
    subs_true = {0: set(), 1: {0}, 2: {0}, 3: {0, 1, 2}}

    subs_fact = {idx: s.sub_elements(idx) for idx in range(len(elements))}
    assert subs_fact == subs_true


def test_direct_super_elements():
    elements = ['', 'a', 'b', 'ab']
    leq_func = lambda x, y: x in y
    s = POSet(elements, leq_func)
    dsups_true = {0: {1, 2}, 1: {3}, 2: {3}, 3: set()}

    dsups_fact = {idx: s.direct_super_elements(idx) for idx in range(len(elements))}
    assert dsups_fact == dsups_true


def test_direct_sub_elements():
    elements = ['', 'a', 'b', 'ab']
    leq_func = lambda x, y: x in y
    s = POSet(elements, leq_func)
    dsubs_true = {0: set(), 1: {0}, 2: {0}, 3: {1, 2}}

    dsubs_fact = {idx: s.direct_sub_elements(idx) for idx in range(len(elements))}
    assert dsubs_fact == dsubs_true
