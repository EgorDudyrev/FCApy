import json
import pytest
from fcapy.context import read_json, read_csv, read_cxt, from_pandas
from fcapy.algorithms import concept_construction as cca
from fcapy.algorithms import lattice_construction as lca
from fcapy.lattice.formal_concept import FormalConcept, JSON_BOTTOM_PLACEHOLDER
from fcapy.context.formal_context import FormalContext
from fcapy.lattice.pattern_concept import PatternConcept
from fcapy.lattice import ConceptLattice
from fcapy.mvcontext import pattern_structure as PS, mvcontext
from fcapy.ml import decision_lattice as DL

import numpy as np
from sklearn.datasets import load_iris
from sklearn.metrics import accuracy_score
from sklearn.tree import DecisionTreeClassifier


def test_close_by_one():
    with open('data/animal_movement_concepts.json', 'r') as f:
        file_data = json.load(f)
    context = read_json("data/animal_movement.json")

    concepts_loaded = []
    for c_json in file_data:
        c_json['Context_Hash'] = context.hash_fixed()
        concepts_loaded.append(FormalConcept.from_dict(c_json))

    concepts_constructed = cca.close_by_one(context, output_as_concepts=True, iterate_extents=True)
    assert set(concepts_constructed) == set(concepts_loaded),\
        "Close_by_one error. Constructed concepts do not match the true ones"

    data = cca.close_by_one(context, output_as_concepts=False, iterate_extents=True)
    extents_i, intents_i = data['extents_i'], data['intents_i']

    def is_equal(idx, c):
        return set(c.extent_i) == set(extents_i[idx]) and set(c.intent_i) == set(intents_i[idx])
    assert all([is_equal(c_i, c) for c_i, c in enumerate(concepts_constructed)]),\
        'Close_by_one failed. Output concepts as dict do not match output concepts as concepts'

    context = read_csv("data/mango_bin.csv")
    concepts_constructed = cca.close_by_one(context, output_as_concepts=True, iterate_extents=True)
    assert len(concepts_constructed) == 22, "Close_by_one failed. Binary mango dataset should have 22 concepts"

    concepts_constructed_iterixt = cca.close_by_one(context, output_as_concepts=True, iterate_extents=False)
    concepts_constructed_iterauto = cca.close_by_one(context, output_as_concepts=True, iterate_extents=None)
    assert set(concepts_constructed) == set(concepts_constructed_iterixt),\
        "Close_by_one failed. Iterations over extents and intents give different set of concepts"
    assert set(concepts_constructed) == set(concepts_constructed_iterauto), \
        "Close_by_one failed. Iterations over extents and automatically chosen set give different set of concepts"

    data = [[1], [2]]
    object_names = ['a', 'b']
    attribute_names = ['M1']
    pattern_types = {'M1': PS.IntervalPS}
    mvctx = mvcontext.MVContext(data, pattern_types, object_names, attribute_names)
    concepts = cca.close_by_one(mvctx)
    context_hash = mvctx.hash_fixed()
    c0 = PatternConcept((0, 1), ('a', 'b'), {0: (1, 2)}, {'M1': (1, 2)},
                        pattern_types, mvctx.attribute_names, context_hash=context_hash)
    c1 = PatternConcept((0,), ('a',), {0: (1, 1)}, {'M1': (1, 1)},
                        pattern_types, mvctx.attribute_names, context_hash=context_hash)
    c2 = PatternConcept((1,), ('b',), {0: (2, 2)}, {'M1': (2, 2)},
                        pattern_types, mvctx.attribute_names, context_hash=context_hash)
    c3 = PatternConcept((), (), {0: None}, {'M1': None},
                        pattern_types, mvctx.attribute_names, context_hash=context_hash)
    assert set(concepts) == {c0, c1, c2, c3}, 'Close_by_one failed.'


