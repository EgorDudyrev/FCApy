from fcapy.visualizer.mover import Mover
from fcapy.visualizer import hasse_layouts

from fcapy.context import FormalContext
from fcapy.lattice import ConceptLattice

import pytest


def test_init():
    mvr = Mover()
    assert mvr.pos is None


def test_get_nodes_position():
    path = 'data/animal_movement.json'
    K = FormalContext.read_json(path)
    L = ConceptLattice.from_context(K)

    mvr = Mover()
    mvr.initialize_pos(L)
    mvr.initialize_pos(L, 'fcart')

    with pytest.raises(ValueError):
        mvr.initialize_pos(L, 'FaKeLaYoUt')
