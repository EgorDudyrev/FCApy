import json
from fcapy.context import read_json
from fcapy.algorithms import concept_construction
from fcapy.lattice.formal_concept import FormalConcept


def test_close_by_one():
    with open('data/animal_movement_concepts.json', 'r') as f:
        file_data = json.load(f)
    concepts_loaded = {FormalConcept.from_dict(c_json) for c_json in file_data}

    context = read_json("data/animal_movement.json")
    concepts_constructed = concept_construction.close_by_one(context)
    assert set(concepts_constructed) == concepts_loaded,\
        "Close_by_one error. Constructed concepts do not match the true ones"
