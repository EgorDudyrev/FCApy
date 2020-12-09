import pytest
from fcapy.concept.formal_concept import FormalConcept


def test_formal_concept_init():
    c = FormalConcept([1, 2], ['a', 'b'], [4, 5], ['d', 'e'])

    with pytest.raises(AssertionError):
        c = FormalConcept([1, 2], [1, 2], [4, 5], ["d", "e"])
    with pytest.raises(AssertionError):
        c = FormalConcept([1, 2], ["a", "b"], [4, 5], [4, 5])


def test_formal_concept_extent_intent():
    c = FormalConcept([1, 2], ['a', 'b'], [4, 5], ["d", "e"])
    assert tuple(c.extent) == ('a', 'b'), "FormalConcept.extent failed. Extent values differ from the given ones"
    assert tuple(c.intent) == ('d', 'e'), "FormalConcept.intent failed. Intent values differ from the given ones"

    with pytest.raises(AttributeError):
        c.extent = 42
    with pytest.raises(AttributeError):
        c.intent = 42


def test__eq__ne__():
    c1 = FormalConcept([1, 2], ['a', 'b'], [4, 5], ['d', 'e'])
    c2 = FormalConcept([1, 2], ['a', 'b'], [4, 5], ['d', 'e'])
    c3 = FormalConcept([1, 3], ['a', 'c'], [5, 6], ['e', 'f'])

    assert c1 == c2, "FormalConcept.__eq__ failed. Two same concepts are classified as different"
    assert not c1 != c2, "FormalConcept.__neq__ failed. Two same concepts are classified as different"

    assert c1 != c3, "FormalConcept.__eq__ failed. Two different concepts are classified as the same"


def test__hash__():
    c1 = FormalConcept([1, 2], ['a', 'b'], [4, 5], ['d', 'e'])
    c2 = FormalConcept([1, 2], ['a', 'b'], [4, 5], ['d', 'e'])
    assert len({c1, c2}) == 1, "FormalConcept.__hash__ failed. Two same concepts put twice in set"
