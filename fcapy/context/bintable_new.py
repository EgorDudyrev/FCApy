"""
This module offers a class BinTable to work with binary table efficiently.

"""
from abc import ABCMeta, abstractmethod
from typing import List, Tuple, Optional, Collection, Sequence

from fcapy.context import bintable_errors as berrors
from fcapy import LIB_INSTALLED
if LIB_INSTALLED['bitarray']:
    from bitarray import frozenbitarray as fbitarray
    from bitarray import bitarray

if LIB_INSTALLED['numpy']:
    import numpy as np
    import numpy.typing as npt


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

    def all(self, axis: int = None, element_indexes: Collection[int] = None) -> bool or Collection[bool]:
        if axis not in {None, 0, 1}:
            raise berrors.UnknownAxisError(axis)

        if axis is None:
            return self._all()
        if axis == 0:
            return self._all_per_column(element_indexes)
        if axis == 1:
            return self._all_per_row(element_indexes)

    def all_i(self, axis: int, element_indexes: Collection[int] = None) -> Collection[int]:
        flg_all = self.all(axis, element_indexes)
        iterator = enumerate(flg_all) if element_indexes is None else zip(element_indexes, flg_all)
        return [i for i, flg in iterator if flg]

    def any(self, axis: int = None, element_indexes: Collection[int] = None) -> bool or Collection[bool]:
        if axis not in {None, 0, 1}:
            raise berrors.UnknownAxisError(axis)

        if axis is None:
            return self._any()
        if axis == 0:
            return self._any_per_column(element_indexes)
        if axis == 1:
            return self._any_per_row(element_indexes)

    def any_i(self, axis: int, element_indexes: Collection[int] = None) -> Collection[int]:
        flg_any = self.any(axis, element_indexes)
        iterator = enumerate(flg_any) if element_indexes is None else zip(element_indexes, flg_any)
        return [i for i, flg in iterator if flg]

    def sum(self, axis: int = None, element_indexes: Collection[int] = None) -> int or Collection[int]:
        if axis not in {None, 0, 1}:
            raise berrors.UnknownAxisError(axis)

        if axis is None:
            return self._sum()
        if axis == 0:
            return self._sum_per_column(element_indexes)
        if axis == 1:
            return self._sum_per_row(element_indexes)

    def to_lists(self) -> List[List[bool]]:
        return [[bool(v) for v in row] for row in self.data]

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

    def __and__(self, other: 'AbstractBinTable') -> 'AbstractBinTable':
        assert self.shape == other.shape
        return self.__class__(self.data & other.data)

    def __or__(self, other: 'AbstractBinTable') -> 'AbstractBinTable':
        assert self.shape == other.shape
        return self.__class__(self.data | other.data)

    @abstractmethod
    def _validate_data(self, data) -> bool:
        ...

    def _transform_data(self, data) -> Tuple[Collection, int, Optional[int]]:
        if data is None:
            return [], 0, None

        dclass = self.decide_dataclass(data)
        if dclass == self.__class__.__name__:
            return self._transform_data_inherent(data)

        bt = BINTABLE_CLASSES[dclass](data)
        return self._transform_data_fromlists(bt.to_lists()), bt.height, bt.width

    @staticmethod
    def _transform_data_inherent(data) -> Tuple[Collection, int, int]:
        return data, len(data), len(data[0])

    @abstractmethod
    def _transform_data_fromlists(self, data: List[List[bool]]) -> Collection:
        ...

    @abstractmethod
    def _all(self) -> bool:
        ...

    @abstractmethod
    def _all_per_row(self, row_indexes: Collection[int] = None) -> List[bool]:
        ...

    @abstractmethod
    def _all_per_column(self, column_indexes: Collection[int] = None) -> List[bool]:
        ...

    @abstractmethod
    def _any(self) -> bool:
        ...

    @abstractmethod
    def _any_per_row(self, row_indexes: Collection[int] = None) -> List[bool]:
        ...

    @abstractmethod
    def _any_per_column(self, column_indexes: Collection[int] = None) -> List[bool]:
        ...

    @abstractmethod
    def _sum(self) -> int:
        ...

    @abstractmethod
    def _sum_per_row(self, row_indexes: Collection[int] = None) -> List[int]:
        ...

    @abstractmethod
    def _sum_per_column(self, column_indexes: Collection[int] = None) -> List[int]:
        ...

    def __len__(self):
        return self.height

    def __getitem__(self, item):
        if isinstance(item, int):
            return self._get_row(item)
        if isinstance(item, (slice, list)):
            return self._get_subtable(item, None)
        if isinstance(item, tuple):
            single_slices = tuple([isinstance(x, int) for x in item])
            func_dict = {
                (True, True): self._get_item, (True, False): self._get_row,
                (False, True): self._get_column, (False, False): self._get_subtable
            }
            return func_dict[single_slices](*item)

        raise NotImplementedError("Unknown `item` to slice the BinTable")

    def _get_item(self, row_idx: int, column_idx: int) -> bool:
        return bool(self.data[row_idx][column_idx])

    def _get_row(self, row_idx: int, column_slicer: List[int] or slice = None) -> Collection:
        if column_slicer is None:
            return self.data[row_idx]
        return self.data[row_idx][column_slicer]

    def _get_column(self, row_slicer: List[int] or slice, column_idx: int) -> Collection:
        return self.data[row_slicer][:, column_idx]

    def _get_subtable(self, row_slicer: List[int] or slice, column_slicer: List[int] or slice or None)\
            -> "AbstractBinTable":
        if column_slicer is None:
            return self.__class__(self.data[row_slicer])
        return self.__class__(self.data[row_slicer, column_slicer])

    @staticmethod
    def decide_dataclass(data: Collection) -> str:
        assert len(data) > 0, "Too small data to decide what class does it belong to"
        if isinstance(data, list) and isinstance(data[0], list):
            return 'BinTableLists'
        if isinstance(data, list) and isinstance(data[0], fbitarray):
            return 'BinTableBitarray'
        if isinstance(data, np.ndarray):
            return 'BinTableNumpy'

        raise berrors.UnknownDataTypeError(type(data))


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
                raise berrors.UnmatchedTypeError(i)
            if len(row) != l_:
                raise berrors.UnmatchedLengthError(i)
            for v in row:
                if not isinstance(v, bool):
                    raise berrors.NotBooleanValueError(i)

        return True

    def _transform_data_fromlists(self, data: List[List[bool]]) -> List[List[bool]]:
        return data

    def _all(self) -> bool:
        for row in self.data:
            if not all(row):
                return False
        return True

    def _all_per_row(self, row_indexes: List[int] = None) -> List[bool]:
        row_indexes = range(self.height) if row_indexes is None else row_indexes
        return [all(self.data[i]) for i in row_indexes]

    def _all_per_column(self, column_indexes: List[int] = None) -> List[bool]:
        if column_indexes is None:
            vals, column_indexes = [True] * self.width, range(self.width)
        else:
            vals = [True] * len(column_indexes)

        for row in self.data:
            vals = [v & row[col_i] for v, col_i in zip(vals, column_indexes)]
            if not any(vals):  # All values are False
                break
        return vals

    def _any(self) -> bool:
        for row in self.data:
            if any(row):
                return True
        return False

    def _any_per_row(self, row_indexes: List[int] = None) -> List[bool]:
        row_indexes = range(self.height) if row_indexes is None else row_indexes
        return [any(self.data[i]) for i in row_indexes]

    def _any_per_column(self, column_indexes: List[int] = None) -> List[bool]:
        if column_indexes is None:
            vals, column_indexes = range(self.width), [False] * self.width
        else:
            vals = [False] * len(column_indexes)

        for row in self.data:
            vals = [v | row[col_i] for v, col_i in zip(vals, column_indexes)]
            if all(vals):  # All values are True
                break
        return vals

    def _sum(self) -> int:
        return sum(self._sum_per_row())

    def _sum_per_row(self, row_indexes: List[int] = None) -> List[int]:
        row_indexes = range(self.height) if row_indexes is None else row_indexes
        return [sum(self.data[i]) for i in row_indexes]

    def _sum_per_column(self, column_indexes: List[int] = None) -> List[int]:
        if column_indexes is None:
            vals, column_indexes = range(self.width), [0] * self.width
        else:
            vals = [0] * len(column_indexes)

        for row in self.data:
            vals = [v + int(row[col_i]) for v, col_i in zip(vals, column_indexes)]
        return vals

    def _get_row(self, row_idx: int, column_slicer: List[int] or slice = None) -> List[bool]:
        row = self.data[row_idx]
        if column_slicer:
            if isinstance(column_slicer, slice):
                column_slicer = range(*column_slicer.indices(self.width))
            return [row[col] for col in column_slicer]
        return row

    def _get_column(self, row_slicer: List[int] or slice, column_idx: int) -> List[bool]:
        if isinstance(row_slicer, slice):
            row_slicer = range(*row_slicer.indices(self.height))
        column = [self.data[row_i][column_idx] for row_i in row_slicer]
        return column

    def _get_subtable(self, row_slicer: List[int] or slice, column_slicer: List[int] or slice or None) \
            -> 'BinTableLists':
        if isinstance(row_slicer, slice):
            row_slicer = range(*row_slicer.indices(self.height))

        if column_slicer is None:
            subtable = [self.data[row_i] for row_i in row_slicer]
        else:
            if isinstance(column_slicer, slice):
                column_slicer = range(*column_slicer.indices(self.width))
            subtable = [[self.data[row_i][col_i] for col_i in column_slicer] for row_i in row_slicer]

        return self.__class__(subtable)

    def __and__(self, other: 'BinTableLists') -> 'BinTableLists':
        assert self.shape == other.shape
        intersection = [[a and b for a, b in zip(row_a, row_b)] for row_a, row_b in zip(self.data, other.data)]
        return self.__class__(intersection)

    def __or__(self, other: 'BinTableLists') -> 'BinTableLists':
        assert self.shape == other.shape
        intersection = [[a or b for a, b in zip(row_a, row_b)] for row_a, row_b in zip(self.data, other.data)]
        return self.__class__(intersection)


