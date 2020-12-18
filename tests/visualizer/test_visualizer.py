from fcapy.visualizer import visualizer
from fcapy.context import converters
from fcapy.lattice.concept_lattice import ConceptLattice
import numpy as np


def test__init__():
    vsl = visualizer.Visualizer()


def test_get_nodes_position():
    path = 'data/animal_movement.json'
    ctx = converters.read_json(path)
    ltc = ConceptLattice.from_context(ctx)

    vsl = visualizer.Visualizer(ltc)
    pos = {0: np.array([0.0, -1.0]),
           1: np.array([0.6666666666666666, 0.3333333333333333]),
           2: np.array([0.0, 1.0]),
           3: np.array([0.6666666666666666, -0.3333333333333333]),
           4: np.array([0.0, -0.3333333333333333]),
           5: np.array([0.0, 0.3333333333333333]),
           6: np.array([-0.6666666666666666, -0.3333333333333333]),
           7: np.array([-0.6666666666666666, 0.3333333333333333]),
           }

    pos_diff_dict = {
        c_i: np.sqrt(((np.array(vsl._pos[c_i]) - np.array(pos[c_i])) ** 2).sum())
        for c_i in range(len(ltc.concepts))
    }
    pos_diff_mean = np.mean(list(pos_diff_dict.values()))
    assert pos_diff_mean < 1e-6, \
        f'Visualizer.get_nodes_position failed. Nodes position calculated wrongly.' +\
        f'Position differences: {pos_diff_dict}'


def test_draw_networkx():
    path = 'data/animal_movement.json'
    ctx = converters.read_json(path)
    ltc = ConceptLattice.from_context(ctx)

    vsl = visualizer.Visualizer(ltc)
    vsl.draw_networkx(draw_node_indices=True)


def test_get_plotly_figure():
    path = 'data/animal_movement.json'
    ctx = converters.read_json(path)
    ltc = ConceptLattice.from_context(ctx)

    vsl = visualizer.Visualizer(ltc)
    vsl.get_plotly_figure()
