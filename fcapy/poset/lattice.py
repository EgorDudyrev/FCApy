from fcapy.poset.poset import POSet


class UpperSemiLattice(POSet):
    """A class to represent Join (or Upper) Semilattice

    A join (or upper) semilattice is a POSet with a single top (join) element
    """
    CLASS_NAME = 'SemiLattice'

    def __init__(self, elements, leq_func, use_cache: bool = True, direct_subelements_dict=None):
        """Construct an UpperSemiLattice based on a set of ``elements`` and ``leq_func`` defined on this set

        Parameters
        ----------
        elements : `list`
            A set of elements of semillatice of any kind
        leq_func : `function` (a,b)-> True of False
            A function to compare whether element ``a` from the semillatice is smaller than ``b`` or not
        use_cache : `bool`
            (optional) A flag whether to save for the output of leq_func and other computations in the cache or not
        direct_subelements_dict: `dict` of type {``element_i``: indexes of direct subelements of ``element_i``}
            (optional) A dictionary that contains the precomputed direct subelements relation
        """
        if len(elements) == 0:
            raise ValueError(f'{self.CLASS_NAME} cannot be constructed upon zero elements')
        super(UpperSemiLattice, self).__init__(elements, leq_func, use_cache, direct_subelements_dict)

        top_elements = super(UpperSemiLattice, self).top_elements
        if len(top_elements) != 1:
            raise ValueError(f"The set of ``elements`` should have a single top element")

        if use_cache:
            self._cache_top_element = top_elements[0]

    @property
    def top_element(self):
        """An index of the single top (the biggest) element of the semilattice"""
        if self._use_cache:
            if self._cache_top_element is None:
                self._cache_top_element = super(UpperSemiLattice, self).top_elements[0]
            top_element = self._cache_top_element
        else:
            top_element = super(UpperSemiLattice, self).top_elements[0]
        return top_element

    @property
    def top_elements(self):
        """The set of indexes of the top (the biggest) elements of the semilattice"""
        return [self.top_element]

    def add(self, element, fill_up_cache=True):
        """Add an ``element`` to semilattice. Automatically fill up the comparison caches if needed"""
        is_smaller_than_top = self.leq_func(element, self._elements[self.top_element])
        is_bigger_than_top = self.leq_func(self._elements[self.top_element], element)

        if not (is_smaller_than_top or is_bigger_than_top):
            raise ValueError(f"New element {element} is incomparable with the top element of {self.CLASS_NAME}")
        super(UpperSemiLattice, self).add(element, fill_up_cache)

        if self._use_cache:
            if is_bigger_than_top:
                self._cache_top_element = self._elements_to_index_map[element]
        
    def remove(self, element):
        """Remove and ``element`` from the semilattice"""
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
    """A class to represent Meet (or Lower) Semilattice

    A meet (or lower) semilattice is a POSet with a single bottom (meet) element
    """
    CLASS_NAME = 'SemiLattice'

    def __init__(self, elements, leq_func, use_cache: bool = True, direct_subelements_dict=None):
        """Construct a LowerSemiLattice based on a set of ``elements`` and ``leq_func`` defined on this set

        Parameters
        ----------
        elements : `list`
            A set of elements of semillatice of any kind
        leq_func : `function` (a,b)-> True of False
            A function to compare whether element ``a` from the semillatice is smaller than ``b`` or not
        use_cache : `bool`
            A flag whether to save for the output of leq_func and other computations in the cache or not
        direct_subelements_dict: `dict` of type {``element_i``: indexes of direct subelements of ``element_i``}
            (optional) A dictionary that contains the precomputed direct subelements relation
        """
        if len(elements) == 0:
            raise ValueError(f'{self.CLASS_NAME} cannot be constructed upon zero elements')
        super(LowerSemiLattice, self).__init__(elements, leq_func, use_cache, direct_subelements_dict)

        bottom_elements = super(LowerSemiLattice, self).bottom_elements
        if len(bottom_elements) != 1:
            raise ValueError(f"The set of ``elements`` should have a single bottom element")

        if use_cache:
            self._cache_bottom_element = bottom_elements[0]

    @property
    def bottom_element(self):
        """An index of the bottom (the smallest) element of a semilattice"""
        if self._use_cache:
            if self._cache_bottom_element is None:
                self._cache_bottom_element = super(LowerSemiLattice, self).bottom_elements[0]
            bottom_element = self._cache_bottom_element
        else:
            bottom_element = super(LowerSemiLattice, self).bottom_elements[0]
        return bottom_element

    @property
    def bottom_elements(self):
        """A list of indexes of the bottom (the smallest) elements of a semilattice"""
        return [self.bottom_element]

    def add(self, element, fill_up_cache=True):
        """Add an ``element`` to semilattice. Automatically fill up the comparison caches if needed"""
        is_smaller_than_bottom = self.leq_func(element, self._elements[self.bottom_element])
        is_bigger_than_bottom = self.leq_func(self._elements[self.bottom_element], element)

        if not (is_smaller_than_bottom or is_bigger_than_bottom):
            raise ValueError(f"New element {element} is incomparable with the bottom element of {self.CLASS_NAME}")
        super(LowerSemiLattice, self).add(element, fill_up_cache)

        if self._use_cache:
            if is_smaller_than_bottom:
                self._cache_bottom_element = self._elements_to_index_map[element]

    def remove(self, element):
        """Remove and ``element`` from the semilattice"""
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
    """A class to represent a Lattice

    A lattice is a POSet with a single top (the biggest) and a single bottom (the smallest) elements
    """
    CLASS_NAME = 'Lattice'
