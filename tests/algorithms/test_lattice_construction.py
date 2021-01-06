import pytest
from fcapy.lattice.formal_concept import FormalConcept
from fcapy.algorithms import lattice_construction as lca
from fcapy.lattice import ConceptLattice
from fcapy.context import read_cxt
import numpy as np


def test_complete_comparison():
    c1 = FormalConcept((), (), (0, 1), ('a', 'b'))
    c2 = FormalConcept((0,), ('a',), (0,), ('a',))
    c3 = FormalConcept((1,), ('b',), (1,), ('b',))
    c4 = FormalConcept((0, 1), ('a', 'b'), (), ())
    subconcepts_dict = lca.complete_comparison([c1, c2, c3, c4])
    subconcepts_dict_true = {0: set(), 1: {0}, 2: {0}, 3: {1, 2}}
    assert subconcepts_dict == subconcepts_dict_true,\
        'lattice_construction.complete_comparison failed. Wrong subconcepts_dict is constructed'

    concepts_sorted = [c4, c2, c3, c1]
    subconcepts_dict_sorted = lca.complete_comparison(concepts_sorted, is_concepts_sorted=True)
    subconcepts_dict_unsorted = lca.complete_comparison(concepts_sorted, is_concepts_sorted=False)
    assert subconcepts_dict_sorted == subconcepts_dict_unsorted,\
        'lattice_construction.complete_comparison failed. Output changes with is_concepts_sorted parameter'

    subconcepts_dict = lca.complete_comparison([c1, c2, c3, c4])
    subconcepts_dict_parallel = lca.complete_comparison([c1, c2, c3, c4], n_jobs=-1)
    assert subconcepts_dict == subconcepts_dict_parallel,\
        "Complete_comparison failed. Parallel constructed subconcepts differ from non parallel ones"


def test_spanning_tree():
    ctx = read_cxt('data/animal_movement.cxt')
    ltc = ConceptLattice.from_context(ctx)
    concepts = ltc.concepts
    np.random.seed(42)
    np.random.shuffle(concepts)
    sub_st, sup_st = lca.construct_spanning_tree(concepts)
    sub_true = lca.complete_comparison(concepts)
    sup_true = ConceptLattice.transpose_hierarchy(sub_true)

    for c_i in sup_true.keys():
        assert set(sup_st[c_i]) & set(sup_true[c_i]) == set(sup_st[c_i]),\
            'lattice_construction.construct_spanning_tree failed'

    concepts_sorted = ConceptLattice.sort_concepts(concepts)
    sub_st_sort, sup_st_sort = lca.construct_spanning_tree(concepts_sorted, is_concepts_sorted=True)
    sub_st_unsort, sup_st_unsort = lca.construct_spanning_tree(concepts_sorted, is_concepts_sorted=False)
    assert sub_st_sort == sub_st_unsort,\
        'lattice_construction.construct_spanning_tree failed.' \
        'Spanning tree subconcepts dict changes with is_concepts_sorted parameter'
    assert sup_st_sort == sup_st_unsort, \
        'lattice_construction.construct_spanning_tree failed.' \
        'Spanning tree superconcepts dict changes with is_concepts_sorted parameter'


def test_lattice_construction_from_spanning_tree_parallel():
    ctx = read_cxt('data/animal_movement.cxt')
    ltc = ConceptLattice.from_context(ctx)
    concepts = ltc.concepts
    np.random.seed(42)
    np.random.shuffle(concepts)
    sub_true = lca.complete_comparison(concepts)
    sub_st, sup_st = lca.construct_spanning_tree(concepts)
    chains = ConceptLattice._get_chains(concepts, sup_st)
    sub_from_sptree = lca.construct_lattice_from_spanning_tree_parallel(concepts, chains)
    assert sub_true == sub_from_sptree, \
        'lattice_construction.construct_lattice_fromm_spanning_tree_parallel failed. ' + \
        'The result is different then the one of complete comparison'

    concepts_sorted = ltc.sort_concepts(concepts)
    sup_st_sorted = lca.construct_spanning_tree(concepts_sorted, is_concepts_sorted=True)[1]
    chains_sorted = ConceptLattice._get_chains(concepts_sorted, sup_st_sorted, is_concepts_sorted=True)
    sub_with_sptree_sort = lca.construct_lattice_from_spanning_tree_parallel(
        concepts_sorted, chains_sorted, is_concepts_sorted=True)
    sub_with_sptree_unsort = lca.construct_lattice_from_spanning_tree_parallel(
        concepts_sorted, chains_sorted, is_concepts_sorted=False)
    assert sub_with_sptree_sort == sub_with_sptree_unsort, \
        'lattice_construction.construct_lattice_fromm_spanning_tree_parallel failed.' \
        'The result changes with is_concepts_sorted parameter'

    sub_parallel_sort = lca.construct_lattice_from_spanning_tree_parallel(
        concepts_sorted, chains_sorted, is_concepts_sorted=True, n_jobs=-1)
    sub_parallel_unsort = lca.construct_lattice_from_spanning_tree_parallel(
        concepts_sorted, chains_sorted, is_concepts_sorted=False, n_jobs=-1)
    assert sub_with_sptree_sort == sub_parallel_sort, \
        'lattice_construction.construct_lattice_fromm_spanning_tree_parallel failed.' \
        'Parallel computing give wrong result when concepts are sorted'
    assert sub_with_sptree_unsort == sub_parallel_unsort, \
        'lattice_construction.construct_lattice_fromm_spanning_tree_parallel failed.' \
        'Parallel computing give wrong result when concepts are not sorted'


def test_lattice_construction_by_spanning_tree():
    ctx = read_cxt('data/animal_movement.cxt')
    ltc = ConceptLattice.from_context(ctx)
    concepts = ltc.concepts
    np.random.seed(42)
    np.random.shuffle(concepts)
    sub_true = lca.complete_comparison(concepts)
    sub_with_sptree = lca.construct_lattice_by_spanning_tree(concepts)
    assert sub_true == sub_with_sptree,\
        'lattice_construction.construct_lattice_by_spanning_tree failed. ' +\
        'The result is different then the one of complete comparison'

    concepts_sorted = ltc.sort_concepts(concepts)
    sub_with_sptree_sort = lca.construct_lattice_by_spanning_tree(concepts_sorted, is_concepts_sorted=True)
    sub_with_sptree_unsort = lca.construct_lattice_by_spanning_tree(concepts_sorted, is_concepts_sorted=False)
    assert sub_with_sptree_sort == sub_with_sptree_unsort,\
        'lattice_construction.construct_lattice_by_spanning_tree failed.' \
        'The result changes with is_concepts_sorted parameter'

    sub_parallel_sort = lca.construct_lattice_by_spanning_tree(concepts_sorted, is_concepts_sorted=True, n_jobs=-1)
    sub_parallel_unsort = lca.construct_lattice_by_spanning_tree(concepts_sorted, is_concepts_sorted=False, n_jobs=-1)
    assert sub_with_sptree_sort == sub_parallel_sort, \
        'lattice_construction.construct_lattice_by_spanning_tree failed.' \
        'Parallel computing give wrong result when concepts are sorted'
    assert sub_with_sptree_unsort == sub_parallel_unsort, \
        'lattice_construction.construct_lattice_by_spanning_tree failed.' \
        'Parallel computing give wrong result when concepts are not sorted'
