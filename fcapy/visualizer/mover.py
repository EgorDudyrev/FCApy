from typing import Dict, Tuple, List, Optional

from attr import dataclass

from fcapy.poset import POSet
from fcapy.visualizer.hasse_layouts import LAYOUTS
from fcapy.utils.utils import get_kwargs_used

PosDictType = Dict[int, Tuple[float, float]]


@dataclass
class DifferentHierarchyLevelsError(ValueError):
    el_a: int
    el_b: int
    operation_name: str = ''

    def __str__(self):
        msg = '\n'.join([
            f"Elements {self.el_a} and {self.el_b} are on the different hierarchy levels.",
            f"Thus the operation{' '+self.operation_name} cannot be performed",
        ])
        return msg


class Mover:
    """Class to make node moving in Hasse Diagrams easier

    Methods
    -------
    pos: get/set nodes position in {element_idx: (x_coord, y_coord)} format

    Attributes
    ----------
    levels: Position of each node in level hierarchy (0 = Top element, 1,2,3,... lower levels)
    peers_order: Position of each node inside a level (i = The i-th element)

    pos_levels: Float coordinate of each level
    pos_peers: Float coordinate of each peer by level
    """
    levels: Optional[List[Optional[int]]]
    peers_order: Optional[List[Optional[int]]]

    pos_levels: Optional[List[float]]
    pos_peers: Optional[List[List[float]]]

    def __init__(self, pos: PosDictType = None):
        self.pos = pos

    @property
    def pos(self) -> Optional[PosDictType]:
        if self.levels is None:
            return None

        return {el_i: (self.pos_peers[lvl][peer], self.pos_levels[lvl])
                for el_i, (lvl, peer) in enumerate(zip(self.levels, self.peers_order))}

    @pos.setter
    def pos(self, value: PosDictType):
        if value is None:
            self.levels = None
            self.peers_order = None
            self.pos_levels = None
            self.pos_peers = None
            return

        max_el_i = max(value)
        lvl_coords = sorted(set([value[el_i][1] if el_i in value else None for el_i in range(max_el_i + 1)]),
                            reverse=True)
        lvl_coords_inv_dct = {coord: lvl_i for lvl_i, coord in enumerate(lvl_coords)}
        levels = [lvl_coords_inv_dct[value[el_i][1]] if el_i in value else None for el_i in range(max_el_i + 1)]

        peers_order = [[] for _ in range(len(lvl_coords))]
        for el_i, lvl in enumerate(levels):
            peers_order[lvl].append(el_i)
        peers_order = [sorted(peers, key=lambda el_i: value[el_i][0]) for peers in peers_order]
        pos_peers = [[value[el_i][0] for el_i in peers] for peers in peers_order]

        peers_order_flat = [peers_order[lvl].index(el_i) if lvl is not None else None
                            for el_i, lvl in enumerate(levels)]

        self.levels = levels
        self.peers_order = peers_order_flat
        self.pos_levels = lvl_coords
        self.pos_peers = pos_peers

    def initialize_pos(self, poset: POSet, layout='fcart', **kwargs) -> None:
        """Return a dict of nodes float positions in a line diagram"""
        if layout not in LAYOUTS:
            raise ValueError(
                f'Layout "{layout}" is not supported. '
                f'Possible layouts are: {", ".join(LAYOUTS.keys())}'
            )
        layout_func = LAYOUTS[layout]
        kwargs_used = get_kwargs_used(kwargs, layout_func)
        self.pos = layout_func(poset, **kwargs_used)

    def swap_nodes(self, el_a: int, el_b: int) -> None:
        lvl_a, lvl_b = [self.levels[el] for el in [el_a, el_b]]
        if lvl_a is None or lvl_b is None or lvl_a != lvl_b:
            raise DifferentHierarchyLevelsError(el_a, el_b, "'swap_nodes'")

        self.peers_order[el_a], self.peers_order[el_b] = self.peers_order[el_b], self.peers_order[el_a]

    def shift_node(self, node_i: int, n_nodes_right: int) -> None:
        node_lvl, node_peer_id = self.levels[node_i], self.peers_order[node_i]

        peers_ids = [i for i, lvl in enumerate(self.levels) if lvl == node_lvl]
        peers_ids = sorted(peers_ids, key=lambda i: self.peers_order[i])

        nodes_to_swap = peers_ids[node_peer_id+1:] if n_nodes_right >= 0 else peers_ids[:node_peer_id][::-1]
        nodes_to_swap = nodes_to_swap[:abs(n_nodes_right)]

        for node_swap in nodes_to_swap:
            self.swap_nodes(node_i, node_swap)

    def jitter_node(self, node_i: int, dx: float) -> None:
        lvl_id, peer_id = self.levels[node_i], self.peers_order[node_i]
        pos_peers = self.pos_peers[lvl_id]

        new_x = pos_peers[peer_id] + dx

        is_on_border = peer_id == len(pos_peers) - 1 if dx >= 0 else peer_id == 0
        if is_on_border:
            pos_peers[peer_id] = new_x
            return

        is_preserving_order = new_x < pos_peers[peer_id + 1] if dx >= 0 else new_x > pos_peers[peer_id - 1]
        if is_preserving_order:
            pos_peers[peer_id] = new_x
            return

        # if shifts with other nodes
        if any([x == new_x for x in pos_peers]):
            raise AssertionError("New node position overlaps another node")  # TODO: Determine the overlapping node

        if dx >= 0:
            n_nodes_to_shift = len([x for x in pos_peers[peer_id+1:] if x < new_x])
        else:
            n_nodes_to_shift = -len([x for x in pos_peers[:peer_id] if x > new_x])

        self.shift_node(node_i, n_nodes_to_shift)

        peer_id = self.peers_order[node_i]
        self.pos_peers[lvl_id][peer_id] = new_x
