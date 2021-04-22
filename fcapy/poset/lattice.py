from fcapy.poset.poset import POSet


class UpperSemiLattice(POSet):
    def __init__(self, elements, leq_func, use_cache: bool = True):
        super(UpperSemiLattice, self).__init__(elements, leq_func, use_cache)

        if len(self.top_elements) != 1:
            raise ValueError(f"The set of ``elements`` should have a single top element")

        if use_cache:
            self._cache_top_element = None

    @property
    def top_element(self):
        if self._use_cache:
            if self._cache_top_element is None:
                self._cache_top_element = self.top_elements[0]
            top_element = self._cache_top_element
        else:
            top_element = self.top_elements[0]
        return top_element

    def add(self, element):
        is_smaller_than_top = self.leq_func(self._elements[self.top_element], element)
        is_bigger_than_top = self.leq_func(element, self._elements[self.top_element])

        if not (is_smaller_than_top or is_bigger_than_top):
            raise ValueError(f"New element {element} is incomparable with the top element of SemiLattice")
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
    def __init__(self, elements, leq_func, use_cache: bool = True):
        super(LowerSemiLattice, self).__init__(elements, leq_func, use_cache)

        if len(self.bottom_elements) != 1:
            raise ValueError(f"The set of ``elements`` should have a single bottom element")

        if use_cache:
            self._cache_bottom_element = None

    @property
    def bottom_element(self):
        if self._use_cache:
            if self._cache_bottom_element is None:
                self._cache_bottom_element = self.bottom_elements[0]
            bottom_element = self._cache_bottom_element
        else:
            bottom_element = self.bottom_elements[0]
        return bottom_element

    def add(self, element):
        is_smaller_than_bottom = self.leq_func(element, self._elements[self.bottom_element])
        is_bigger_than_bottom = self.leq_func(self._elements[self.bottom_element], element)

        if not (is_smaller_than_bottom or is_bigger_than_bottom):
            raise ValueError(f"New element {element} is incomparable with the bottom element of SemiLattice")
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
    def __init__(self, elements, leq_func, use_cache: bool = True):
        super(Lattice, self).__init__(elements, leq_func, use_cache)

        if len(self.top_elements) != 1:
            raise ValueError(f"The set of ``elements`` should have a single top element")
        if len(self.bottom_elements) != 1:
            raise ValueError(f"The set of ``elements`` should have a single bottom element")

        if use_cache:
            self._cache_top_element = None
            self._cache_bottom_element = None

    def add(self, element):
        is_smaller_than_top = self.leq_func(self._elements[self.top_element], element)
        is_bigger_than_top = self.leq_func(element, self._elements[self.top_element])

        if not (is_smaller_than_top or is_bigger_than_top):
            raise ValueError(f"New element {element} is incomparable with the top element of Lattice")

        is_smaller_than_bottom = self.leq_func(element, self._elements[self.bottom_element])
        is_bigger_than_bottom = self.leq_func(self._elements[self.bottom_element], element)

        if not (is_smaller_than_bottom or is_bigger_than_bottom):
            raise ValueError(f"New element {element} is incomparable with the bottom element of Lattice")
        super(Lattice, self).add(element)

        if self._use_cache:
            if is_smaller_than_bottom:
                self._cache_bottom_element = self._elements_to_index_map[element]
            if is_bigger_than_top:
                self._cache_top_element = self._elements_to_index_map[element]

    def remove(self, element):
        if self._elements[self.top_element] == element:
            raise ValueError(f"Cannot remove top element {element}")
        if self._elements[self.bottom_element] == element:
            raise ValueError(f"Cannot remove bottom element {element}")
        super(Lattice, self).remove(element)

    def __delitem__(self, key):
        if self.top_element == key:
            raise KeyError(f"Cannot delete top element {key}")
        if self.bottom_element == key:
            raise KeyError(f"Cannot delete bottom element {key}")
        super(Lattice, self).__delitem__(key)

        if self._use_cache:
            self._cache_top_element -= int(self._cache_top_element > key)
            self._cache_bottom_element -= int(self._cache_bottom_element > key)