class BinTableNumpy(AbstractBinTable):
    data: npt.NDArray[bool]  # Updating type hint

    def _transform_data_fromlists(self, data: List[List[bool]]) -> npt.NDArray[bool]:
        return np.array(data)

    def _validate_data(self, data: npt.NDArray[bool]) -> bool:
        if len(data) == 0:
            return True

        if data.dtype != 'bool':
            raise berrors.NotBooleanValueError()

        if len(data.shape) != 2:
            raise berrors.UnmatchedLengthError()

        return True

    def _all(self) -> bool:
        return self.data.all()

    def _all_per_row(self, row_indexes: npt.NDArray[int] = None) -> npt.NDArray[bool]:
        flg = self.data.all(1)
        if row_indexes is None:
            return flg
        return flg[row_indexes]

    def _all_per_column(self, column_indexes: npt.NDArray[int] = None) -> npt.NDArray[bool]:
        flg = self.data.all(0)
        if column_indexes is None:
            return flg
        return flg[column_indexes]

    def _any(self) -> bool:
        return self.data.any()

    def _any_per_row(self, row_indexes: npt.NDArray[int] = None) -> npt.NDArray[bool]:
        flg = self.data.any(1)
        if row_indexes is None:
            return flg
        return flg[row_indexes]

    def _any_per_column(self, column_indexes: npt.NDArray[int] = None) -> npt.NDArray[bool]:
        flg = self.data.any(0)
        if column_indexes is None:
            return flg
        return flg[column_indexes]

    def _sum(self) -> int:
        return self.data.sum()

    def _sum_per_row(self, row_indexes: npt.NDArray[int] = None) -> npt.NDArray[int]:
        flg = self.data.sum(1)
        if row_indexes is None:
            return flg
        return flg[row_indexes]

    def _sum_per_column(self, column_indexes: npt.NDArray[int] = None) -> npt.NDArray[int]:
        flg = self.data.sum(0)
        if column_indexes is None:
            return flg
        return flg[column_indexes]

    def __eq__(self, other: 'BinTableNumpy'):
        if self.height != other.height:
            return False
        if self.width != other.width:
            return False
        return (self.data == other.data).all()

    def __hash__(self):
        return hash(self.to_tuples())


