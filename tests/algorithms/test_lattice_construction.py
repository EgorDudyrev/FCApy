import pytest
from fcapy.lattice.formal_concept import FormalConcept
from fcapy.algorithms import lattice_construction as lca, concept_construction as cca
from fcapy.lattice import ConceptLattice
from fcapy.context import read_cxt, read_csv
import numpy as np


def test_complete_comparison():
    c1 = FormalConcept((), (), (0, 1), ('a', 'b'))
    c2 = FormalConcept((0,), ('a',), (0,), ('a',))
    c3 = FormalConcept((1,), ('b',), (1,), ('b',))
    c4 = FormalConcept((0, 1), ('a', 'b'), (), ())
    subconcepts_dict = lca.complete_comparison([c1, c2, c3, c4])
    subconcepts_dict_true = {0: set(), 1: {0}, 2: {0}, 3: {1, 2}}
    assert subconcepts_dict == subconcepts_dict_true,\
        'lattice_construction.complete_comparison failed. Wrong children_dict is constructed'

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
    concepts = list(ltc)
    np.random.seed(42)
    np.random.shuffle(concepts)
    sub_st, sup_st = lca.construct_spanning_tree(concepts)
    sub_true = lca.complete_comparison(concepts)
    sup_true = ConceptLattice._transpose_hierarchy(sub_true)

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
    concepts = list(ltc)
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
    concepts = list(ltc)
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


def test_add_concept():
    ctx = read_csv('data/mango_bin.csv')
    np.random.seed(13)
    concepts_true = cca.close_by_one(ctx)
    np.random.shuffle(concepts_true)
    top_concept_i, bottom_concept_i = ConceptLattice.get_top_bottom_concepts_i(concepts_true)
    concepts_true = [concepts_true[top_concept_i], concepts_true[bottom_concept_i]] + \
               [c for c_i, c in enumerate(concepts_true) if c_i not in [top_concept_i, bottom_concept_i]]

    subconcepts_dict_true = lca.complete_comparison(concepts_true)
    superconcepts_dict_true = ConceptLattice._transpose_hierarchy(subconcepts_dict_true)

    concepts = concepts_true[:2]
    subconcepts_dict, superconcepts_dict = {0: {1}, 1: set()}, {0: set(), 1: {0}}
    for c_i, c in enumerate(concepts_true[2:]):
        c_i += 2
        lca.add_concept(c, concepts, subconcepts_dict, superconcepts_dict,
                        top_concept_i=0, bottom_concept_i=1, inplace=True)

    assert concepts == concepts_true,\
        'lattice_construction.add failed. Concepts list dict differs when run inplace'
    assert subconcepts_dict == subconcepts_dict_true,\
        'lattice_construction.add failed. Subconcepts dict differs when run inplace'
    assert superconcepts_dict == superconcepts_dict_true, \
        'lattice_construction.add failed. Superconcepts dict differs when run inplace'

    concepts = concepts_true[:2]
    subconcepts_dict, superconcepts_dict = {0: {1}, 1: set()}, {0: set(), 1: {0}}
    for c_i, c in enumerate(concepts_true[2:]):
        c_i += 2
        concepts, subconcepts_dict, superconcepts_dict, _, _ = lca.add_concept(
            c, concepts[:c_i], subconcepts_dict, superconcepts_dict,
            top_concept_i=0, bottom_concept_i=1, inplace=False)

    assert concepts == concepts_true, \
        'lattice_construction.add failed. Concepts list dict differs when run not inplace'
    assert subconcepts_dict == subconcepts_dict_true, \
        'lattice_construction.add failed. Subconcepts dict differs when run not inplace'
    assert superconcepts_dict == superconcepts_dict_true, \
        'lattice_construction.add failed. Superconcepts dict differs when run not inplace'

    c_newbottom = FormalConcept((), (), (0, 1, 2, 3), ('a', 'b', 'c', 'd'))
    c1 = FormalConcept((2,), ('c',), (0, 1, 2), ('a', 'b', 'c'))
    c2 = FormalConcept((0, 2), ('a', 'c'), (0, 2), ('a', 'c'))
    c3 = FormalConcept((1, 2), ('b', 'c'), (1, 2), ('b', 'c'))
    c4 = FormalConcept((0, 1, 2), ('a', 'b', 'c'), (2,), ('c',))
    c_newtop = FormalConcept((0, 1, 2, 3), ('a', 'b', 'c', 'd'), (), ())

    concepts_true = [c1, c2, c3, c4, c_newbottom, c_newtop]
    subconcepts_dict_true = {4: set(), 0: {4}, 1: {0}, 2: {0}, 3: {1, 2}, 5: {3}}
    superconcepts_dict_true = ConceptLattice._transpose_hierarchy(subconcepts_dict_true)

    concepts = [c1, c2, c3, c4]
    subconcepts_dict = lca.complete_comparison(concepts)
    superconcepts_dict = ConceptLattice._transpose_hierarchy(subconcepts_dict)
    for c in [c_newbottom, c_newtop]:
        lca.add_concept(c, concepts, subconcepts_dict, superconcepts_dict, inplace=True)
    error_msg = 'lattice_construction.add failed. Error when adding new top_concept or bottom_concept'
    assert set(concepts) == set(concepts_true), error_msg
    assert subconcepts_dict == subconcepts_dict_true, error_msg
    assert superconcepts_dict == superconcepts_dict_true, error_msg


