import json
import pytest
from fcapy.context import read_json, read_csv, read_cxt
from fcapy.algorithms import concept_construction as cca
from fcapy.algorithms import lattice_construction as lca
from fcapy.lattice.formal_concept import FormalConcept
from fcapy.lattice import ConceptLattice


def test_close_by_one():
    with open('data/animal_movement_concepts.json', 'r') as f:
        file_data = json.load(f)
    concepts_loaded = {FormalConcept.from_dict(c_json) for c_json in file_data}

    context = read_json("data/animal_movement.json")
    concepts_constructed = cca.close_by_one(context, output_as_concepts=True, iterate_extents=True)
    assert set(concepts_constructed) == concepts_loaded,\
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


def test_sofia_binary():
    ctx = read_cxt('data/digits.cxt')
    concepts_all = cca.close_by_one(ctx)
    subconcepts_dict_all = lca.complete_comparison(concepts_all)
    ltc_all = ConceptLattice(concepts_all, subconcepts_dict=subconcepts_dict_all)
    with pytest.warns(UserWarning):
        ltc_all.calc_concepts_measures('stability', ctx)
    stabilities_all = [c.measures['Stab'] for c in ltc_all.concepts]
    stabilities_all_mean = sum(stabilities_all) / len(stabilities_all)

    concepts_sofia = cca.sofia_binary(ctx, len(concepts_all)//2)
    subconcepts_dict_sofia = lca.complete_comparison(concepts_sofia)
    ltc_sofia = ConceptLattice(concepts_sofia, subconcepts_dict=subconcepts_dict_sofia)
    with pytest.warns(UserWarning):
        ltc_sofia.calc_concepts_measures('stability', ctx)
    stabilities_sofia = [c.measures['Stab'] for c in ltc_sofia.concepts]
    stabilities_sofia_mean = sum(stabilities_sofia) / len(stabilities_sofia)

    assert stabilities_sofia_mean > stabilities_all_mean,\
        'sofia_binary failed. Sofia algorithm does not produce the subset of stable concepts'

    for projection_sorting in ['ascending', 'descending', 'random']:
        concepts_sofia = cca.sofia_binary(ctx, len(concepts_all) // 2, projection_sorting=projection_sorting)
    with pytest.raises(ValueError):
        concepts_sofia = cca.sofia_binary(ctx, len(concepts_all) // 2, projection_sorting="UnKnOwN OrDeR")


def test_sofia_general():
    ctx = read_cxt('data/digits.cxt')
    concepts_all = cca.close_by_one(ctx)
    subconcepts_dict_all = lca.complete_comparison(concepts_all)
    ltc_all = ConceptLattice(concepts_all, subconcepts_dict=subconcepts_dict_all)
    with pytest.warns(UserWarning):
        ltc_all.calc_concepts_measures('stability', ctx)
    stabilities_all = [c.measures['Stab'] for c in ltc_all.concepts]
    stabilities_all_mean = sum(stabilities_all) / len(stabilities_all)

    concepts_sofia = cca.sofia_general(ctx, len(concepts_all)//2)
    subconcepts_dict_sofia = lca.complete_comparison(concepts_sofia)
    ltc_sofia = ConceptLattice(concepts_sofia, subconcepts_dict=subconcepts_dict_sofia)
    with pytest.warns(UserWarning):
        ltc_sofia.calc_concepts_measures('stability', ctx)
    stabilities_sofia = [c.measures['Stab'] for c in ltc_sofia.concepts]
    stabilities_sofia_mean = sum(stabilities_sofia) / len(stabilities_sofia)

    assert stabilities_sofia_mean > stabilities_all_mean,\
        'sofia_general failed. Sofia algorithm does not produce the subset of stable concepts'