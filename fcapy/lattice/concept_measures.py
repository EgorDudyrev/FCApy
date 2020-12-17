from .concept_lattice import  ConceptLattice
from ..context import FormalContext
from ..utils.utils import powerset


def stability(c_i, lattice: ConceptLattice, context: FormalContext):
    c = lattice.concepts[c_i]
    x = 0
    n = 2 ** len(c.extent_i)
    for gs in powerset(c.extent_i):
        int_i = context.intention_i(gs)
        x += int(set(int_i) == set(c.intent_i))
    x /= n
    return x
