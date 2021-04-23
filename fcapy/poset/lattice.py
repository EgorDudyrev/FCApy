from fcapy.poset.poset import POSet


class UpperSemiLattice(POSet):
    CLASS_NAME = 'SemiLattice'

    def __init__(self, elements, leq_func, use_cache: bool = True):
        if len(elements) == 0:
            raise ValueError(f'{self.CLASS_NAME} cannot be constructed upon zero elements')
        super(UpperSemiLattice, self).__init__(elements, leq_func, use_cache)

        top_elements = super(UpperSemiLattice, self).top_elements
        if len(top_elements) != 1:
            raise ValueError(f"The set of ``elements`` should have a single top element")

        if use_cache:
            self._cache_top_element = top_elements[0]

    @property
    def top_element(self):
        if self._use_cache:
            if self._cache_top_element is None:
                self._cache_top_element = super(UpperSemiLattice, self).top_elements[0]
            top_element = self._cache_top_element
        else:
            top_element = super(UpperSemiLattice, self).top_elements[0]
        return top_element

    @property
    def top_elements(self):
        return [self.top_element]

    def add(self, element):
        is_smaller_than_top = self.leq_func(self._elements[self.top_element], element)
        is_bigger_than_top = self.leq_func(element, self._elements[self.top_element])

        if not (is_smaller_than_top or is_bigger_than_top):
            raise ValueError(f"New element {element} is incomparable with the top element of {self.CLASS_NAME}")
        super(UpperSemiLattice, self).add(element)

        if self._use_cache:
            if is_bigger_than_top:
                self._cache_top_element = self._elements_to_index_map[element]
        
    def remove(self, element):
        if self._elements[self.top_element] == element:
            raise ValueError(f"Cannot remove top element {element}")
        super(UpperSemiLattice, self).remove(element)
        
    def __delitem__(self, key):
        if self.top_element == key:
            raise KeyError(f"Cannot remove top element {key}")
        super(UpperSemiLattice, self).__delitem__(key)

        if self._use_cache:
            self._cache_top_element -= int(self._cache_top_element > key)


class LowerSemiLattice(POSet):
    CLASS_NAME = 'SemiLattice'

    def __init__(self, elements, leq_func, use_cache: bool = True):
        if len(elements) == 0:
            raise ValueError(f'{self.CLASS_NAME} cannot be constructed upon zero elements')
        super(LowerSemiLattice, self).__init__(elements, leq_func, use_cache)

        bottom_elements = super(LowerSemiLattice, self).bottom_elements
        if len(bottom_elements) != 1:
            raise ValueError(f"The set of ``elements`` should have a single bottom element")

        if use_cache:
            self._cache_bottom_element = bottom_elements[0]

    @property
    def bottom_element(self):
        if self._use_cache:
            if self._cache_bottom_element is None:
                self._cache_bottom_element = super(LowerSemiLattice, self).bottom_elements[0]
            bottom_element = self._cache_bottom_element
        else:
            bottom_element = super(LowerSemiLattice, self).bottom_elements[0]
        return bottom_element

    @property
    def bottom_elements(self):
        return [self.bottom_element]

    def add(self, element):
        is_smaller_than_bottom = self.leq_func(element, self._elements[self.bottom_element])
        is_bigger_than_bottom = self.leq_func(self._elements[self.bottom_element], element)

        if not (is_smaller_than_bottom or is_bigger_than_bottom):
            raise ValueError(f"New element {element} is incomparable with the bottom element of {self.CLASS_NAME}")
        super(LowerSemiLattice, self).add(element)

        if self._use_cache:
            if is_smaller_than_bottom:
                self._cache_bottom_element = self._elements_to_index_map[element]

    def remove(self, element):
        if self._elements[self.bottom_element] == element:
            raise ValueError(f"Cannot remove bottom element {element}")
        super(LowerSemiLattice, self).remove(element)

    def __delitem__(self, key):
        if self.bottom_element == key:
            raise KeyError(f"Cannot delete bottom element {key}")
        super(LowerSemiLattice, self).__delitem__(key)

        if self._use_cache:
            self._cache_bottom_element -= int(self._cache_bottom_element > key)


class Lattice(UpperSemiLattice, LowerSemiLattice):
    CLASS_NAME = 'Lattice'
