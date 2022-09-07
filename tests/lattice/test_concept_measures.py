import pytest

from fcapy.lattice import concept_measures as cm
from fcapy.context import read_json
from fcapy.lattice.concept_lattice import ConceptLattice


def test_stability():
    ctx = read_json('data/animal_movement.json')
    ltc = ConceptLattice.read_json('data/animal_movement_lattice.json')

    stabs_true = [c.measures.get('Stab') for c in ltc]

    with pytest.warns(UserWarning):
        ltc.calc_concepts_measures('stability', context=ctx)
    stabs_est = [c.measures.get('Stab') for c in ltc]
    assert stabs_est == stabs_true,\
        "concept_measure.stability failed. Stability of concepts does not match the ones computed by latviz.loria.ft"


def test_stability_bounds():
    ltc = ConceptLattice.read_json('data/animal_movement_lattice.json')

    lstabs_true = [c.measures.get('LStab') for c in ltc]

    ltc.calc_concepts_measures('stability_bounds')
    lstabs_est = [c.measures.get('LStab') for c in ltc]

    # TODO: Check why stability bounds are not fully match the ones from latviz.loria.ft
    mae = sum([abs(lstabs_true[c_i]-lstabs_est[c_i])
               if len(c.extent_i) > 0 else 0 for c_i, c in enumerate(ltc)]
              )/len(lstabs_true)
    assert mae < 0.05, "concept_measure.stability_bounds failed. " \
                       "Lower stability bounds of concepts does not match the ones computed by latviz.loria.ft"