class BinTableBitarray(AbstractBinTable):
    data: List[fbitarray]  # Updating type hint

    def _transform_data_fromlists(self, data: List[List[bool]]) -> List[fbitarray]:
        return [fbitarray(row) for row in data]

    def _validate_data(self, data: List[fbitarray]) -> bool:
        if len(data) == 0:
            return True

        l_ = len(data[0])
        for i, row in enumerate(data):
            if len(row) != l_:
                raise berrors.UnmatchedLengthError(i)

        return True

    def _all(self) -> bool:
        for row in self.data:
            if not row.all():
                return False
        return True

    def _all_per_row(self, row_indexes: List[int] = None) -> fbitarray:
        row_indexes = range(self.height) if row_indexes is None else row_indexes
        return fbitarray([self.data[i].all() for i in row_indexes])

    def _all_per_column(self, column_indexes: List[int] = None) -> fbitarray:
        vals = bitarray(self.data[0])
        for row in self.data[1:]:
            vals &= row
            if not vals.any():  # If all values are False
                break
        if column_indexes is not None:
            vals = fbitarray([vals[i] for i in column_indexes])
        return vals

    def _any(self) -> bool:
        for row in self.data:
            if row.any():
                return True
        return False

    def _any_per_row(self, row_indexes: List[int] = None) -> fbitarray:
        row_indexes = range(self.height) if row_indexes is None else row_indexes
        return fbitarray([self.data[i].any() for i in row_indexes])

    def _any_per_column(self, column_indexes: List[int] = None) -> fbitarray:
        vals = bitarray(self.data[0])
        for row in self.data[1:]:
            vals |= row
            if vals.all():
                break
        if column_indexes is not None:
            vals = fbitarray([vals[i] for i in column_indexes])
        return vals

    def _sum(self) -> int:
        return sum(self._sum_per_row())

    def _sum_per_row(self, row_indexes: List[int] = None) -> List[int]:
        row_indexes = range(self.height) if row_indexes is None else row_indexes
        return [self.data[i].count() for i in row_indexes]

    def _sum_per_column(self, column_indexes: List[int] = None) -> List[int]:
        if column_indexes is None:
            vals, column_indexes = [0] * self.width, range(self.width)
        else:
            vals = [0] * len(column_indexes)

        for row in self.data:
            vals = [v + int(row[i]) for v, i in zip(vals, column_indexes)]
        return vals

    def _get_row(self, row_idx: int, column_slicer: List[int] or slice = None) -> fbitarray:
        row = self.data[row_idx]
        if column_slicer:
            if isinstance(column_slicer, list):
                return fbitarray([row[col_i] for col_i in column_slicer])
            return row[column_slicer]
        return row

    def _get_column(self, row_slicer: List[int] or slice, column_idx: int) -> fbitarray:
        if isinstance(row_slicer, slice):
            row_slicer = range(*row_slicer.indices(self.height))
        return fbitarray([self._data[row_i][column_idx] for row_i in row_slicer])

    def _get_subtable(self, row_slicer: List[int] or slice, column_slicer: List[int] or slice or None) \
            -> 'BinTableBitarray':
        if isinstance(row_slicer, slice):
            row_slicer = range(*row_slicer.indices(self.height))

        if column_slicer is None:
            subtable = [self.data[row_i] for row_i in row_slicer]
        elif isinstance(column_slicer, list):
            subtable = [fbitarray([self.data[row_i][col_i] for col_i in column_slicer]) for row_i in row_slicer]
        else:
            subtable = [self.data[row_i][column_slicer] for row_i in row_slicer]

        return self.__class__(subtable)

    def __eq__(self, other: 'BinTableBitarray'):
        if self.height != other.height:
            return False
        if self.width != other.width:
            return False
        return self.data == other.data

    def __hash__(self):
        return hash(tuple(self.data))

    def __and__(self, other: 'BinTableBitarray') -> 'BinTableBitarray':
        assert self.shape == other.shape
        intersection = [row_a & row_b for row_a, row_b in zip(self.data, other.data)]
        return self.__class__(intersection)

    def __or__(self, other: 'BinTableBitarray') -> 'BinTableBitarray':
        assert self.shape == other.shape
        intersection = [row_a | row_b for row_a, row_b in zip(self.data, other.data)]
        return self.__class__(intersection)


BINTABLE_CLASSES = {cl.__name__: cl for cl in [BinTableLists, BinTableNumpy, BinTableBitarray]}
