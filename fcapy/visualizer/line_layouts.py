"""
This module provides a set of functions to derive a layout (node positions) for a given POSet

"""
from typing import Dict, Tuple, FrozenSet

import networkx as nx
from frozendict import frozendict

from fcapy.poset import POSet


def calc_levels(poset: POSet):
    """Return levels (y position) of nodes and dict with {`level`: `nodes`} mapping in a line diagram"""
    dsups_dict = poset.parents_dict

    levels = [-1] * len(poset)
    top_els = set(poset.tops)
    nodes_to_visit = list(top_els)

    while len(nodes_to_visit) > 0:
        node_id = nodes_to_visit.pop(0)

        levels[node_id] = max([levels[dsup_id] for dsup_id in dsups_dict[node_id]])+1 if node_id not in top_els else 0

        nodes_to_visit += [n_i for n_i in poset.children(node_id)
                           if levels[n_i] == -1 and all([levels[dsup_id] >= 0 for dsup_id in dsups_dict[n_i]])]

    levels_dict = {i: [] for i in range(max(levels) + 1)}
    for c_i in range(len(poset)):
        levels_dict[levels[c_i]].append(c_i)
    return levels, levels_dict


def multipartite_layout(poset):
    """A basic layout generated by networkx.multipartite_layout function"""
    c_levels, levels_dict = calc_levels(poset)
    G = poset.to_networkx('down')
    nx.set_node_attributes(G, dict(enumerate(c_levels)), 'level')
    pos = nx.multipartite_layout(G, subset_key='level', align='horizontal')
    pos = {c_i: [p[0], -p[1]] for c_i, p in pos.items()}
    return pos


def fcart_layout(poset, c=0.5, dpth=1):
    """Get a `POSet` elements positioning on [-1; 1]x[-1; 1] plane

    Parameters
    ----------
    poset: `POSet`
        A partially ordered set to visualize
    с: `float`
        Parameter showing how much upper layers affect node positioning 
        (if c < 1, the higher the layer, the less it affects node positioning)
    dpth: `int`
        Parameter showing how many upper layers affect node positioning

    Returns
    -------
    pos: `dict` of type {`int` : [`float`, `float`]}
        maps `POSet` elements id to (x, y) coordinates on [-1; 1]x[-1; 1] plane

    """
    c_levels, levels_dict = calc_levels(poset)
    id_on_lvl = [0] * len(poset)

    for lvl, elems in levels_dict.items():
        if lvl != 0:
            priority = []
            for elem in elems:
                mp = 0
                for par in poset.parents(elem):
                    if c_levels[elem] - c_levels[par] <= dpth:
                        mp += c ** (c_levels[elem] - c_levels[par] - 1) * id_on_lvl[par] / len(levels_dict[c_levels[par]])
                priority += [mp / len(poset.parents(elem))]
            elems = [x for _, x in sorted(zip(priority, elems))]
        for i, elem in enumerate(elems):
            id_on_lvl[elem] = i;

    x_pos = [2 * (id_on_lvl[i] + 1) / (len(levels_dict[c_levels[i]]) + 1) - 1 for i in range(len(c_levels))]
    y_pos = [-2 * c_levels[i] / len(levels_dict) + 1 for i in range(len(c_levels))]

    pos = {i : [x_pos[i], y_pos[i]] for i in range(len(c_levels))}
    return pos


LAYOUTS = frozendict({
    'multipartite': multipartite_layout,
    'fcart': fcart_layout,
})


def find_nodes_edges_overlay(
        pos: Dict[int, Tuple[float, float]],
        nodes: Tuple[int, ...],
        edges: Tuple[Tuple[int, int], ...]
) -> Dict[Tuple[int, int], FrozenSet[int]]:
    def dist(a_pos, b_pos):
        return ((a_pos[0] - b_pos[0]) ** 2 + (a_pos[1] - b_pos[1]) ** 2)**0.5

    def test_is_on_line(a_pos, b_pos, v_pos) -> bool:
        if not b_pos[1] <= v_pos[1] <= a_pos[1]:  # Since b_pos[1] always <= a_pos[1] due to line diagram nature
            return False

        if not (a_pos[0] <= v_pos[0] <= b_pos[0] or b_pos[0] <= v_pos[0] <= a_pos[0]):
            return False

        dist_ab = dist(a_pos, b_pos)
        dist_av = dist(a_pos, v_pos)
        dist_vb = dist(v_pos, b_pos)
        if (dist_av + dist_vb) - dist_ab > 1e-6:
            return False

        return True

    overlays = {
        edge: {v_idx for v_idx in nodes
               if v_idx not in edge and test_is_on_line(pos[edge[0]], pos[edge[1]], pos[v_idx])}
        for edge in edges
    }

    overlays = {edge: frozenset(overs) for edge, overs in overlays.items() if len(overs) > 0}
    return overlays
