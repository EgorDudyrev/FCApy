from fcapy.poset import POSet
import pytest


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
    assert s._cache


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


def test_fill_up_cache():
    elements = ['', 'a', 'b', 'ab']
    leq_func = lambda x, y: x in y
    s = POSet(elements, leq_func, use_cache=False)
    with pytest.raises(AssertionError):
        s.fill_up_cache()

    s = POSet(elements, leq_func, use_cache=True)
    s.fill_up_cache()
    cache_true = {
        0: {0: True, 1: True, 2: True, 3: True},
        1: {0: False, 1: True, 2: False, 3: True},
        2: {0: False, 1: False, 2: True, 3: True},
        3: {0: False, 1: False, 2: False, 3: True}
    }
    assert s._cache == cache_true


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
    elements = ['', 'a', 'b', 'ab']
    leq_func = lambda x, y: x in y

    # Test if intersection operation is working
    for use_cache in [False, True]:
        s1 = POSet(elements[:-1], leq_func, use_cache=use_cache)
        s2 = POSet(elements[1:], leq_func, use_cache=use_cache)
        s_and_true = POSet(elements[1:-1], leq_func, use_cache=use_cache)
        s_and_fact = s1 & s2
        assert s_and_fact == s_and_true

    # Test if cache of intersection is intersection of filled up caches
    s1 = POSet(elements[:-1], leq_func, use_cache=True)
    s1.fill_up_cache()
    s2 = POSet(elements[1:], leq_func, use_cache=True)
    s2.fill_up_cache()
    s_and_true = POSet(elements[1:-1], leq_func)
    s_and_true.fill_up_cache()

    s_and_fact = s1 & s2
    assert s_and_fact == s_and_true
    assert s_and_fact._cache == s_and_true._cache

    # Test if cache of intersection is union of caches
    s1 = POSet(elements, leq_func, use_cache=True)
    s1.leq_elements(0, 1)
    s2 = POSet(elements[:-1], leq_func, use_cache=True)
    s2.leq_elements(1, 2)
    s_and_true = POSet(elements[:-1], leq_func)
    s_and_true.leq_elements(0,1)
    s_and_true.leq_elements(1,2)

    s_and_fact = s1 & s2
    assert s_and_fact == s_and_true
    assert s_and_fact._cache == s_and_true._cache


def test_or():
    elements = ['', 'a', 'b', 'ab']
    leq_func = lambda x, y: x in y

    # Test if union operation is working
    for use_cache in [False, True]:
        s1 = POSet(elements[:-1], leq_func, use_cache=use_cache)
        s2 = POSet(elements[1:], leq_func, use_cache=use_cache)
        s_or_true = POSet(elements, leq_func, use_cache=use_cache)
        s_or_fact = s1 | s2
        assert s_or_fact == s_or_true

    # Test if cache of union is union of filled up caches
    s1 = POSet(elements[:-1], leq_func, use_cache=True)
    s1.fill_up_cache()
    s2 = POSet(elements[1:], leq_func, use_cache=True)
    s2.fill_up_cache()
    s_or_true = POSet(elements, leq_func, use_cache=True)
    s_or_true.fill_up_cache()

    s_or_fact = s1 | s2
    assert s_or_fact == s_or_true
    assert s_or_fact._cache == s_or_true._cache


def test_xor():
    elements = ['', 'a', 'b', 'ab']
    elements_xor = ['', 'ab']
    leq_func = lambda x, y: x in y

    # Test if xor operation is working
    for use_cache in [False, True]:
        s1 = POSet(elements[:-1], leq_func, use_cache=use_cache)
        s2 = POSet(elements[1:], leq_func, use_cache=use_cache)
        s_xor_true = POSet(elements_xor, leq_func, use_cache=use_cache)
        s_xor_fact = s1 ^ s2
        assert s_xor_fact == s_xor_true

    # Test if cache of xor is xor of filled up caches
    s1 = POSet(elements[:-1], leq_func, use_cache=True)
    s1.fill_up_cache()
    s2 = POSet(elements[1:], leq_func, use_cache=True)
    s2.fill_up_cache()
    s_xor_true = POSet(elements_xor, leq_func, use_cache=True)
    s_xor_true.fill_up_cache()

    s_xor_fact = s1 ^ s2
    assert s_xor_fact == s_xor_true
    assert s_xor_fact._cache == s_xor_true._cache


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
    s = POSet(elements, leq_func)
    del s[del_i]
    assert s.elements == elements_del

    #TODO: Add test of caches


def test_add():
    elements = ['', 'a', 'b', 'ab']
    leq_func = lambda x, y: x in y
    s = POSet(elements[:-1], leq_func)
    s.add(elements[-1])
    assert s.elements == elements

    #TODO: Add test of caches


def test_remove():
    elements = ['', 'a', 'b', 'ab']
    leq_func = lambda x, y: x in y
    s = POSet(elements, leq_func)
    s.remove(elements[-1])
    assert s.elements == elements[:-1]

    #TODO: Add test of caches


def test_super_elements():
    elements = ['', 'a', 'b', 'ab']
    leq_func = lambda x, y: x in y
    s = POSet(elements, leq_func)
    sups = s.super_elements(3)
    assert sups == []

    sups = s.super_elements(2)
    assert sups == [3]

    sups = s.super_elements(0)
    assert sups == [1, 2, 3]


def test_sub_elements():
    elements = ['', 'a', 'b', 'ab']
    leq_func = lambda x, y: x in y
    s = POSet(elements, leq_func)
    subs = s.sub_elements(0)
    assert subs == []

    subs = s.sub_elements(2)
    assert subs == [0]

    subs = s.sub_elements(3)
    assert subs == [0, 1, 2]
