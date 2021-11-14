from typing import Dict, Tuple

from attr import dataclass

from fcapy.poset import POSet
from fcapy.visualizer.hasse_layouts import LAYOUTS
from fcapy.utils.utils import get_kwargs_used

PosDictType = Dict[int, Tuple[float, float]]


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
