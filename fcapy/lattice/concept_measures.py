"""
This module provides a set of functions to compute interestingness measures of elements

For the definition of interestingness measures look the paper:

Kuznetsov, Sergei & Makhalova, Tatiana. (2016). On interestingness measures of formal elements.
Information Sciences. 442. 10.1016/j.ins.2018.02.032.


For the definition of stability and its bounds look the paper:

Buzmakov, Aleksey & Kuznetsov, Sergei & Napoli, Amedeo. (2014). Scalable Estimates of Concept Stability.
8478. 10.1007/978-3-319-07248-7_12.

"""

from fcapy.lattice.concept_lattice import ConceptLattice
from fcapy.context.formal_context import FormalContext
from fcapy.utils.utils import powerset

from fcapy import LIB_INSTALLED
if LIB_INSTALLED['numpy']:
    import numpy as np


def stability(c_i, lattice: ConceptLattice, context: FormalContext):
    """Compute the exact stability of the concept number ``c_i`` of a ``lattice`` constructed over ``context``

    Exact but exponential time to compute measure
    """
    c = lattice[c_i]

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
    """Compute the lower and upper stability of the concept number ``c_i`` of a ``lattice`` constructed over ``context``

    Approximate but polynomial time to compute measure of concept stability
    """
    c = lattice[c_i]
    inv_diff = [0]

    children_i = lattice.children(c_i)
    if len(children_i) > 0:
        inv_diff = [2 ** (-len(set(c.extent_i) - set(lattice[child_i].extent_i))) for child_i in children_i]

    lb = 1 - sum(inv_diff)
    ub = 1 - max(inv_diff)
    return lb, ub


def target_entropy(c_i, lattice: ConceptLattice, context: FormalContext):
    """Compute the entropy of target labels of objects from concept extent"""
    target_ext = context.target[list(lattice[c_i].extent_i)]
    return np.var(target_ext)


def mean_information_gain(c_i, lattice: ConceptLattice):
    h = lattice[c_i].measures['target_entropy']
    mean_parent_h = np.mean(lattice.measures['target_entropy'][lattice.ancestors(c_i)])
    return mean_parent_h - h
