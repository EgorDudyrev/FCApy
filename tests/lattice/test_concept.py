import pytest
from fcapy.lattice.concept import FormalConcept


def test_formal_concept_init():
    c = FormalConcept(['a', 'b'], ['d', 'e'])

    with pytest.raises(AssertionError):
        c = FormalConcept([1, 2], ["d", "e"])
    with pytest.raises(AssertionError):
        c = FormalConcept(["a", "b"], [3, 4])


def test_formal_concept_extent_intent():
    c = FormalConcept(['a', 'b'], ["d", "e"])
    assert tuple(c.extent) == ('a', 'b'), "FormalConcept.extent failed. Extent values differ from the given ones"
    assert tuple(c.intent) == ('d', 'e'), "FormalConcept.intent failed. Intent values differ from the given ones"

    with pytest.raises(AttributeError):
        c.extent = 42
    with pytest.raises(AttributeError):
        c.intent = 42