def test_sofia_binary():
    ctx = read_cxt('data/digits.cxt')
    concepts_all = cca.close_by_one(ctx)
    lattice_sofia = cca.sofia_binary(ctx, len(concepts_all))
    concepts_sofia = list(lattice_sofia)
    assert len(concepts_all) == len(concepts_sofia),\
        'sofia_binary failed. Sofia algorithm produces wrong number of all concepts ' \
        f'({len(concepts_sofia)} against {len(concepts_all)})'
    assert set(concepts_all) == set(concepts_sofia),\
        'sofia_binary failed. Sofia algorithm produces the wrong set of all concepts'

    subconcepts_dict_all = lca.complete_comparison(concepts_all)
    ltc_all = ConceptLattice(concepts_all, subconcepts_dict=subconcepts_dict_all)
    with pytest.warns(UserWarning):
        ltc_all.calc_concepts_measures('stability', ctx)
    stabilities_all = [c.measures['Stab'] for c in ltc_all]
    stabilities_all_mean = sum(stabilities_all) / len(stabilities_all)

    ltc_sofia = cca.sofia_binary(ctx, len(concepts_all)//2)
    ltc_sofia_precalc = ConceptLattice.read_json('data/digits_sofia_lattice_22.json')
    assert ltc_sofia == ltc_sofia_precalc

    with pytest.warns(UserWarning):
        ltc_sofia.calc_concepts_measures('stability', ctx)
    stabilities_sofia = [c.measures['Stab'] for c in ltc_sofia]
    stabilities_sofia_mean = sum(stabilities_sofia) / len(stabilities_sofia)

    assert stabilities_sofia_mean > stabilities_all_mean,\
        'sofia_binary failed. Sofia algorithm does not produce the subset of stable concepts'

    for projection_sorting in ['ascending', 'descending', 'random']:
        concepts_sofia = cca.sofia_binary(ctx, len(concepts_all) // 2, proj_sorting=projection_sorting)
    with pytest.raises(ValueError):
        concepts_sofia = cca.sofia_binary(ctx, len(concepts_all) // 2, proj_sorting="UnKnOwN OrDeR")


def test_sofia_general():
    ctx = read_cxt('data/digits.cxt')
    concepts_all = cca.close_by_one(ctx)
    lattice_sofia = cca.sofia_general(ctx, len(concepts_all))
    concepts_sofia = list(lattice_sofia)
    assert len(concepts_all) == len(concepts_sofia),\
        'sofia_general failed. Sofia algorithm produces wrong number of all concepts' \
        f'({len(concepts_sofia)} against {len(concepts_all)})'
    assert set(concepts_all) == set(concepts_sofia), \
        'sofia_general failed. Sofia algorithm produces wrong set of all concepts. '

    subconcepts_dict_all = lca.complete_comparison(concepts_all)
    ltc_all = ConceptLattice(concepts_all, subconcepts_dict=subconcepts_dict_all)
    with pytest.warns(UserWarning):
        ltc_all.calc_concepts_measures('stability', ctx)
    stabilities_all = [c.measures['Stab'] for c in ltc_all]
    stabilities_all_mean = sum(stabilities_all) / len(stabilities_all)

    lattice_sofia = cca.sofia_general(ctx, len(concepts_all)//2)
    concepts_sofia = list(lattice_sofia)
    subconcepts_dict_sofia = lca.complete_comparison(concepts_sofia)
    ltc_sofia = ConceptLattice(concepts_sofia, subconcepts_dict=subconcepts_dict_sofia)
    with pytest.warns(UserWarning):
        ltc_sofia.calc_concepts_measures('stability', ctx)
    stabilities_sofia = [c.measures['Stab'] for c in ltc_sofia]
    stabilities_sofia_mean = sum(stabilities_sofia) / len(stabilities_sofia)

    assert stabilities_sofia_mean > stabilities_all_mean,\
        'sofia_general failed. Sofia algorithm does not produce the subset of stable concepts'


def test_parse_decision_tree_to_extents():
    iris_data = load_iris()
    X = iris_data['data']
    Y = iris_data['target']

    dt = DecisionTreeClassifier()
    dt.fit(X, Y)
    extents = cca.parse_decision_tree_to_extents(dt, X, n_jobs=1)
    extents_par = cca.parse_decision_tree_to_extents(dt, X, n_jobs=2)
    assert set([tuple(sorted(ext_)) for ext_ in extents]) == set([tuple(sorted(ext_)) for ext_ in extents_par])


def test_random_forest_concepts():
    ctx = read_csv('data/mango_bin.csv')
    y_train = ctx.to_pandas().drop('mango')['fruit'].values
    y_test = ctx.to_pandas().loc[['mango']]['fruit'].values

    ctx = read_csv('data/mango_bin.csv')
    ctx_full = from_pandas(ctx.to_pandas().drop('fruit', 1))

    ctx_full._target = list(y_train) + list(y_test)
    dlc = DL.DecisionLatticeClassifier(algo='RandomForest', algo_params={'random_state': 42})
    dlc.fit(ctx_full)


    iris_data = load_iris()
    X = iris_data['data']
    Y = iris_data['target']
    feature_names = iris_data['feature_names']

    np.random.seed(42)
    train_idxs = np.random.choice(range(len(Y)), 100, replace=False)
    test_idxs = sorted(set(range(len(Y))) - set(train_idxs))

    pattern_types = {f: PS.IntervalPS for f in feature_names}
    mvctx_full = mvcontext.MVContext(data=X, target=Y, pattern_types=pattern_types, attribute_names=feature_names)
    mvctx_train, mvctx_test = mvctx_full[train_idxs], mvctx_full[test_idxs]

    dlc = DL.DecisionLatticeClassifier(algo='RandomForest', algo_params={'random_state': 42})
    dlc.fit(mvctx_train)
    preds_train, preds_test = dlc.predict(mvctx_train), dlc.predict(mvctx_test)
    acc_train, acc_test = accuracy_score(Y[train_idxs], preds_train), accuracy_score(Y[test_idxs], preds_test)
    assert acc_train == 1, 'random_forest_concepts failed'
    assert acc_test >= 0.88, 'random_forest_concepts failed'

    
def test_lindig_algorithm():
    context = FormalContext.read_csv('data/mango_bin.csv')
    L_cbo = ConceptLattice.from_context(context, algo='CbO')
    for iterate_extents in [False, True]:
        L_lin = cca.lindig_algorithm(context, iterate_extents)
        assert L_cbo == L_lin