def test_remove_concept():
    ctx = read_csv('data/mango_bin.csv')
    concepts_true = cca.close_by_one(ctx)
    concepts_true1 = cca.close_by_one(ctx)
    np.random.seed(13)
    np.random.shuffle(concepts_true)
    np.random.seed(13)
    np.random.shuffle(concepts_true1)
    top_concept_i, bottom_concept_i = ConceptLattice.get_top_bottom_concepts_i(concepts_true)

    subconcepts_dict_true = lca.complete_comparison(concepts_true)
    superconcepts_dict_true = ConceptLattice._transpose_hierarchy(subconcepts_dict_true)
    subconcepts_dict_true1 = lca.complete_comparison(concepts_true1)
    superconcepts_dict_true1 = ConceptLattice._transpose_hierarchy(subconcepts_dict_true1)

    with pytest.raises(AssertionError, match='Cannot remove the top concept of the lattice'):
        concepts, subconcepts_dict, superconcepts_dict, _, _ = lca.remove_concept(
            top_concept_i, concepts_true, subconcepts_dict_true, superconcepts_dict_true, inplace=False)

    with pytest.raises(AssertionError, match='Cannot remove the bottom concept of the lattice'):
        concepts, subconcepts_dict, superconcepts_dict, _, _ = lca.remove_concept(
            bottom_concept_i, concepts_true, subconcepts_dict_true, superconcepts_dict_true, inplace=False)

    for i in range(len(concepts_true)):
        if i in {top_concept_i, bottom_concept_i}:
            continue

        concepts, subconcepts_dict, superconcepts_dict, _, _ = lca.remove_concept(
            i, concepts_true, subconcepts_dict_true, superconcepts_dict_true, inplace=False)
        subconcepts_dict_true_new = lca.complete_comparison(concepts)
        superconcepts_dict_true_new = ConceptLattice._transpose_hierarchy(subconcepts_dict_true_new)
        assert concepts_true[i] not in concepts, 'remove_concept failed. The concept is still in the concept list'
        assert concepts_true == concepts_true1,\
            'remove_concept failed. The original concepts list has been changed during non inplace function call'
        assert subconcepts_dict_true == subconcepts_dict_true1,\
            'remove_concept failed. The original children_dict has been changed during non inplace function call'
        assert superconcepts_dict_true == superconcepts_dict_true1, \
            'remove_concept failed. The original parents_dict has been changed during non inplace function call'

        assert subconcepts_dict == subconcepts_dict_true_new,\
            'remove_concept failed. Subconcept_dict is calculated wrong'
        assert superconcepts_dict == superconcepts_dict_true_new, \
            'remove_concept failed. Superconcept_dict is calculated wrong'

    for i in range(len(concepts_true)):
        if i in {top_concept_i, bottom_concept_i}:
            continue

        from copy import deepcopy
        concepts_true = deepcopy(concepts_true1)
        subconcepts_dict_true = deepcopy(subconcepts_dict_true1)
        superconcepts_dict_true = deepcopy(superconcepts_dict_true1)

        concepts, subconcepts_dict, superconcepts_dict, _, _ = lca.remove_concept(
            i, concepts_true, subconcepts_dict_true, superconcepts_dict_true, inplace=True)
        subconcepts_dict_true_new = lca.complete_comparison(concepts)
        superconcepts_dict_true_new = ConceptLattice._transpose_hierarchy(subconcepts_dict_true_new)
        assert concepts_true1[i] not in concepts, 'remove_concept failed. The concept is still in the concept list'
        assert concepts_true != concepts_true1,\
            'remove_concept failed. The original concepts list should been changed during inplace function call'
        assert subconcepts_dict_true != subconcepts_dict_true1,\
            'remove_concept failed. The original children_dict should been changed during inplace function call'
        assert superconcepts_dict_true != superconcepts_dict_true1, \
            'remove_concept failed. The original parents_dict should been changed during inplace function call'

        assert subconcepts_dict == subconcepts_dict_true_new,\
            'remove_concept failed. Subconcept_dict is calculated wrong'
        assert superconcepts_dict == superconcepts_dict_true_new, \
            'remove_concept failed. Superconcept_dict is calculated wrong'
