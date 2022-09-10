"""
This module offers a class BinTable to work with binary table efficiently.

"""
from typing import List, Tuple, Optional, Collection

from fcapy import LIB_INSTALLED
if LIB_INSTALLED['bitsets']:
    import bitsets
if LIB_INSTALLED['bitarray']:
    import bitarray
if LIB_INSTALLED['numpy']:
    import numpy as np


class AbstractBinTable:
    def __init__(self, data: List[List[bool]]):
        self.data = data

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value

    @property
    def height(self) -> Optional[int]:
        return len(self._data) if self.data else None

    @property
    def width(self) -> Optional[int]:
        return len(self.data[0]) if self.data else None

    @property
    def shape(self) -> Optional[Tuple[int, int]]:
        return (self.height, self.width) if self.data else None

    def all(self, axis: int = None) -> bool or Collection[bool]:
        raise NotImplementedError

    def any(self, axis: int = None) -> bool or Collection[bool]:
        raise NotImplementedError

    def sum(self, axis: int = None) -> int or Collection[int]:
        raise NotImplementedError

    def to_lists(self) -> List[List[bool]]:
        return [list(row) for row in self.data]

    def to_tuples(self) -> Tuple[Tuple[bool, ...], ...]:
        return tuple([tuple(row) for row in self.to_lists()])

    def __eq__(self, other):
        """Compare is this BinTable is equal to the ``other`` """
        return self._data == other.data

    def __hash__(self):
        return hash(self.to_tuples())


class BinTableLists(AbstractBinTable):
    pass


class BinTableNumpy(AbstractBinTable):
    pass


class BinTableBitsets(AbstractBinTable):
    pass
