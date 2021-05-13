from fcapy.poset.lattice import UpperSemiLattice


class BinaryTree(UpperSemiLattice):
    def __init__(self, elements, leq_func, use_cache: bool = True):
        super(BinaryTree, self).__init__(elements, leq_func, use_cache)

        for el_i in range(len(self)):
            dsub_els_i = self.direct_sub_elements(el_i)
            if len(dsub_els_i) not in {0, 2}:
                raise ValueError('Given elements do not result in binary tree')

    def add(self, element, fill_up_cache=True):
        bottom_elements, _ = self.trace_element(element, 'down')
        if len(bottom_elements) >= 2:
            raise ValueError(f'Cannot add element {element} to BinaryTree. The binary structure will break')

        super(BinaryTree, self).add(element, fill_up_cache=fill_up_cache)
