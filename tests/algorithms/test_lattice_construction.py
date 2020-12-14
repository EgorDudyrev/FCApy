import pytest
from fcapy.lattice.formal_concept import FormalConcept
from fcapy.algorithms import lattice_construction as lca


def test_complete_comparison():
    c1 = FormalConcept((), (), (0, 1), ('a', 'b'))
    c2 = FormalConcept((0,), ('a',), (0,), ('a',))
    c3 = FormalConcept((1,), ('b',), (1,), ('b',))
    c4 = FormalConcept((0, 1), ('a', 'b'), (), ())
    subconcepts_dict = lca.complete_comparison([c1, c2, c3, c4])
    subconcepts_dict_true = {0: [], 1: [0], 2: [0], 3: [1, 2]}
    assert subconcepts_dict == subconcepts_dict_true,\
        'lattice_construction.complete_comparison failed. Wrong subconcepts_dict is constructed'
