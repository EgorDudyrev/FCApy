import pytest
import numpy as np
from fcapy.context import converters, FormalContext, BINTABLE_CLASSES
from fcapy.lattice.concept_lattice import ConceptLattice
from fcapy.lattice.formal_concept import FormalConcept
from fcapy.mvcontext import MVContext, pattern_structure as PS
from fcapy.mvcontext import pattern_structure as ps, mvcontext


def test_concept_lattice_init():
    with pytest.raises(TypeError):
        ConceptLattice()
    with pytest.raises(ValueError):
        ConceptLattice([])

    c1 = FormalConcept((), (), (0, 1), ('a', 'b'))
    c2 = FormalConcept((0,), ('a',), (0,), ('a',))
    c3 = FormalConcept((0, 1), ('a', 'b'), (), ())
    c4 = FormalConcept((1,), ('b',), (1,), ('b',))
    concepts = [c1, c2, c3, c4]
    ltc = ConceptLattice(concepts)

    parents_dict = {0: {1, 3}, 1: {2}, 2: set(), 3: {2}}
    children_dict = {0: set(), 1: {0}, 2: {1, 3}, 3: {0}}
    ltc = ConceptLattice(concepts, parents_dict=parents_dict)
    assert ltc.children_dict == children_dict,\
        'ConceptLattice.__init__ failed. The calculation of children based on parents is wrong'

    ltc = ConceptLattice(concepts, children_dict=children_dict)
    assert ltc.parents_dict == parents_dict,\
        'ConceptLattice.__init__ failed. The calculation of parents based on children is wrong'

    assert ltc.elements == concepts,\
        'ConceptLattice.__init__ failed. Something is wrong with accessing the elements property'

    assert ltc.top == 2, 'ConceptLattice.__init__ failed. The top concept index is wrongly assigned'
    assert ltc.bottom == 0, 'ConceptLattice.__init__ failed. The bottom concept index is wrongly assigned'


def test_from_context():
    for backend in ['auto'] + list(BINTABLE_CLASSES):
        ctx = FormalContext([[True, False], [False, True]], ['a', 'b'], ['a', 'b'], backend=backend)
        ltc = ConceptLattice.from_context(ctx)

        context_hash = ctx.hash_fixed()

        c1 = FormalConcept((), (), (0, 1), ('a', 'b'), context_hash=context_hash)
        c2 = FormalConcept((0,), ('a',), (0,), ('a',), context_hash=context_hash)
        c3 = FormalConcept((0, 1), ('a', 'b'), (), (), context_hash=context_hash)
        c4 = FormalConcept((1,), ('b',), (1,), ('b',), context_hash=context_hash)
        concepts = [c1, c2, c3, c4]

        assert set(ltc) == set(concepts),\
            'ConceptLattice.from_context failed. Wrong concepts in the constructed lattice'

    ctx = converters.read_csv('data/mango_bin.csv')
    ltc_cbo, ltc_sofia, ltc_lindig = [ConceptLattice.from_context(ctx, algo=alg_name)
                                      for alg_name in ['CbO', 'Sofia', 'Lindig']]
    for L in [ltc_cbo, ltc_sofia, ltc_lindig]:
        assert all([idx == L.index(el) for idx, el in enumerate(L)]),\
            "ConceptLattice.from_context failed. Something is wrong with lattice.index function"
    for L in [ltc_sofia, ltc_lindig]:
        assert ltc_cbo == L, "ConceptLattice.from_context failed. Lattices differ when constructed by different methods"

    data = [[1, 10],
            [2, 22],
            [3, 100],
            [4, 60]]
    object_names = ['a', 'b', 'c', 'd']
    attribute_names = ['M1', 'M2']
    pattern_types = {'M1': ps.IntervalPS, 'M2': ps.IntervalPS}
    mvctx = mvcontext.MVContext(data, pattern_types, object_names, attribute_names)
    ltc_cbo, ltc_sofia = [ConceptLattice.from_context(mvctx, algo=alg_name) for alg_name in ['CbO', 'Sofia']]
    for L in [ltc_cbo, ltc_sofia]:
        assert all([idx == L.index(el) for idx, el in enumerate(L)]),\
            "ConceptLattice.from_context failed. Something is wrong with lattice.index function"
    for L in [ltc_sofia]:
        assert ltc_cbo == L, "ConceptLattice.from_context failed. Lattices differ when constructed by different methods"

    with pytest.raises(NotImplementedError):
        ConceptLattice.from_context(mvctx, algo='Lindig')

    with pytest.raises(ValueError):
        ConceptLattice.from_context(mvctx, algo='OtHeR MeThOd')


