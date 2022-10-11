"""
The module provides a lattice object from Order theory and its upper/lower semilattices.

An upper semilattice is a poset that contains a single top (join) element.
A lower semilattice is a poset  that contains a single bottom (meet) element.
A lattice contains both a single top and a single bottom elements.

"""
from typing import List, Callable, Any, Dict, Tuple, Collection

from fcapy.poset.poset import POSet


class UpperSemiLattice(POSet):
    """A class to represent Join (or Upper) Semilattice

    A join (or upper) semilattice is a POSet with a single top (join) element
    """
    CLASS_NAME = 'SemiLattice'

    def __init__(
            self,
            elements: Collection[Any],
            leq_func: Callable[[Any, Any], bool] = lambda a, b: a <= b,
            use_cache: bool = True, children_dict: Dict[int, Tuple[int, ...]] = None
    ):
        """Construct an UpperSemiLattice based on a set of ``elements`` and ``leq_func`` defined on this set

        Parameters
        ----------
        elements : `list`
            A set of elements of semillatice of any kind
        leq_func : `function` (a,b)-> True of False
            A function to compare whether element ``a` from the semillatice is smaller than ``b`` or not
        use_cache : `bool`
            (optional) A flag whether to save for the output of leq_func and other computations in the cache or not
        children_dict: `dict` of type {``element_i``: indexes of the biggest elements smaller than ``element_i``}
            (optional) A dictionary that contains the precomputed children relation
        """
        if len(elements) == 0:
            raise ValueError(f'{self.CLASS_NAME} cannot be constructed upon zero elements')
        super(UpperSemiLattice, self).__init__(elements, leq_func, use_cache, children_dict)

        top_elements = super(UpperSemiLattice, self).tops
        if len(top_elements) != 1:
            raise ValueError(f"The set of ``elements`` should have a single top element")

        if use_cache:
            self._cache_top = top_elements[0]

    @property
    def top(self) -> int:
        """An index of the single top (the biggest) element of the semilattice"""
        if self._use_cache:
            if self._cache_top is None:
                self._cache_top = super(UpperSemiLattice, self).tops[0]
            top_element = self._cache_top
        else:
            top_element = super(UpperSemiLattice, self).tops[0]
        return top_element

    @property
    def tops(self) -> List[int]:
        """The set of indexes of the top (the biggest) elements of the semilattice"""
        return [self.top]

    def add(self, element: Any, fill_up_cache: bool = True):
        """Add an ``element`` to semilattice. Automatically fill up the comparison caches if needed"""
        is_smaller_than_top = self.leq_func(element, self._elements[self.top])
        is_bigger_than_top = self.leq_func(self._elements[self.top], element)

        if not (is_smaller_than_top or is_bigger_than_top):
            raise ValueError(f"New element {element} is incomparable with the top element of {self.CLASS_NAME}")
        super(UpperSemiLattice, self).add(element, fill_up_cache)

        if self._use_cache:
            if is_bigger_than_top:
                self._cache_top = self._elements_to_index_map[element]
        
    def remove(self, element: Any):
        """Remove and ``element`` from the semilattice"""
        if self._elements[self.top] == element:
            raise ValueError(f"Cannot remove top element {element}")
        super(UpperSemiLattice, self).remove(element)
        
    def __delitem__(self, key: int):
        if self.top == key:
            raise KeyError(f"Cannot remove top element {key}")
        super(UpperSemiLattice, self).__delitem__(key)

        if self._use_cache:
            self._cache_top -= int(self._cache_top > key)


class LowerSemiLattice(POSet):
    """A class to represent Meet (or Lower) Semilattice

    A meet (or lower) semilattice is a POSet with a single bottom (meet) element
    """
    CLASS_NAME = 'SemiLattice'

    def __init__(
            self, elements: Collection[Any],
            leq_func: Callable[[Any, Any], bool] = lambda a, b: a <= b,
            use_cache: bool = True, children_dict: Dict[int, Tuple[int, ...]] = None
    ):
        """Construct a LowerSemiLattice based on a set of ``elements`` and ``leq_func`` defined on this set

        Parameters
        ----------
        elements : `list`
            A set of elements of semillatice of any kind
        leq_func : `function` (a,b)-> True of False
            A function to compare whether element ``a` from the semillatice is smaller than ``b`` or not
        use_cache : `bool`
            A flag whether to save for the output of leq_func and other computations in the cache or not
        children_dict: `dict` of type {``element_i``: indexes of direct subelements of ``element_i``}
            (optional) A dictionary that contains the precomputed direct subelements relation
        """
        if len(elements) == 0:
            raise ValueError(f'{self.CLASS_NAME} cannot be constructed upon zero elements')
        super(LowerSemiLattice, self).__init__(elements, leq_func, use_cache, children_dict)

        bottom_elements = super(LowerSemiLattice, self).bottoms
        if len(bottom_elements) != 1:
            raise ValueError(f"The set of ``elements`` should have a single bottom element")

        if use_cache:
            self._cache_bottom = bottom_elements[0]

    @property
    def bottom(self) -> int:
        """An index of the bottom (the smallest) element of a semilattice"""
        if self._use_cache:
            if self._cache_bottom is None:
                self._cache_bottom = super(LowerSemiLattice, self).bottoms[0]
            bottom_element = self._cache_bottom
        else:
            bottom_element = super(LowerSemiLattice, self).bottoms[0]
        return bottom_element

    @property
    def bottoms(self) -> List[int]:
        """A list of indexes of the bottom (the smallest) elements of a semilattice"""
        return [self.bottom]

    def add(self, element: Any, fill_up_cache: bool = True):
        """Add an ``element`` to semilattice. Automatically fill up the comparison caches if needed"""
        is_smaller_than_bottom = self.leq_func(element, self._elements[self.bottom])
        is_bigger_than_bottom = self.leq_func(self._elements[self.bottom], element)

        if not (is_smaller_than_bottom or is_bigger_than_bottom):
            raise ValueError(f"New element {element} is incomparable with the bottom element of {self.CLASS_NAME}")
        super(LowerSemiLattice, self).add(element, fill_up_cache)

        if self._use_cache:
            if is_smaller_than_bottom:
                self._cache_bottom = self._elements_to_index_map[element]

    def remove(self, element: Any):
        """Remove and ``element`` from the semilattice"""
        if self._elements[self.bottom] == element:
            raise ValueError(f"Cannot remove bottom element {element}")
        super(LowerSemiLattice, self).remove(element)

    def __delitem__(self, key: int):
        if self.bottom == key:
            raise KeyError(f"Cannot delete bottom element {key}")
        super(LowerSemiLattice, self).__delitem__(key)

        if self._use_cache:
            self._cache_bottom -= int(self._cache_bottom > key)


class Lattice(UpperSemiLattice, LowerSemiLattice):
    """A class to represent a Lattice

    A lattice is a POSet with a single top (the biggest) and a single bottom (the smallest) elements
    """
    CLASS_NAME = 'Lattice'
