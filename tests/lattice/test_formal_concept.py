import pytest
from fcapy.lattice.formal_concept import FormalConcept, UnmatchedMonotonicityError, UnmatchedContextError


def test_formal_concept_init():
    c = FormalConcept([1, 2], ['a', 'b'], [4, 5], ['d', 'e'])

    #with pytest.raises(AssertionError):
    c = FormalConcept([1, 2], [1, 2], [4, 5], ["d", "e"])
    assert c.extent == ('1', '2')
    assert c.intent == ('d', 'e')

    c = FormalConcept([1, 2], ["a", "b"], [4, 5], [4, 5])
    assert c.extent == ('a', 'b')
    assert c.intent == ('4', '5')


def test_formal_concept_extent_intent():
    c = FormalConcept([1, 2], ['a', 'b'], [4, 5], ["d", "e"])
    assert tuple(c.extent_i) == (1, 2), "FormalConcept.extent_i failed. Extent indices differ from the given ones"
    assert tuple(c.extent) == ('a', 'b'), "FormalConcept.extent failed. Extent values differ from the given ones"
    assert tuple(c.intent_i) == (4, 5), "FormalConcept.intent_i failed. Intent indices differ from the given ones"
    assert tuple(c.intent) == ('d', 'e'), "FormalConcept.intent failed. Intent values differ from the given ones"

    with pytest.raises(AttributeError):
        c.extent = 42
    with pytest.raises(AttributeError):
        c.intent = 42
    with pytest.raises(AttributeError):
        c.extent_i = 42
    with pytest.raises(AttributeError):
        c.intent_i = 42


def test__eq__ne__():
    c1 = FormalConcept([1, 2], ['a', 'b'], [4, 5], ['d', 'e'])
    c2 = FormalConcept([1, 2], ['a', 'b'], [4, 5], ['d', 'e'])
    c3 = FormalConcept([1, 3], ['a', 'c'], [5, 6], ['e', 'f'])

    assert c1 == c2, "FormalConcept.__eq__ failed. Two same concepts are classified as different"
    assert not c1 != c2, "FormalConcept.__neq__ failed. Two same concepts are classified as different"

    assert c1 != c3, "FormalConcept.__eq__ failed. Two different concepts are classified as the same"

    c4 = FormalConcept([1, 3, 4], ['a', 'c', 'd'], [4, 5, 6], ['d', 'e', 'f'])
    assert not c1 == c4, "FormalConcept.__eq__ failed. Two concept with different support are classified as the same"

    c5 = FormalConcept([2, 3], ['b', 'c'], [5], ['e'], context_hash=42)
    with pytest.raises(UnmatchedContextError):
        c1 == c5
    with pytest.raises(UnmatchedContextError):
        c1 != c5

    c6 = FormalConcept([], [], [], [], is_monotone=True)
    with pytest.raises(UnmatchedMonotonicityError):
        c1 == c6
    with pytest.raises(UnmatchedMonotonicityError):
        c1 != c6


def test__le__lt__():
    c1 = FormalConcept([1, 2, 3], ['a', 'b', 'c'], [4], ['d'])
    c2 = FormalConcept([1, 2], ['a', 'b'], [4, 5], ['d', 'e'])
    c3 = FormalConcept([1], ['a'], [4, 5, 6], ['d', 'e', 'f'])

    c4 = FormalConcept([2, 3], ['b', 'c'], [5], ['e'])

    assert c1 <= c1, "FormalConcept.__le__ failed. The same concept is classified as not <="
    assert c2 <= c1, "FormalConcept.__le__ failed. The bigger concept is classified as smaller"
    assert not c1 <= c2, "FormalConcept.__le__ failed. The bigger concept is classified as smaller"

    assert not c1 < c1, "FormalConcept.__lt__ failed. The same concept is classified as not <"
    assert c2 < c1, "FormalConcept.__lt__ failed. The bigger concept is classified as smaller"
    assert not c1 < c2, "FormalConcept.__lt__ failed. The bigger concept is classified as smaller"

    c5 = FormalConcept([2, 3], ['b', 'c'], [5], ['e'], context_hash=42)
    with pytest.raises(UnmatchedContextError):
        c1 < c5
    with pytest.raises(UnmatchedContextError):
        c1 <= c5

    c6 = FormalConcept([], [], [], [], is_monotone=True)
    with pytest.raises(UnmatchedMonotonicityError):
        c1 < c6
    with pytest.raises(UnmatchedMonotonicityError):
        c1 <= c6


def test__hash__():
    c1 = FormalConcept([1, 2], ['a', 'b'], [4, 5], ['d', 'e'])
    c2 = FormalConcept([1, 2], ['a', 'b'], [4, 5], ['d', 'e'])
    assert len({c1, c2}) == 1, "FormalConcept.__hash__ failed. Two same concepts put twice in set"


def test_dict_converter():
    G, M = ['a', 'b'], ['d', 'e']
    c1 = FormalConcept([1, 2], ['a', 'b'], [4, 5], ['d', 'e'])
    c2 = FormalConcept.from_dict(c1.to_dict(G, M))
    assert c1 == c2, "FormalConcept.to_dict/from_dict failed. The concept is modified after to/from operations"

    dct = {'Ext': {'Inds': []}, "Int": "BOTTOM", "Supp": 0}
    c = FormalConcept([], [], [], [])
    assert FormalConcept.from_dict(dct) == c, "FormalConcept.from_dict. Can not load bottom concept"

    c1.measures['LStab'] = 0.5
    c1_dict = c1.to_dict(G, M)
    assert FormalConcept.from_dict(c1_dict).to_dict(G, M) == c1_dict,\
        "FormalConcept.to/from_dict failed. Dict does not contain concept measures"


def test_json_converter():
    G, M = ['a', 'b'], ['d', 'e']
    c1 = FormalConcept([1, 2], ['a', 'b'], [4, 5], ['d', 'e'])
    c2 = FormalConcept.read_json(json_data=c1.write_json(G, M))
    assert c1 == c2, "FormalConcept.write_json/read_json failed. The concept is modified after to/from operations"

    c1.write_json(G, M, 'concept_tmp.json')
    c2 = FormalConcept.read_json('concept_tmp.json')
    assert c1 == c2, "FormalConcept.write_json/read_json failed. The concept is modified after to/from file operations"
    import os
    os.remove('concept_tmp.json')