def test_from_context_monotone():
    ctx = FormalContext([[True, False], [False, True]], ['a', 'b'], ['a', 'b'])
    ltc = ConceptLattice.from_context(ctx, is_monotone=True)

    c_kwargs = dict(context_hash=ctx.hash_fixed(), is_monotone=True)

    c1 = FormalConcept((), (), (), (), **c_kwargs)
    c2 = FormalConcept((0,), ('a',), (0,), ('a',), **c_kwargs)
    c3 = FormalConcept((0, 1), ('a', 'b'), (0, 1), ('a', 'b'), **c_kwargs)
    c4 = FormalConcept((1,), ('b',), (1,), ('b',), **c_kwargs)
    concepts = [c1, c2, c3, c4]

    assert set(ltc) == set(concepts), \
        'ConceptLattice.from_context failed. Wrong concepts in the constructed lattice'


def test_get_top_bottom_concepts_i():
    c1 = FormalConcept((0,), ('a',), (0,), ('a',))
    c2 = FormalConcept((), (), (0, 1), ('a', 'b'))
    c3 = FormalConcept((0, 1), ('a', 'b'), (), ())
    c4 = FormalConcept((1,), ('b',), (1,), ('b',))
    concepts = [c1, c2, c3, c4]
    top_concept_i, bottom_concept_i = ConceptLattice.get_top_bottom_concepts_i(concepts)
    assert top_concept_i == 2,\
        "ConceptLattice.get_top_bottom_concepts_i failed. Top concept index is wrongly assigned"
    assert bottom_concept_i == 1, \
        "ConceptLattice.get_top_bottom_concepts_i failed. Bottom concept index is wrongly assigned"

    concepts_sorted = [c3, c1, c4, c2]
    top_concept_i, bottom_concept_i = ConceptLattice.get_top_bottom_concepts_i(concepts_sorted, is_concepts_sorted=True)
    assert top_concept_i == 0,\
        "ConceptLattice.get_top_bottom_concepts_i failed. " \
        "Top concept index is wrongly assigned when sorted concepts given"
    assert bottom_concept_i == 3, \
        "ConceptLattice.get_top_bottom_concepts_i failed. " \
        "Bottom concept index is wrongly assigned when sorted concepts given"


def test_to_from_json():
    G, M = ['a', 'b'], ['a', 'b']
    ctx = FormalContext([[True, False], [False, True]], G, M)
    ltc = ConceptLattice.from_context(ctx)
    ltc_json = ltc.read_json(json_data=ltc.write_json(G, M))
    assert ltc == ltc_json,\
        'ConceptLattice.to/read_json failed. The lattice changed after 2 conversions.'

    path = 'test.json'
    ltc.write_json(G, M, path)
    ltc_new = ltc.read_json(path)
    assert ltc == ltc_new,\
        'ConceptLattice.to/read_json failed. The lattice changed after 2 conversions and saving to file.'
    import os
    os.remove(path)

    pattern_types = {'f1': PS.IntervalPS}
    mvK = MVContext([{0: (1, 2)}, {0: (0, 4)}, {0: (2, 3)}], pattern_types, attribute_names=['f1'])
    L = ConceptLattice.from_context(mvK)
    L_new = ConceptLattice.read_json(json_data=L.write_json(mvK.object_names, mvK.attribute_names))
    assert L == L_new, 'ConceptLattice.to/read_json failed. The pattern lattice changed after two conversions'


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

    ltc3 = ConceptLattice([c1, c2, c4], children_dict={0: {1}, 1: {2}, 2: set()})
    ltc3._parents_dict = None
    assert ltc1 != ltc3,\
        "ConceptLattice.__eq__ failed. The lattices should not be equal if their children_dicts are different"
    ltc4 = ConceptLattice([c1, c2, c4], children_dict=None, parents_dict={0: set(), 1: {0}, 2: {1}})
    ltc4._children_dict = None
    assert ltc1 != ltc4, \
        "ConceptLattice.__eq__ failed. The lattices should not be equal if their parents_dicts are different"


