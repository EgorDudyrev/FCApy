import pytest
from fcapy.lattice.pattern_concept import PatternConcept
from fcapy.mvcontext import pattern_structure as ps
from frozendict import frozendict


def test_init():
    c = PatternConcept((0, 1), ('a', 'b'), {0: (1, 2)}, {'M1': (1, 2)}, {'M1': ps.IntervalPS}, ('M1',))
    assert c.extent_i == (0, 1)
    assert c.extent == ('a', 'b')
    assert c.intent_i == frozendict({0: (1, 2)})
    assert c.intent == frozendict({'M1': (1, 2)})
    assert c.pattern_types == {'M1': ps.IntervalPS}
    assert c.support == 2


def test_hash():
    c1 = PatternConcept((0, 1), ('a', 'b'), {0: (1, 2)}, {'M1': (1, 2)}, {'M1': ps.IntervalPS}, ('M1',))
    c2 = PatternConcept((0, 1), ('a', 'b'), {0: (1, 2)}, {'M1': (1, 2)}, {'M1': ps.IntervalPS}, ('M1',))
    assert len({c1, c2}) == 1


def test_eq_neq():
    c1 = PatternConcept((0, 1), ('a', 'b'), {0: (1, 2)}, {'M1': (1, 2)}, {'M1': ps.IntervalPS}, ('M1',))
    c2 = PatternConcept((0, 1), ('a', 'b'), {0: (1, 2)}, {'M1': (1, 2)}, {'M1': ps.IntervalPS}, ('M1',))
    c3 = PatternConcept((0,), ('a',), {0: 1}, {'M1': 1}, {'M1': ps.IntervalPS}, ('M1',))

    assert c1 == c2
    assert c1 != c3

    c4 = PatternConcept((0,), ('a',), {0: 1}, {'M1': 1}, {'M1': ps.IntervalPS}, ('M1',), context_hash=42,)
    with pytest.raises(NotImplementedError):
        c1 == c4


def test_le_leq():
    c1 = PatternConcept((0, 1), ('a', 'b'), {0: (1, 2)}, {'M1': (1, 2)}, {'M1': ps.IntervalPS}, ('M1',))
    c2 = PatternConcept((0,), ('a',), {0: 1}, {'M1': 1}, {'M1': ps.IntervalPS}, ('M1',))
    c3 = PatternConcept((0, 1), ('a', 'b'), {0: (1, 2)}, {'M1': (1, 2)}, {'M1': ps.IntervalPS}, ('M1',))
    c4 = PatternConcept((1, 2), ('b', 'c'), {0: (2, 3)}, {'M1': (2, 3)}, {'M1': ps.IntervalPS}, ('M1',))

    assert c2 < c1
    assert c2 <= c2
    assert not c1 < c2
    assert not c1 <= c2
    assert not c4 < c3
    assert not c4 <= c3

    c5 = PatternConcept((0,), ('a',), {0: 1}, {'M1': 1}, {'M1': ps.IntervalPS}, ('M1',), context_hash=42)
    with pytest.raises(NotImplementedError):
        c1 < c5
    with pytest.raises(NotImplementedError):
        c1 <= c5


def test_from_to_dict():
    c = PatternConcept((0, 1), ('a', 'b'), {0: (1, 2)}, {'M1': (1, 2)}, {'M1': ps.IntervalPS}, ('M1',))
    c_new = PatternConcept.from_dict(c.to_dict())
    assert c == c_new, "PatternConcept.to/from_dict error"


def test_from_to_json():
    c = PatternConcept((0, 1), ('a', 'b'), {0: (1, 2)}, {'M1': (1, 2)}, {'M1': ps.IntervalPS}, ('M1',))
    c_new = PatternConcept.read_json(json_data=c.write_json())
    assert c == c_new, "PatternConcept.write/read_json error"

    path = 'test.json'
    c.write_json(path)
    c_new = PatternConcept.read_json(path)
    assert c == c_new,\
        'PatternConcept.write/read_json failed. The lattice changed after 2 conversions and saving to file.'
    import os
    os.remove(path)
