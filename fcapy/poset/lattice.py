from fcapy.poset.poset import POSet


class UpperSemiLattice(POSet):
    def __init__(self, elements, leq_func, use_cache: bool = True):
        super(UpperSemiLattice, self).__init__(elements, leq_func, use_cache)

        if len(self.top_elements) != 1:
            raise ValueError(f"The set of ``elements`` should have a single top element")

    @property
    def top_element(self):
        return self.top_elements[0]

    def add(self, element):
        if not (self.leq_func(self._elements[self.top_element], element)
                or self.leq_func(element, self._elements[self.top_element])
        ):
            raise ValueError(f"New element {element} is incomparable with the top element of SemiLattice")
        super(UpperSemiLattice, self).add(element)
        
    def remove(self, element):
        if self._elements[self.top_element] == element:
            raise ValueError(f"Cannot remove top element {element}")
        super(UpperSemiLattice, self).remove(element)
        
    def __delitem__(self, key):
        if self.top_element == key:
            raise KeyError(f"Cannot remove top element {key}")
        super(UpperSemiLattice, self).__delitem__(key)


class LowerSemiLattice(POSet):
    def __init__(self, elements, leq_func, use_cache: bool = True):
        super(LowerSemiLattice, self).__init__(elements, leq_func, use_cache)

        if len(self.bottom_elements) != 1:
            raise ValueError(f"The set of ``elements`` should have a single bottom element")

    @property
    def bottom_element(self):
        return self.bottom_elements[0]

    def add(self, element):
        if not (self.leq_func(self._elements[self.bottom_element], element)
                or self.leq_func(element, self._elements[self.bottom_element])
        ):
            raise ValueError(f"New element {element} is incomparable with the bottom element of SemiLattice")
        super(LowerSemiLattice, self).add(element)

    def remove(self, element):
        if self._elements[self.bottom_element] == element:
            raise ValueError(f"Cannot remove bottom element {element}")
        super(LowerSemiLattice, self).remove(element)

    def __delitem__(self, key):
        if self.bottom_element == key:
            raise KeyError(f"Cannot delete bottom element {key}")
        super(LowerSemiLattice, self).__delitem__(key)


class Lattice(UpperSemiLattice, LowerSemiLattice):
    def __init__(self, elements, leq_func, use_cache: bool = True):
        super(Lattice, self).__init__(elements, leq_func, use_cache)

        if len(self.top_elements) != 1:
            raise ValueError(f"The set of ``elements`` should have a single top element")
        if len(self.bottom_elements) != 1:
            raise ValueError(f"The set of ``elements`` should have a single bottom element")

    def add(self, element):
        if not (self.leq_func(self._elements[self.top_element], element)
                or self.leq_func(element, self._elements[self.top_element])
        ):
            raise ValueError(f"New element {element} is incomparable with the top element of Lattice")
        if not (self.leq_func(self._elements[self.bottom_element], element)
                or self.leq_func(element, self._elements[self.bottom_element])
        ):
            raise ValueError(f"New element {element} is incomparable with the bottom element of Lattice")
        super(Lattice, self).add(element)

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

