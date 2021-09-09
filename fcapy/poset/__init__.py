"""
This subpackage provides a class POSet to work with Partially Ordered Set object from Ordered Sets theory.

The subpackage is created to encapsulate the order functions of ConceptLattice class

Classes
-------
poset.POSet:
    A class that implement a partially ordered set
lattice.UpperSemilattice:
    A class that implements an upper semilattice: POSet with the greatest element
lattice.LowerSemilattice:
    A class that implements a lower semilattices: POSet with the smallest element
lattice.Lattice:
    A class that implements a lattice: POSet with both the greatest and the smallest element
tree.BinaryTree:
    A class that implements

Modules
-------
concept_lattice:
    This module provides the ConceptLattice class
concept_measures:
    This module provides a set of functions to compute interestingness measures of concepts
formal_concept:
    This module provides the FormalConcept class
pattern_concept:
    This module provides the PatternConcept class

"""

from .poset import POSet
from .lattice import UpperSemiLattice, LowerSemiLattice, Lattice
from .tree import BinaryTree
