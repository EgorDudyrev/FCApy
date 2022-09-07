"""
This subpackage contains all the complex algorithms of the package.

Modules:
--------
  concept_construction:
    This module contains a number of functions which take a `FormalContext` (or `MVContext`)
    and return a set of formal (or pattern) concepts.
    Some of them return a `ConceptLattice` instead of just a set of concepts
  lattice_construction:
    This module contains a number of function which take a set of formal (or pattern) concepts
    and return its children_dict
    i.e. the order of given concepts in the form {`parent_concept_index`: `child_concept_index`}.
    Parent_concept is a concept which is bigger (or more general) than the child concept
    and there is no other concept between these two.

"""