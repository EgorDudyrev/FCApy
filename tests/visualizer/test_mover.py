from fcapy.visualizer.mover import Mover, DifferentHierarchyLevelsError
from fcapy.visualizer import hasse_layouts

from fcapy.context import FormalContext
from fcapy.lattice import ConceptLattice

import pytest


def test_init():
    mvr = Mover()
    assert mvr.pos is None

    pos = {
        0: (0.0, 1.0), 1: (-0.5, 0.5), 2: (0.0, 0.5), 3: (0.5, 0.5),
        4: (-0.5, 0.0), 5: (0.0, 0.0), 6: (0.5, 0.0), 7: (0.0, -0.5)
    }
    mvr = Mover(pos=pos)
    assert pos == pos


def test_get_nodes_position():
    path = 'data/animal_movement.json'
    K = FormalContext.read_json(path)
    L = ConceptLattice.from_context(K)

    mvr = Mover()
    mvr.initialize_pos(L)
    mvr.initialize_pos(L, 'fcart')

    with pytest.raises(ValueError):
        mvr.initialize_pos(L, 'FaKeLaYoUt')


def test_swap_nodes():
    pos = {
        0: (0.0, 1.0), 1: (-0.5, 0.5), 2: (0.0, 0.5), 3: (0.5, 0.5),
        4: (-0.5, 0.0), 5: (0.0, 0.0), 6: (0.5, 0.0), 7: (0.0, -0.5)
    }
    mvr = Mover(pos={k: v for k, v in pos.items()})

    mvr.swap_nodes(1, 2)
    assert mvr.pos[1] == pos[2] and mvr.pos[2] == pos[1]

    with pytest.raises(DifferentHierarchyLevelsError):
        mvr.swap_nodes(1, 4)
