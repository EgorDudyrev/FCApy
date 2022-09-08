import pytest
from fcapy.poset import Lattice, UpperSemiLattice, LowerSemiLattice


def test_init_uppersemilattice():
    elements = []
    leq_func = lambda x, y: x in y
    with pytest.raises(ValueError):
        l = UpperSemiLattice(elements, leq_func)

    elements = ['a']
    l = UpperSemiLattice(elements, leq_func)
    assert l.elements == elements
    assert l._elements_to_index_map == {'a': 0}

    elements = ['', 'a', 'b', 'ab']
    for use_cache in [False, True]:
        l = UpperSemiLattice(elements, leq_func, use_cache=use_cache)
        assert l._elements == elements
        assert l._leq_func == leq_func
        assert l._use_cache == use_cache

    l = UpperSemiLattice(elements, leq_func)
    assert l._use_cache
    assert l._elements_to_index_map == {'': 0, 'a': 1, 'b':2, 'ab': 3}
    assert l._cache_top == 3

    with pytest.raises(ValueError):
        UpperSemiLattice(elements[:-1], leq_func)

    UpperSemiLattice(elements[1:], leq_func)


def test_top_bottom_element_uppersemilattice():
    elements = ['', 'a', 'b', 'ab']
    leq_func = lambda x, y: x in y

    l = UpperSemiLattice(elements, leq_func)
    assert l.top == 3


def test_add_uppersemilattice():
    elements = ['', 'a', 'b', 'ab']
    leq_func = lambda x, y: x in y
    l = UpperSemiLattice(elements, leq_func)
    l.add('abc')

    elements = ['', 'a', 'b', 'ab']
    l = UpperSemiLattice(elements, leq_func)
    with pytest.raises(ValueError):
        l.add('c')

    elements = ['a', 'ab']
    l = UpperSemiLattice(elements, leq_func)
    l.add('')


def test_remove_uppersemilattice():
    elements = ['', 'a', 'b', 'ab']
    leq_func = lambda x, y: x in y
    l = UpperSemiLattice(elements, leq_func)
    l.remove('a')
    l_removed = UpperSemiLattice(['', 'b', 'ab'], leq_func)
    assert l == l_removed

    l.remove('')
    l = UpperSemiLattice(elements, leq_func)
    with pytest.raises(ValueError):
        l.remove('ab')


def test_deleteitem_uppersemilattice():
    elements = ['', 'a', 'b', 'ab']
    leq_func = lambda x, y: x in y
    l = UpperSemiLattice(elements, leq_func)
    del l[1]
    l_removed = UpperSemiLattice(['', 'b', 'ab'], leq_func)
    assert l == l_removed

    del l[0]

    elements = ['', 'a', 'b', 'ab']
    l = UpperSemiLattice(elements, leq_func)
    with pytest.raises(KeyError):
        del l[3]


def test_init_lowersemilattice():
    elements = []
    leq_func = lambda x, y: x in y
    with pytest.raises(ValueError):
        l = LowerSemiLattice(elements, leq_func)

    elements = ['a']
    l = LowerSemiLattice(elements, leq_func)
    assert l.elements == elements
    assert l._elements_to_index_map == {'a': 0}

    elements = ['', 'a', 'b', 'ab']
    for use_cache in [False, True]:
        l = LowerSemiLattice(elements, leq_func, use_cache=use_cache)
        assert l._elements == elements
        assert l._leq_func == leq_func
        assert l._use_cache == use_cache

    l = LowerSemiLattice(elements, leq_func)
    assert l._use_cache
    assert l._elements_to_index_map == {'': 0, 'a': 1, 'b':2, 'ab': 3}
    assert l._cache_bottom == 0

    LowerSemiLattice(elements[:-1], leq_func)

    with pytest.raises(ValueError):
        LowerSemiLattice(elements[1:], leq_func)


def test_top_bottom_element_lowersemilattice():
    elements = ['', 'a', 'b', 'ab']
    leq_func = lambda x, y: x in y

    l = LowerSemiLattice(elements, leq_func)
    assert l.bottom == 0