def test_transpose():
    c1 = FormalConcept((), (), (0, 1), ('a', 'b'))
    c2 = FormalConcept((0,), ('a',), (0,), ('a',))
    c3 = FormalConcept((1,), ('b',), (1,), ('b',))
    c4 = FormalConcept((0, 1), ('a', 'b'), (), ())

    L = ConceptLattice([c1, c2, c3, c4])
    assert L.T.T == L


def test_concept_new_intent_extent():
    ctx = FormalContext([[True, False], [False, True]], ['a', 'b'], ['a', 'b'])
    ltc = ConceptLattice.from_context(ctx)

    new_extent_i_true = [set(), {0}, {1}, set()]
    new_extent_true = [set(), {'a'}, {'b'}, set()]
    new_intent_i_true = [set(), {0}, {1}, set()]
    new_intent_true = [set(), {'a'}, {'b'}, set()]

    new_extent_i = [ltc.get_concept_new_extent_i(c_i) for c_i in range(len(ltc))]
    new_extent = [ltc.get_concept_new_extent(c_i) for c_i in range(len(ltc))]
    new_intent_i = [ltc.get_concept_new_intent_i(c_i) for c_i in range(len(ltc))]
    new_intent = [ltc.get_concept_new_intent(c_i) for c_i in range(len(ltc))]

    assert new_extent_i == new_extent_i_true,\
        'ConceptLattice.get_concept_new_extent_i failed. The result is different from the expected'
    assert new_extent == new_extent_true, \
        'ConceptLattice.get_concept_new_extent failed. The result is different from the expected'
    assert new_intent_i == new_intent_i_true, \
        'ConceptLattice.get_concept_new_intent_i failed. The result is different from the expected'
    assert new_intent == new_intent_true, \
        'ConceptLattice.get_concept_new_intent failed. The result is different from the expected'


def test_concept_lattice_unknown_measure():
    ctx = FormalContext([[True, False], [False, True]], ['a', 'b'], ['a', 'b'])
    ltc = ConceptLattice.from_context(ctx)

    with pytest.raises(ValueError):
        ltc.calc_concepts_measures('unknown measure')


def test_sort_concepts():
    ctx = FormalContext([[True, False], [False, True]], ['a', 'b'], ['a', 'b'])
    ltc = ConceptLattice.from_context(ctx)
    sorted_extents = [c.extent for c in ltc.sort_concepts(list(ltc))]
    extents_true = [('a', 'b'), ('a',), ('b',), ()]
    assert sorted_extents == extents_true, 'ConceptLattice.sort_concepts failed'


def test_get_chains():
    ctx = converters.read_cxt('data/animal_movement.cxt')
    ltc = ConceptLattice.from_context(ctx)
    chains = ltc.get_chains()
    chains_true = [[0, 1, 4, 7], [0, 3, 6], [0, 1, 5], [0, 2]]

    assert chains == chains_true, "ConceptLattice.get_chains failed. The result is different from the expected"

    chains_sorted = ltc._get_chains(list(ltc), ltc.parents_dict, is_concepts_sorted=True)
    chains_unsorted = ltc._get_chains(list(ltc), ltc.parents_dict, is_concepts_sorted=False)
    assert chains_sorted == chains_unsorted,\
        "ConceptLattice.get_chains failed. The result changes with is_concepts_sorted parameter"


def test_add_concept():
    ctx = converters.read_csv('data/mango_bin.csv')
    from fcapy.algorithms import concept_construction as cca, lattice_construction as lca

    concepts = cca.close_by_one(ctx)
    np.random.shuffle(concepts)
    top_concept_i, bottom_concept_i = ConceptLattice.get_top_bottom_concepts_i(concepts)
    concepts = [concepts[top_concept_i], concepts[bottom_concept_i]] + \
               [c for c_i, c in enumerate(concepts) if c_i not in [top_concept_i, bottom_concept_i]]
    ltc = ConceptLattice(concepts[:2],
                         children_dict={0: {1}, 1: set()})

    for c in concepts[2:]:
        ltc.add(c)

    ltc_true = ConceptLattice(concepts, children_dict=lca.complete_comparison(concepts))

    assert ltc == ltc_true, 'ConceptLattice.add failed'


