"""
This module offers a class BinTable to work with binary table efficiently.

"""
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import List, Tuple, Optional, Collection, Any

from fcapy import LIB_INSTALLED
if LIB_INSTALLED['bitsets']:
    import bitsets
if LIB_INSTALLED['bitarray']:
    import bitarray
if LIB_INSTALLED['numpy']:
    import numpy as np
    import numpy.typing as npt


@dataclass
class UnmatchedTypeError(ValueError):
    row_idx: int

    def __str__(self):
        msg = '\n'.join([
            f'All rows should of the given `data` should be of the same type. '
            f'The problem is with the row #{self.row_idx}'
        ])
        return msg


@dataclass
class UnmatchedLengthError(ValueError):
    row_idx: int = None

    def __str__(self):
        msg = '\n'.join([
            f'All rows should of the given `data` should be of the same length. ',
            f'The problem is with the row #{self.row_idx}' if self.row_idx else ''
        ]).strip()
        return msg


@dataclass
class NotBooleanValueError(ValueError):
    row_idx: int = None

    def __str__(self):
        msg = '\n'.join([
            f"All values in each row should be of type bool.",
            f"The problem is with the row #{self.row_idx}" if self.row_idx else ''
        ]).strip()
        return msg


@dataclass
class UnknownDataTypeError(TypeError):
    unknown_type: type

    def __str__(self):
        msg = '\n'.join([
            "Dont know how to process the given `data`. ",
            "Acceptable types of data: List[List[bool]]. ",
            f"The given type: {self.unknown_type}"
        ]).strip()
        return msg


@dataclass
class UnknownAxisError(TypeError):
    unknown_axis: Any
    known_axes: set = frozenset({None, 0, 1})

    def __str__(self):
        msg = '\n'.join([
            f"Unknown `axis` value passed: {self.unknown_axis}. ",
            f"Supported values are: {self.known_axes}"
        ]).strip()
        return msg


class AbstractBinTable(metaclass=ABCMeta):
    def __init__(self, data: List[List[bool]] = None):
        self.data = data

    @property
    def data(self) -> Collection:
        return self._data

    @data.setter
    def data(self, value):
        data, h, w = self._transform_data(value)
        self._validate_data(data)
        self._data, self._height, self._width = data, h, w

    @property
    def height(self) -> Optional[int]:
        return self._height

    @property
    def width(self) -> Optional[int]:
        return self._width

    @property
    def shape(self) -> Optional[Tuple[int, Optional[int]]]:
        return self.height, self.width

    def all(self, axis: int = None) -> bool or Collection[bool]:
        if axis not in {None, 0, 1}:
            raise UnknownAxisError(axis)

        if axis is None:
            return self._all()
        if axis == 0:
            return self._all_per_column()
        if axis == 1:
            return self._all_per_row()

    def all_i(self, axis: int) -> Collection[int]:
        return [i for i, flg in enumerate(self.all(axis)) if flg]

    def any(self, axis: int = None) -> bool or Collection[bool]:
        if axis not in {None, 0, 1}:
            raise UnknownAxisError(axis)

        if axis is None:
            return self._any()
        if axis == 0:
            return self._any_per_column()
        if axis == 1:
            return self._any_per_row()

    def any_i(self, axis: int) -> Collection[int]:
        return [i for i, flg in enumerate(self.any(axis)) if flg]

    def sum(self, axis: int = None) -> int or Collection[int]:
        if axis not in {None, 0, 1}:
            raise UnknownAxisError(axis)

        if axis is None:
            return self._sum()
        if axis == 0:
            return self._sum_per_column()
        if axis == 1:
            return self._sum_per_row()

    def to_lists(self) -> List[List[bool]]:
        return [list(row) for row in self.data]

    def to_tuples(self) -> Tuple[Tuple[bool, ...], ...]:
        return tuple([tuple(row) for row in self.to_lists()])

    def __hash__(self):
        return hash(self.to_tuples())

    def __eq__(self, other: 'AbstractBinTable') -> bool:
        if self.height != other.height:
            return False
        if self.width != other.width:
            return False
        return self.data == other.data

    @abstractmethod
    def _validate_data(self, data) -> bool:
        ...

    @abstractmethod
    def _transform_data(self, data) -> Tuple[Collection, int, int]:
        ...

    @abstractmethod
    def _all(self) -> bool:
        ...

    @abstractmethod
    def _all_per_row(self) -> List[bool]:
        ...

    @abstractmethod
    def _all_per_column(self) -> List[bool]:
        ...

    @abstractmethod
    def _any(self) -> bool:
        ...

    @abstractmethod
    def _any_per_row(self) -> List[bool]:
        ...

    @abstractmethod
    def _any_per_column(self) -> List[bool]:
        ...

    @abstractmethod
    def _sum(self) -> int:
        ...

    @abstractmethod
    def _sum_per_row(self) -> List[int]:
        ...

    @abstractmethod
    def _sum_per_column(self) -> List[int]:
        ...


