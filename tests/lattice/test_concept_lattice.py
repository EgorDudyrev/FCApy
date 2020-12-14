import pytest
from fcapy.context import converters, FormalContext
from fcapy.lattice.concept_lattice import ConceptLattice
from fcapy.lattice.formal_concept import FormalConcept


def test_concept_lattice_init():
    c1 = FormalConcept((), (), (0, 1), ('a', 'b'))
    c2 = FormalConcept((0,), ('a',), (0,), ('a',))
    c3 = FormalConcept((0, 1), ('a', 'b'), (), ())
    c4 = FormalConcept((1,), ('b',), (1,), ('b',))
    concepts = [c1, c2, c3, c4]
    ltc = ConceptLattice(concepts)

    superconcepts_dict = {0: [1, 3], 1: [2], 2: [], 3: [2]}
    subconcepts_dict = {0: [], 1: [0], 2: [1, 3], 3: [0]}
    ltc = ConceptLattice(concepts, superconcepts_dict=superconcepts_dict)
    assert ltc.subconcepts_dict == subconcepts_dict,\
        'ConceptLattice.__init__ failed. The calculation of subconcepts based on superconcepts is wrong'

    ltc = ConceptLattice(concepts, subconcepts_dict=subconcepts_dict)
    assert ltc.superconcepts_dict == superconcepts_dict,\
        'ConceptLattice.__init__ failed. The calculation of superconcepts based on subconcepts is wrong'

    assert ltc.concepts == concepts,\
        'ConceptLattice.__init__ failed. Something is wrong with accessing the concepts property'

    assert ltc.top_concept_i == 2, 'ConceptLattice.__init__ failed. The top concept index is wrongly assigned'
    assert ltc.bottom_concept_i == 0, 'ConceptLattice.__init__ failed. The bottom concept index is wrongly assigned'
    assert ltc.top_concept == c3, 'ConceptLattice.__init__ failed. The top concept is wrongly assigned'
    assert ltc.bottom_concept == c1, 'ConceptLattice.__init__ failed. The bottom concept is wrongly assigned'


def test_from_context():
    ctx = FormalContext([[True, False], [False, True]], ['a', 'b'], ['a', 'b'])
    ltc = ConceptLattice.from_context(ctx)

    c1 = FormalConcept((), (), (0, 1), ('a', 'b'))
    c2 = FormalConcept((0,), ('a',), (0,), ('a',))
    c3 = FormalConcept((0, 1), ('a', 'b'), (), ())
    c4 = FormalConcept((1,), ('b',), (1,), ('b',))
    concepts = [c1, c2, c3, c4]

    assert ltc.concepts == concepts, 'ConceptLattice.from_context failed. Wrong concepts in the constructed lattice'


def test_get_top_bottom_concepts_i():
    ltc = ConceptLattice()
    top_concept_i, bottom_concept_i = ltc.get_top_bottom_concepts_i(None)
    assert top_concept_i is None and bottom_concept_i is None,\
        'ConceptLattice.get_top_bottom_concepts_i failed. None values should be returned if None value is given'

    c1 = FormalConcept((0,), ('a',), (0,), ('a',))
    c2 = FormalConcept((), (), (0, 1), ('a', 'b'))
    c3 = FormalConcept((0, 1), ('a', 'b'), (), ())
    c4 = FormalConcept((1,), ('b',), (1,), ('b',))
    concepts = [c1, c2, c3, c4]
    top_concept_i, bottom_concept_i = ltc.get_top_bottom_concepts_i(concepts)
    assert top_concept_i == 2,\
        "ConceptLattice.get_top_bottom_concepts_i failed. Top concept index is wrongly assigned"
    assert bottom_concept_i == 1, \
        "ConceptLattice.get_top_bottom_concepts_i failed. Bottom concept index is wrongly assigned"


def test_to_from_json():
    ctx = FormalContext([[True, False], [False, True]], ['a', 'b'], ['a', 'b'])
    ltc = ConceptLattice.from_context(ctx)
    assert ltc == ltc.from_json(json_data=ltc.to_json()),\
        'ConceptLattice.to/from_json failed. The lattice changed after 2 conversions.'

    path = 'test.json'
    ltc.to_json(path)
    ltc_new = ltc.from_json(path)
    assert ltc == ltc_new,\
        'ConceptLattice.to/from_json failed. The lattice changed after 2 conversions and saving to file.'
    import os
    os.remove(path)


def test__eq__():
    c1 = FormalConcept((), (), (0, 1), ('a', 'b'))
    c2 = FormalConcept((0,), ('a',), (0,), ('a',))
    c3 = FormalConcept((1,), ('b',), (1,), ('b',))
    c4 = FormalConcept((0, 1), ('a', 'b'), (), ())

    ltc1 = ConceptLattice([c1, c2, c4])
    ltc2 = ConceptLattice([c1, c3, c4])

    assert ltc1 == ltc1, "ConceptLattice.__eq__ failed. The lattice does not equal to itself"
    assert not ltc1 == ltc2, "ConceptLattice.__eq__ failed. Two different lattices are classified as the same"
    assert ltc1 != ltc2, "ConceptLattice.__ne__ failed. Two different lattices are not classified as different"
