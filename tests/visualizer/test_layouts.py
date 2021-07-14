from fcapy.context import FormalContext
from fcapy.lattice import ConceptLattice
from fcapy.visualizer import layouts

import numpy as np


def test_multipartite_layout():
    path = 'data/animal_movement.json'
    K = FormalContext.read_json(path)
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
    path = 'data/mango_bin.csv'
    K = FormalContext.read_csv(path)
    L = ConceptLattice.from_context(K)

    pos_fact = layouts.fcart_layout(L)
    
    pos_true = {0: [0.0, 1.0], 1: [-0.7142857142857143, 0.6666666666666667], 2: [-0.4285714285714286, 0.6666666666666667], 3: [-0.1428571428571429, 0.6666666666666667], 4: [0.1428571428571428, 0.6666666666666667], 5: [-0.75, 0.33333333333333337], 6: [-0.5, 0.33333333333333337], 7: [0.4285714285714286, 0.6666666666666667], 8: [0.0, 0.33333333333333337], 9: [0.25, 0.33333333333333337], 10: [-0.6666666666666667, 0.0], 11: [-0.33333333333333337, 0.0], 12: [-0.25, 0.33333333333333337], 13: [0.5, 0.33333333333333337], 14: [0.7142857142857142, 0.6666666666666667], 15: [0.33333333333333326, 0.0], 16: [0.33333333333333326, -0.33333333333333326], 17: [0.6666666666666667, 0.0], 18: [0.0, 0.0], 19: [0.75, 0.33333333333333337], 20: [-0.33333333333333337, -0.33333333333333326], 21: [0.0, -0.6666666666666667]}
    
    pos_diff_dict = {
        c_i: np.sqrt(((np.array(pos_fact[c_i]) - np.array(pos_true[c_i])) ** 2).sum())
        for c_i in range(len(L))
    }
    pos_diff_mean = np.mean(list(pos_diff_dict.values()))
    assert pos_diff_mean < 1e-6, \
        f'layouts.fcart_layout failed. Nodes position calculated wrongly.' + \
        f'Position differences: {pos_diff_dict}'
    
    pos_fact = layouts.fcart_layout(L, c=1, dpth=2)
    
    pos_true = {0: [0.0, 1.0], 1: [-0.7142857142857143, 0.6666666666666667], 2: [-0.4285714285714286, 0.6666666666666667], 3: [-0.1428571428571429, 0.6666666666666667], 4: [0.1428571428571428, 0.6666666666666667], 5: [-0.75, 0.33333333333333337], 6: [-0.5, 0.33333333333333337], 7: [0.4285714285714286, 0.6666666666666667], 8: [0.0, 0.33333333333333337], 9: [0.25, 0.33333333333333337], 10: [0.0, 0.0], 11: [-0.6666666666666667, 0.0], 12: [-0.25, 0.33333333333333337], 13: [0.5, 0.33333333333333337], 14: [0.7142857142857142, 0.6666666666666667], 15: [-0.33333333333333337, 0.0], 16: [-0.33333333333333337, -0.33333333333333326], 17: [0.33333333333333326, 0.0], 18: [0.6666666666666667, 0.0], 19: [0.75, 0.33333333333333337], 20: [0.33333333333333326, -0.33333333333333326], 21: [0.0, -0.6666666666666667]}
    
    pos_diff_dict = {
        c_i: np.sqrt(((np.array(pos_fact[c_i]) - np.array(pos_true[c_i])) ** 2).sum())
        for c_i in range(len(L))
    }
    pos_diff_mean = np.mean(list(pos_diff_dict.values()))
    assert pos_diff_mean < 1e-6, \
            f'layouts.fcart _layout failed. Nodes position calculated wrongly while changing parameters.' + \
        f'Position differences: {pos_diff_dict}'


def test_layouts_dict():
    path = 'data/animal_movement.json'
    K = FormalContext.read_json(path)
    L = ConceptLattice.from_context(K)

    for x in ['multipartite', 'fcart']:
        pos = layouts.LAYOUTS[x](L)
