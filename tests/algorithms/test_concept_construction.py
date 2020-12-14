import json
from fcapy.context import read_json
from fcapy.algorithms import concept_construction as cca
from fcapy.lattice.formal_concept import FormalConcept


def test_close_by_one():
    with open('data/animal_movement_concepts.json', 'r') as f:
        file_data = json.load(f)
    concepts_loaded = {FormalConcept.from_dict(c_json) for c_json in file_data}

    context = read_json("data/animal_movement.json")
    concepts_constructed = cca.close_by_one(context, output_as_concepts=True)
    assert set(concepts_constructed) == concepts_loaded,\
        "Close_by_one error. Constructed concepts do not match the true ones"

    data = cca.close_by_one(context, output_as_concepts=False)
    extents_i, intents_i = data['extents_i'], data['intents_i']

    def is_equal(idx, c):
        return set(c.extent_i) == set(extents_i[idx]) and set(c.intent_i) == set(intents_i[idx])
    assert all([is_equal(c_i, c) for c_i, c in enumerate(concepts_constructed)]),\
        'Close_by_one failed. Output concepts as dict do not match output concepts as concepts'