def test_trace_context():
    ctx = converters.read_csv('data/mango_bin.csv')
    ctx_train = converters.from_pandas(ctx.to_pandas().drop('mango'))
    ltc = ConceptLattice.from_context(ctx_train)
    bottom_concepts, traced_concepts = ltc.trace_context(ctx_train)
    all_parents_dict = ltc.get_all_superconcepts_dict(list(ltc), ltc.parents_dict)
    for g in ctx_train.object_names:
        bottom_concept_i = list(bottom_concepts[g])[0]
        assert traced_concepts[g] - {bottom_concept_i} == all_parents_dict[bottom_concept_i],\
            f'ConceptLattice.trace_context failed. Traced concepts are calculated wrong for object {g}'

    ctx_test = converters.from_pandas(ctx.to_pandas().loc[['mango']])
    bottom_concepts, traced_concepts = ltc.trace_context(ctx_test)
    assert bottom_concepts['mango'] == {6, 9, 13},\
        'ConceptLattice.trace_context failed. Test context traced concepts are calculated wrong'
    traced_concepts_true = {6, 9, 13}
    for c_i in [6, 9, 13]:
        traced_concepts_true |= all_parents_dict[c_i]
    assert traced_concepts['mango'] == traced_concepts_true,\
        "ConceptLattice.trace_context failed. Traced concepts for test context are calculated wrong"


def test_conditional_generators_dict():
    ctx = converters.read_csv('data/mango_bin.csv')
    ltc = ConceptLattice.from_context(ctx)
    condgens_dict = ltc.get_conditional_generators_dict(ctx)
    for c_i, condgens in condgens_dict.items():
        ext_i = ltc[c_i].extent_i
        for supc_i, supc_condgens in condgens.items():
            for supc_condgen in supc_condgens:
                assert set(ctx.extension_i(supc_condgen, base_objects_i=ltc[supc_i].extent_i)) == set(ext_i), \
                    "ConceptLattice.get_conditional_generators_dict failed"

    data = [[5.1, 3.5, 1.4, 0.2],
            [4.9, 3., 1.4, 0.2],
            [4.7, 3.2, 1.3, 0.2],
            [4.6, 3.1, 1.5, 0.2]]
    pattern_types = {'0': ps.IntervalPS, '1': ps.IntervalPS, '2': ps.IntervalPS, '3': ps.IntervalPS}
    mvctx = mvcontext.MVContext(data, pattern_types)
    ltc = ConceptLattice.from_context(mvctx)
    condgens_dict = ltc.get_conditional_generators_dict(mvctx)
    for c_i, condgens in condgens_dict.items():
        ext_i = ltc[c_i].extent_i
        for supc_i, supc_condgens in condgens.items():
            for supc_condgen in supc_condgens:
                assert set(mvctx.extension_i(
                    supc_condgen, base_objects_i=ltc[supc_i].extent_i)) == set(ext_i), \
                    "ConceptLattice.get_conditional_generators_dict failed"

    condgens_dict_approx = ltc.get_conditional_generators_dict(mvctx, algo='approximate')
    for k in condgens_dict.keys():
        assert set(condgens_dict[k]) == set(condgens_dict_approx[k]),\
            'ConceptLattice.get_conditional_generators_dict failed. Approximate method gives wrong results'


def test_measures():
    K = converters.read_csv('data/mango_bin.csv')
    L = ConceptLattice.from_context(K)

    meas1 = np.random.random(len(L))
    meas2 = np.random.random(len(L))
    for i, c in enumerate(L):
        c.measures['m1'] = meas1[i]
        c.measures['m2'] = meas2[i]

    meas_dict = L.measures
    assert all(meas_dict['m1'] == meas1)
    assert all(meas_dict['m2'] == meas2)
    assert len(meas_dict) == 2
