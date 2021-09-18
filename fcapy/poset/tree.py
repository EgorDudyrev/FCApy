"""
The module provides BinaryTree class which represents a binary tree as a partial case of a poset.

"""
from fcapy.poset.lattice import UpperSemiLattice


class BinaryTree(UpperSemiLattice):
    def __init__(self, elements, leq_func, use_cache: bool = True, direct_subelements_dict=None):
        """Construct a BinaryTree based on a set of ``elements`` and ``leq_func`` defined on this set

        Parameters
        ----------
        elements : `list`
            A set of elements of BinaryTree of any kind
        leq_func : `function` (a,b)-> True of False
            A function to compare whether element ``a` from the BinaryTree is smaller than ``b`` or not
        use_cache : `bool`
            A flag whether to save for the output of leq_func and other computations in the cache or not
        direct_subelements_dict: `dict` of type {``element_i``: indexes of direct subelements of ``element_i``}
            (optional) A dictionary that contains the precomputed direct subelements relation
        """
        super(BinaryTree, self).__init__(elements, leq_func, use_cache, direct_subelements_dict)

        for el_i in range(len(self)):
            dsub_els_i = self.direct_sub_elements(el_i)
            if len(dsub_els_i) not in {0, 2}:
                raise ValueError('Given elements do not result in binary tree')

    def add(self, element, fill_up_cache=True):
        """Add an ``element`` to the BinaryTree only if it does not break the binary structure"""
        bottom_elements, _ = self.trace_element(element, 'down')
        if len(bottom_elements) >= 2:
            raise ValueError(f'Cannot add element {element} to BinaryTree. The binary structure will break')

        super(BinaryTree, self).add(element, fill_up_cache=fill_up_cache)
