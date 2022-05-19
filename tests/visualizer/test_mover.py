from fcapy.visualizer.mover import Mover, DifferentHierarchyLevelsError, UnknownDirectionError
from fcapy.visualizer import line_layouts

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
    assert mvr.pos == pos


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


def test_place_node():
    pos = {
        0: (0.0, 1.0), 1: (-0.5, 0.5), 2: (0.0, 0.5), 3: (0.5, 0.5),
        4: (-0.5, 0.0), 5: (0.0, 0.0), 6: (0.5, 0.0), 7: (0.0, -0.5)
    }
    mvr = Mover(pos={k: v for k, v in pos.items()})
    mvr.place_node(node_i=6, x=0.6)
    pos_true = pos.copy()
    pos_true[6] = (0.6, pos_true[6][1])
    assert mvr.pos == pos_true


def test_jitter_node():
    pos = {
        0: (0.0, 1.0), 1: (-0.5, 0.5), 2: (0.0, 0.5), 3: (0.5, 0.5),
        4: (-0.5, 0.0), 5: (0.0, 0.0), 6: (0.5, 0.0), 7: (0.0, -0.5)
    }
    mvr = Mover(pos={k: v for k, v in pos.items()})
    mvr.jitter_node(node_i=6, dx=0.1)
    pos_true = pos.copy()
    pos_true[6] = (pos_true[6][0] + 0.1, pos_true[6][1])
    assert mvr.pos == pos_true


def test_shift_node():
    pos = {
        0: (0.0, 1.0), 1: (-0.5, 0.5), 2: (0.0, 0.5), 3: (0.5, 0.5),
        4: (-0.5, 0.0), 5: (0.0, 0.0), 6: (0.5, 0.0), 7: (0.0, -0.5),
        8: (0.8, 0.0)
    }
    mvr = Mover(pos={k: v for k, v in pos.items()})
    mvr.shift_node(5, n_nodes_right=2)
    pos_true = pos.copy()
    pos_true[6], pos_true[8], pos_true[5] = pos_true[5], pos_true[6], pos_true[8]
    assert mvr.pos == pos_true


def test_directions():
    pos_true = {
        0: (0.0, 1.0), 1: (-0.5, 0.5), 2: (0.0, 0.5), 3: (0.5, 0.5),
        4: (-0.5, 0.0), 5: (0.0, 0.0), 6: (0.5, 0.0), 7: (0.0, -0.5),
        8: (0.8, 0.0)
    }
    mvr = Mover(pos={k: v for k, v in pos_true.items()})
    mvr.direction = 'h'
    pos_h = mvr.pos
    mvr.direction = 'v'
    pos_v = mvr.pos
    assert pos_true == pos_v

    with pytest.raises(UnknownDirectionError):
        mvr.direction = 'UnknownDirection'
