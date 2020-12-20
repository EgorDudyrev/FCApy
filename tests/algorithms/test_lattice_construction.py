import pytest
from fcapy.lattice.formal_concept import FormalConcept
from fcapy.algorithms import lattice_construction as lca
from fcapy.lattice import ConceptLattice
from fcapy.context import read_cxt


def test_complete_comparison():
    c1 = FormalConcept((), (), (0, 1), ('a', 'b'))
    c2 = FormalConcept((0,), ('a',), (0,), ('a',))
    c3 = FormalConcept((1,), ('b',), (1,), ('b',))
    c4 = FormalConcept((0, 1), ('a', 'b'), (), ())
    subconcepts_dict = lca.complete_comparison([c1, c2, c3, c4])
    subconcepts_dict_true = {0: [], 1: [0], 2: [0], 3: [1, 2]}
    assert subconcepts_dict == subconcepts_dict_true,\
        'lattice_construction.complete_comparison failed. Wrong subconcepts_dict is constructed'


def test_spanning_tree():
    ctx = read_cxt('data/animal_movement.cxt')
    ltc = ConceptLattice.from_context(ctx)
    sub_st, sup_st = lca.construct_spanning_tree(ltc.concepts)

    sub_st_true = {0: [1, 2, 3], 1: [4, 5], 2: [], 3: [6], 4: [7], 5: [], 6: [], 7: []}
    sup_st_true = {0: [], 1: [0], 2: [0], 3: [0], 4: [1], 5: [1], 6: [3], 7: [4]}
    assert sub_st == sub_st_true,\
        'lattice_construction.construct_spanning_tree failed. The set of subconcepts differs from the expected'
    assert sup_st == sup_st_true, \
        'lattice_construction.construct_spanning_tree failed. The set of superconcepts differs from the expected'
