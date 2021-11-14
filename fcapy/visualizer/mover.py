from typing import Dict, Tuple

from attr import dataclass


@dataclass
class Mover:
    pos: Dict[int, Tuple[float, float]] = None