class BinTableLists(AbstractBinTable):
    data: List[List[bool]]  # Updating type hint

    def to_lists(self) -> List[List[bool]]:
        return self.data

    def _validate_data(self, data: List[List[bool]]) -> bool:
        if len(data) == 0:
            return True

        t_, l_ = type(data[0]), len(data[0])
        for i, row in enumerate(data):
            if type(row) != t_:
                raise UnmatchedTypeError(i)
            if len(row) != l_:
                raise UnmatchedLengthError(i)
            for v in row:
                if not isinstance(v, bool):
                    raise NotBooleanValueError(i)

        return True

    def _transform_data(self, data: Collection) \
            -> Tuple[List[List[bool]], int, Optional[int]]:
        if data is None:
            return [], 0, None

        if isinstance(data, list) and isinstance(data[0], list):
            h = len(data)
            w = len(data[0]) if h > 0 else None
            return data, h, w

        raise UnknownDataTypeError(type(data))

    def _all(self) -> bool:
        for row in self.data:
            if not all(row):
                return False
        return True

    def _all_per_row(self) -> List[bool]:
        return [all(row) for row in self.data]

    def _all_per_column(self) -> List[bool]:
        return [all(col) for col in zip(*self.data)]

    def _any(self) -> bool:
        for row in self.data:
            if any(row):
                return True
        return False

    def _any_per_row(self) -> List[bool]:
        return [any(row) for row in self.data]

    def _any_per_column(self) -> List[bool]:
        return [any(col) for col in zip(*self.data)]

    def _sum(self) -> int:
        return sum(self._sum_per_row())

    def _sum_per_row(self) -> List[int]:
        return [sum(row) for row in self.data]

    def _sum_per_column(self) -> List[int]:
        return [sum(col) for col in zip(*self.data)]


class BinTableNumpy(AbstractBinTable):
    data: npt.NDArray[bool]  # Updating type hint

    def _validate_data(self, data: npt.NDArray[bool]) -> bool:
        if len(data) == 0:
            return True

        if data.dtype != 'bool':
            raise NotBooleanValueError()

        if len(data.shape) != 2:
            raise UnmatchedLengthError()

        return True

    def _transform_data(self, data: Collection) -> Tuple[npt.NDArray[bool], int, Optional[int]]:
        if data is None:
            return np.array([]), 0, None

        if isinstance(data, list) and isinstance(data[0], list):
            data = np.array(BinTableLists(data).data)
            h, w = data.shape
            return data, h, w

        raise UnknownDataTypeError(type(data))

    def _all(self) -> bool:
        return self.data.all()

    def _all_per_row(self) -> npt.NDArray[bool]:
        return self.data.all(1)

    def _all_per_column(self) -> npt.NDArray[bool]:
        return self.data.all(0)

    def _any(self) -> bool:
        return self.data.any()

    def _any_per_row(self) -> npt.NDArray[bool]:
        return self.data.any(1)

    def _any_per_column(self) -> npt.NDArray[bool]:
        return self.data.any(0)

    def _sum(self) -> int:
        return self.data.sum()

    def _sum_per_row(self) -> npt.NDArray[int]:
        return self.data.sum(1)

    def _sum_per_column(self) -> npt.NDArray[int]:
        return self.data.sum(0)

    def __eq__(self, other: 'BinTableNumpy'):
        if self.height != other.height:
            return False
        if self.width != other.width:
            return False
        return (self.data == other.data).all()

    def __hash__(self):
        return hash(self.to_tuples())


class BinTableBitsets(AbstractBinTable):
    pass


BINTABLE_CLASSES = {'BinTableLists': BinTableLists, 'BinTableNumpy': BinTableNumpy}
