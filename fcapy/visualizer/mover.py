from typing import Dict, Tuple

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


@dataclass
class Mover:
    pos: PosDictType = None

    def initialize_pos(self, poset: POSet, layout='fcart', **kwargs) -> None:
        """Return a dict of nodes positions in a line diagram"""
        if layout not in LAYOUTS:
            raise ValueError(
                f'Layout "{layout}" is not supported. '
                f'Possible layouts are: {", ".join(LAYOUTS.keys())}'
            )
        layout_func = LAYOUTS[layout]
        kwargs_used = get_kwargs_used(kwargs, layout_func)
        self.pos = layout_func(poset, **kwargs_used)

    def swap_nodes(self, el_a: int, el_b: int) -> None:
        if self.pos[el_a][1] != self.pos[el_b][1]:
            raise DifferentHierarchyLevelsError(el_a, el_b, "'swap_nodes'")

        self.pos[el_a], self.pos[el_b] = self.pos[el_b], self.pos[el_a]
