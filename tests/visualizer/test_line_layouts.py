from fcapy.context import FormalContext
from fcapy.lattice import ConceptLattice
from fcapy.visualizer import line_layouts

import numpy as np


def test_calc_levels():
    path = 'data/animal_movement.json'
    K = FormalContext.read_json(path)

    K_df = K.to_pandas()
    for m in K.attribute_names:
        K_df[f'not_{m}'] = ~K_df[m]
    K = FormalContext.from_pandas(K_df)

    L = ConceptLattice.from_context(K)

    c_levels, levels_dict = line_layouts.calc_levels(L)
    assert all([c_levels[c_i] < c_levels[sub_i] for c_i, subs_i in L.descendants_dict.items() for sub_i in subs_i]),\
        'Calc_levels function failed. Some elements have level not bigger than that of their superelements '


def test_multipartite_layout():
    path = 'data/animal_movement.json'
    K = FormalContext.read_json(path)
    L = ConceptLattice.from_context(K)

    pos_fact = line_layouts.multipartite_layout(L)
    pos_true = {
        0: [0.0000, 1.0000], 1: [0.6667, 0.3333], 2: [0.0000, 0.3333], 3: [-0.6667, 0.3333],
        4: [0.6667, -0.3333], 5: [0.0000, -0.3333], 6: [-0.6667, -0.3333], 7: [0.0000, -1.0000]
    }
    pos_diff = [np.sqrt(((np.array(pos_fact[c_i]) - np.array(pos_true[c_i])) ** 2).sum()) for c_i in range(len(L))]
    assert max(pos_diff) < 1e-4, \
        f'layouts.multipartite_layout failed. Nodes position calculated wrongly.'


def test_fcart_layout():
    path = 'data/mango_bin.csv'
    K = FormalContext.read_csv(path)
    L = ConceptLattice.from_context(K)

    pos_fact = line_layouts.fcart_layout(L)

    pos_true = {
        0: [0.0000, 1.0000], 1: [-0.7143, 0.6667], 2: [-0.4286, 0.6667], 3: [-0.1429, 0.6667], 4: [0.1429, 0.6667],
        5: [-0.7500, 0.3333], 6: [-0.5000, 0.3333], 7: [0.4286, 0.6667], 8: [0.0000, 0.3333], 9: [0.2500, 0.3333],
        10: [-0.6667, 0.0000], 11: [-0.3333, 0.0000], 12: [-0.2500, 0.3333], 13: [0.5000, 0.3333], 14: [0.7143, 0.6667],
        15: [0.3333, 0.0000], 16: [0.3333, -0.3333], 17: [0.6667, 0.0000], 18: [0.0000, 0.0000], 19: [0.7500, 0.3333],
        20: [-0.3333, -0.3333], 21: [0.0000, -0.6667]
    }
    pos_diff = [np.sqrt(((np.array(pos_fact[c_i]) - np.array(pos_true[c_i])) ** 2).sum()) for c_i in range(len(L))]
    assert max(pos_diff) < 1e-4, \
        f'layouts.fcart_layout failed. Nodes position calculated wrongly.'
    
    pos_fact = line_layouts.fcart_layout(L, c=1, dpth=2)

    pos_true = {
        0: [0.0000, 1.0000], 1: [-0.7143, 0.6667], 2: [-0.4286, 0.6667], 3: [-0.1429, 0.6667], 4: [0.1429, 0.6667],
        5: [-0.7500, 0.3333], 6: [-0.5000, 0.3333], 7: [0.4286, 0.6667], 8: [0.0000, 0.3333], 9: [0.2500, 0.3333],
        10: [0.0000, 0.0000], 11: [-0.6667, 0.0000], 12: [-0.2500, 0.3333], 13: [0.5000, 0.3333], 14: [0.7143, 0.6667],
        15: [-0.3333, 0.0000], 16: [-0.3333, -0.3333], 17: [0.3333, 0.0000], 18: [0.6667, 0.0000], 19: [0.7500, 0.3333],
        20: [0.3333, -0.3333], 21: [0.0000, -0.6667]
    }
    pos_diff = [np.sqrt(((np.array(pos_fact[c_i]) - np.array(pos_true[c_i])) ** 2).sum()) for c_i in range(len(L))]
    assert max(pos_diff) < 1e-4, \
        f'layouts.fcart _layout failed. Nodes position calculated wrongly while changing parameters.'


def test_layouts_dict():
    path = 'data/animal_movement.json'
    K = FormalContext.read_json(path)
    L = ConceptLattice.from_context(K)

    for x in ['multipartite', 'fcart']:
        pos = line_layouts.LAYOUTS[x](L)


def test_find_nodes_edges_overlay():
    pos_right = {0: (0, 0), 1: (1, -1), 2: (1, -2), 3: (0, -3)}
    pos_wrong = {0: (0, 0), 1: (0, -1), 2: (0, -2), 3: (0, -3)}
    edges = [(0, 1), (0, 3), (1, 2)]
    nodes = [0, 1, 2, 3]

    assert line_layouts.find_nodes_edges_overlay(pos_wrong, nodes, edges) == {(0, 3): frozenset({1, 2})}
    assert line_layouts.find_nodes_edges_overlay(pos_right, nodes, edges) == {}

    # Real world case: Animal concept lattice with no overlaps
    pos = {
        0: (0.0, 1.0), 1: (-0.5, 0.5), 2: (0.0, 0.5), 3: (0.5, 0.5),
        4: (-0.5, 0.0), 5: (0.0, 0.0), 6: (0.5, 0.0), 7: (0.0, -0.5)
    }
    nodes = (0, 1, 2, 3, 4, 5, 6, 7)
    edges = ((0, 1), (0, 2), (0, 3), (1, 4), (1, 5), (2, 4), (3, 5), (3, 6), (4, 7), (5, 7), (6, 7))
    assert line_layouts.find_nodes_edges_overlay(pos, nodes, edges) == {}