def test_add_lowersemilattice():
    elements = ['', 'a', 'b', 'ab']
    leq_func = lambda x, y: x in y
    l = LowerSemiLattice(elements, leq_func)
    l.add('abc')

    elements = ['', 'a', 'b', 'ab']
    l = LowerSemiLattice(elements, leq_func)
    l.add('c')

    elements = ['a', 'ab']
    l = LowerSemiLattice(elements, leq_func)
    with pytest.raises(ValueError):
        l.add('c')


def test_remove_lowersemilattice():
    elements = ['', 'a', 'b', 'ab']
    leq_func = lambda x, y: x in y
    l = LowerSemiLattice(elements, leq_func)
    l.remove('a')
    l_removed = LowerSemiLattice(['', 'b', 'ab'], leq_func)
    assert l == l_removed

    l = LowerSemiLattice(elements, leq_func)
    with pytest.raises(ValueError):
        l.remove('')

    l.remove('ab')


def test_deleteitem_lowersemilattice():
    elements = ['', 'a', 'b', 'ab']
    leq_func = lambda x, y: x in y
    l = LowerSemiLattice(elements, leq_func)
    del l[1]
    l_removed = LowerSemiLattice(['', 'b', 'ab'], leq_func)
    assert l == l_removed

    l = LowerSemiLattice(elements, leq_func)
    with pytest.raises(KeyError):
        del l[0]

    del l[3]


def test_init_lattice():
    elements = []
    leq_func = lambda x, y: x in y
    with pytest.raises(ValueError):
        l = Lattice(elements, leq_func)

    elements = ['a']
    l = Lattice(elements, leq_func)
    assert l.elements == elements
    assert l._elements_to_index_map == {'a': 0}

    elements = ['', 'a', 'b', 'ab']
    for use_cache in [False, True]:
        l = Lattice(elements, leq_func, use_cache=use_cache)
        assert l._elements == elements
        assert l._leq_func == leq_func
        assert l._use_cache == use_cache

    l = Lattice(elements, leq_func)
    assert l._use_cache
    assert l._elements_to_index_map == {'': 0, 'a': 1, 'b':2, 'ab': 3}
    assert l._cache_top == 3
    assert l._cache_bottom == 0

    with pytest.raises(ValueError):
        Lattice(elements[:-1], leq_func)

    with pytest.raises(ValueError):
        Lattice(elements[1:], leq_func)


def test_top_bottom_element_lattice():
    elements = ['', 'a', 'b', 'ab']
    leq_func = lambda x, y: x in y

    l = Lattice(elements, leq_func)
    assert l.top == 3
    assert l.bottom == 0


def test_add_lattice():
    elements = ['', 'a', 'b', 'ab']
    leq_func = lambda x, y: x in y
    l = Lattice(elements, leq_func)
    l.add('abc')
    assert all([l.elements[l.index(el)] == el for el in l.elements])
    l_added = Lattice(elements+['abc'], leq_func)
    assert l == l_added
    assert l.top == l_added.top

    elements = ['', 'a', 'b', 'ab']
    l = Lattice(elements, leq_func)
    with pytest.raises(ValueError):
        l.add('c')

    elements = ['a', 'ab']
    l = Lattice(elements, leq_func)
    with pytest.raises(ValueError):
        l.add('c')


def test_remove_lattice():
    elements = ['', 'a', 'b', 'ab']
    leq_func = lambda x, y: x in y
    l = Lattice(elements, leq_func)
    l.remove('a')
    l_removed = Lattice(['', 'b', 'ab'], leq_func)
    assert l == l_removed
    assert all([l.elements[l.index(el)] == el for el in l.elements])


    l = Lattice(elements, leq_func)
    with pytest.raises(ValueError):
        l.remove('')
    with pytest.raises(ValueError):
        l.remove('ab')


def test_delitem_lattice():
    elements = ['', 'a', 'b', 'ab']
    leq_func = lambda x, y: x in y
    l = Lattice(elements, leq_func)
    del l[1]
    l_removed = Lattice(['', 'b', 'ab'], leq_func)
    assert l == l_removed

    l = Lattice(elements, leq_func)
    with pytest.raises(KeyError):
        del l[0]
    with pytest.raises(KeyError):
        del l[3]
