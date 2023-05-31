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

    concepts_constructed = list(cca.close_by_one(context))
    assert set(concepts_constructed) == set(concepts_loaded),\
        "Close_by_one error. Constructed concepts do not match the true ones"

    context = read_csv("data/mango_bin.csv")
    concepts_constructed = list(cca.close_by_one(context))
    assert len(concepts_constructed) == 22, "Close_by_one failed. Binary mango dataset should have 22 concepts"


    data = [[1], [2]]
    object_names = ['a', 'b']
    attribute_names = ['M1']
    pattern_types = {'M1': PS.IntervalPS}
    mvctx = mvcontext.MVContext(data, pattern_types, object_names, attribute_names)
    concepts = list(cca.close_by_one(mvctx))
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


def test_sofia():
    ctx = read_cxt('data/digits.cxt')
    concepts_all = list(cca.close_by_one(ctx))
    concepts_sofia = cca.sofia(ctx, len(concepts_all))
    concepts_sofia = [FormalConcept(c.extent_i, c.extent, c.intent_i, c.intent, context_hash=ctx.hash_fixed())
                      for c in concepts_sofia]
    assert len(concepts_all) == len(concepts_sofia),\
        'sofia_binary failed. Sofia algorithm produces wrong number of all concepts ' \
        f'({len(concepts_sofia)} against {len(concepts_all)})'
    assert set(concepts_all) == set(concepts_sofia),\
        'sofia_binary failed. Sofia algorithm produces the wrong set of all concepts'

    subconcepts_dict_all = lca.complete_comparison(concepts_all)
    ltc_all = ConceptLattice(concepts_all, subconcepts_dict=subconcepts_dict_all)
    with pytest.warns(UserWarning):
        ltc_all.calc_concepts_measures('stability', ctx)
    ltc_all.calc_concepts_measures('LStab')
    mean_stability_all = sum(c.measures['LStab'] for c in ltc_all) / len(ltc_all)

    ltc_sofia_half = ConceptLattice(cca.sofia(ctx, len(concepts_all)//2))
    ltc_sofia_half.calc_concepts_measures('LStab')
    mean_stability_half = sum(c.measures['LStab'] for c in ltc_sofia_half) / len(ltc_sofia_half)
    assert mean_stability_half > mean_stability_all, \
        'sofia failed. Sofia algorithm does not produce the subset of stable concepts'


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
    ctx_full = from_pandas(ctx.to_pandas().drop(columns=['fruit']))

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
