from .concept_lattice import ConceptLattice
from ..context import FormalContext
from ..utils.utils import powerset


def stability(c_i, lattice: ConceptLattice, context: FormalContext):
    c = lattice.concepts[c_i]

    n = 2 ** len(c.extent_i)
    if len(c.extent_i) > 0:
        x = 0
        for gs in powerset(c.extent_i):
            int_i = context.intention_i(gs)
            x += int(set(int_i) == set(c.intent_i))
        x /= n
    else:
        x = 1
    return x


def stability_bounds(c_i, lattice: ConceptLattice):
    c = lattice.concepts[c_i]
    dd_i = lattice.subconcepts_dict[c_i]
    inv_diff = [0]
    if len(dd_i) > 0:
        inv_diff = [2**(-len(set(c.extent_i)-set(lattice.concepts[d_i].extent_i))) for d_i in dd_i]

    lb = 1 - sum(inv_diff)
    ub = 1 - max(inv_diff)
    return lb, ub
