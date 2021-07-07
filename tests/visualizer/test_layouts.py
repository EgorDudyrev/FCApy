from fcapy.context import FormalContext
from fcapy.lattice import ConceptLattice
from fcapy.visualizer import layouts

import numpy as np


def test_multipartite_layout():
    path = 'data/animal_movement.json'
    K = FormalContext.from_json(path)
    L = ConceptLattice.from_context(K)

    pos_fact = layouts.multipartite_layout(L)
    pos_true = {
        0: [0.0, 1.0],
        1: [0.6666666666666666, 0.3333333333333333],
        2: [0.0, 0.3333333333333333],
        3: [-0.6666666666666666, 0.3333333333333333],
        4: [0.6666666666666666, -0.3333333333333333],
        5: [0.0, -0.3333333333333333],
        6: [-0.6666666666666666, -0.3333333333333333],
        7: [0.0, -1.0]
    }
    pos_diff_dict = {
        c_i: np.sqrt(((np.array(pos_fact[c_i]) - np.array(pos_true[c_i])) ** 2).sum())
        for c_i in range(len(L))
    }
    pos_diff_mean = np.mean(list(pos_diff_dict.values()))
    assert pos_diff_mean < 1e-6, \
        f'layouts.multipartite_layout failed. Nodes position calculated wrongly.' + \
        f'Position differences: {pos_diff_dict}'


def test_fcart_layout():
    path = 'data/animal_movement.json'
    K = FormalContext.from_json(path)
    L = ConceptLattice.from_context(K)

    pos_fact = layouts.fcart_layout(L)
    pos_true = {
        0: [0.0, 1.0], 
        1: [-0.5, 0.5], 
        2: [0.0, 0.5], 
        3: [0.5, 0.5], 
        4: [-0.5, 0.0], 
        5: [0.0, 0.0], 
        6: [0.5, 0.0], 
        7: [0.0, -0.5]
    }
    pos_diff_dict = {
        c_i: np.sqrt(((np.array(pos_fact[c_i]) - np.array(pos_true[c_i])) ** 2).sum())
        for c_i in range(len(L))
    }
    pos_diff_mean = np.mean(list(pos_diff_dict.values()))
    assert pos_diff_mean < 1e-6, \
        f'layouts.multipartite_layout failed. Nodes position calculated wrongly.' + \
        f'Position differences: {pos_diff_dict}'


def test_layouts_dict():
    path = 'data/animal_movement.json'
    K = FormalContext.from_json(path)
    L = ConceptLattice.from_context(K)

    for x in ['multipartite']:
        pos = layouts.LAYOUTS[x](L)
