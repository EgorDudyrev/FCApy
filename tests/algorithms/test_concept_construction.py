import json
from fcapy.context import read_json, read_csv
from fcapy.algorithms import concept_construction as cca
from fcapy.lattice.formal_concept import FormalConcept


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
