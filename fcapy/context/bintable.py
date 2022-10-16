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
    Row_DType = Collection[bool]

    def __init__(self, data: List[Row_DType] = None):
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

    @property
    def T(self) -> 'AbstractBinTable':
        return self.__class__([list(row) for row in zip(*self.data)])

    def all(self, axis: int = None, rows: Collection[int] = None, columns: Collection[int] = None)\
            -> bool or Collection[bool]:
        if axis not in {None, 0, 1}:
            raise berrors.UnknownAxisError(axis)

        if axis is None:
            return self._all(rows, columns)
        if axis == 0:
            return self._all_per_column(rows, columns)
        if axis == 1:
            return self._all_per_row(rows, columns)

    def all_i(self, axis: int, rows: Collection[int] = None, columns: Collection[int] = None) -> Collection[int]:
        flg_all = self.all(axis, rows, columns)
        if axis == 0:
            iterator = zip(columns, flg_all) if columns is not None else enumerate(flg_all)
        else:  # axis == 1
            iterator = zip(rows, flg_all) if rows is not None else enumerate(flg_all)
        return [i for i, flg in iterator if flg]

    def any(self, axis: int = None, rows: Collection[int] = None, columns: Collection[int] = None)\
            -> bool or Row_DType:
        if axis not in {None, 0, 1}:
            raise berrors.UnknownAxisError(axis)

        if axis is None:
            return self._any(rows, columns)
        if axis == 0:
            return self._any_per_column(rows, columns)
        if axis == 1:
            return self._any_per_row(rows, columns)

    def any_i(self, axis: int, rows: Collection[int] = None, columns: Collection[int] = None) -> Collection[int]:
        flg_any = self.any(axis, rows, columns)

        if axis == 0:
            iterator = zip(columns, flg_any) if columns is not None else enumerate(flg_any)
        else:  # axis == 1
            iterator = zip(rows, flg_any) if rows is not None else enumerate(flg_any)

        return [i for i, flg in iterator if flg]

    def sum(self, axis: int = None, rows: Collection[int] = None, columns: Collection[int] = None)\
            -> int or Collection[int]:
        if axis not in {None, 0, 1}:
            raise berrors.UnknownAxisError(axis)

        if axis is None:
            return self._sum(rows, columns)
        if axis == 0:
            return self._sum_per_column(rows, columns)
        if axis == 1:
            return self._sum_per_row(rows, columns)

    def to_list(self) -> List[List[bool]]:
        return [[bool(v) for v in row] for row in self.data]

    def to_tuple(self) -> Tuple[Tuple[bool, ...], ...]:
        return tuple([tuple(row) for row in self.to_list()])

    def __hash__(self):
        return hash(self.to_tuple())

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

    def __invert__(self) -> 'AbstractBinTable':
        return self.__class__(~self.data)

    @abstractmethod
    def _validate_data(self, data) -> bool:
        ...

    def _transform_data(self, data) -> Tuple[Collection, int, Optional[int]]:
        if data is None or len(data) == 0:
            return [], 0, 0

        dclass = self.decide_dataclass(data)
        if dclass == self.__class__.__name__:
            return self._transform_data_inherent(data)

        bt = BINTABLE_CLASSES[dclass](data)
        return self._transform_data_fromlists(bt.to_list()), bt.height, bt.width

    @staticmethod
    def _transform_data_inherent(data) -> Tuple[Collection, int, int]:
        return data, len(data), len(data[0])

    @abstractmethod
    def _transform_data_fromlists(self, data: List[List[bool]]) -> Collection[Row_DType]:
        ...

    @abstractmethod
    def _all(self, rows: Collection[int] = None, columns: Collection[int] = None) -> bool:
        ...

    @abstractmethod
    def _all_per_row(self, rows: Collection[int] = None, columns: Collection[int] = None) -> Row_DType:
        ...

    @abstractmethod
    def _all_per_column(self, rows: Collection[int] = None, columns: Collection[int] = None) -> Row_DType:
        ...

    @abstractmethod
    def _any(self, rows: Collection[int] = None, columns: Collection[int] = None) -> bool:
        ...

    @abstractmethod
    def _any_per_row(self, rows: Collection[int] = None, columns: Collection[int] = None) -> Row_DType:
        ...

    @abstractmethod
    def _any_per_column(self, rows: Collection[int] = None, columns: Collection[int] = None) -> Row_DType:
        ...

    @abstractmethod
    def _sum(self, rows: Collection[int] = None, columns: Collection[int] = None) -> int:
        ...

    @abstractmethod
    def _sum_per_row(self, rows: Collection[int] = None, columns: Collection[int] = None) -> List[int]:
        ...

    @abstractmethod
    def _sum_per_column(self, rows: Collection[int] = None, columns: Collection[int] = None) -> List[int]:
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

    def _get_row(self, row_idx: int, column_slicer: List[int] or slice = None) -> Row_DType:
        if column_slicer is None:
            return self.data[row_idx]
        return self.data[row_idx][column_slicer]

    def _get_column(self, row_slicer: List[int] or slice, column_idx: int) -> Row_DType:
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
    Row_DType = List[bool]

    def to_list(self) -> List[List[bool]]:
        return self.data

    def _validate_data(self, data: List[Row_DType]) -> bool:
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

    def _transform_data_fromlists(self, data: List[List[bool]]) -> List[Row_DType]:
        return data

    def _all(self, rows: List[int] = None, columns: List[int] = None) -> bool:
        rows = range(self.height) if rows is None else rows
        # A bit faster version in case all columns are selected
        if columns is None:
            for i in rows:
                if not all(self.data[i]):
                    return False
        else:
            for i in rows:
                row = self.data[i]
                for j in columns:
                    if not row[j]:
                        return False

        return True

    def _all_per_row(self, rows: List[int] = None, columns: List[int] = None) -> Row_DType:
        rows = range(self.height) if rows is None else rows
        if columns is None:
            return [all(self.data[i]) for i in rows]
        return [all([self.data[i][j] for j in columns]) for i in rows]

    def _all_per_column(self, rows: List[int] = None, columns: List[int] = None) -> Row_DType:
        rows = range(self.height) if rows is None else rows
        if columns is None:
            vals, columns = [True] * self.width, range(self.width)
        else:
            vals = [True] * len(columns)

        for i in rows:
            row = self.data[i]
            vals = [v & row[col_i] for v, col_i in zip(vals, columns)]
            if not any(vals):  # All values are False
                break
        return vals

    def _any(self, rows: List[int] = None, columns: List[int] = None) -> bool:
        rows = range(self.height) if rows is None else rows
        if columns is None:
            for i in rows:
                if any(self.data[i]):
                    return True
        else:
            for i in rows:
                row = self.data[i]
                for j in columns:
                    if row[j]:
                        return True
        return False

    def _any_per_row(self, rows: List[int] = None, columns: List[int] = None) -> Row_DType:
        rows = range(self.height) if rows is None else rows
        if columns is None:
            return [any(self.data[i]) for i in rows]
        return [any([self.data[i][j] for j in columns] for i in rows)]

    def _any_per_column(self, rows: List[int] = None, columns: List[int] = None) -> Row_DType:
        rows = range(self.height) if rows is None else rows
        if columns is None:
            vals, columns = range(self.width), [False] * self.width
        else:
            vals = [False] * len(columns)

        for i in rows:
            row = self.data[i]
            vals = [v | row[col_i] for v, col_i in zip(vals, columns)]
            if all(vals):  # All values are True
                break
        return vals

    def _sum(self, rows: List[int] = None, columns: List[int] = None) -> int:
        return sum(self._sum_per_row(rows, columns))

    def _sum_per_row(self, rows: List[int] = None, columns: List[int] = None) -> List[int]:
        rows = range(self.height) if rows is None else rows
        if columns is None:
            return [sum(self.data[i]) for i in rows]
        return [sum([self.data[i][j] for j in columns]) for i in rows]

    def _sum_per_column(self, rows: List[int] = None, columns: List[int] = None) -> List[int]:
        rows = range(self.height) if rows is None else rows
        if columns is None:
            vals, columns = range(self.width), [0] * self.width
        else:
            vals = [0] * len(columns)

        for i in rows:
            row = self.data[i]
            vals = [v + int(row[col_i]) for v, col_i in zip(vals, columns)]
        return vals

    def _get_row(self, row_idx: int, column_slicer: List[int] or slice = None) -> Row_DType:
        row = self.data[row_idx]
        if column_slicer:
            if isinstance(column_slicer, slice):
                column_slicer = range(*column_slicer.indices(self.width))
            return [row[col] for col in column_slicer]
        return row

    def _get_column(self, row_slicer: List[int] or slice, column_idx: int) -> Row_DType:
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

    def __invert__(self) -> 'BinTableLists':
        data_neg = [[not v for v in row] for row in self.data]
        return self.__class__(data_neg)


class BinTableNumpy(AbstractBinTable):
    data: npt.NDArray[bool]  # Updating type hint
    Row_DType = npt.NDArray[bool]

    @property
    def T(self) -> 'BinTableNumpy':
        return self.__class__(self.data.T)

    def all_i(self, axis: int, rows: npt.NDArray[int] = None, columns: npt.NDArray[int] = None) -> npt.NDArray[int]:
        flg_all = self.all(axis, rows, columns)

        if axis == 0:
            full_ar = np.arange(self.width) if columns is None else columns
        else:  # axis == 1
            full_ar = np.arange(self.height) if rows is None else rows
        return full_ar[flg_all]

    def any_i(self, axis: int, rows: npt.NDArray[int] = None, columns: npt.NDArray[int] = None) -> npt.NDArray[int]:
        flg_any = self.any(axis, rows, columns)

        if axis == 0:
            full_ar = np.arange(self.width) if columns is None else columns
        else:  # axis == 1
            full_ar = np.arange(self.height) if rows is None else rows
        return full_ar[flg_any]

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

    def _all(self, rows: npt.NDArray[int] = None, columns: npt.NDArray[int] = None) -> bool:
        if rows is None and columns is None:
            return self.data.all()
        return self.data[rows, columns].all()

    def _all_per_row(self, rows: npt.NDArray[int] = None, columns: npt.NDArray[int] = None) -> Row_DType:
        if rows is None and columns is None:
            return self.data.all(1)
        return self.data[rows, columns].all(1)

    def _all_per_column(self, rows: npt.NDArray[int] = None, columns: npt.NDArray[int] = None) -> Row_DType:
        if rows is None and columns is None:
            return self.data.all(0)
        return self.data[rows, columns].all(0)

    def _any(self, rows: npt.NDArray[int] = None, columns: npt.NDArray[int] = None) -> bool:
        if rows is None and columns is None:
            return self.data.any()
        return self.data[rows, columns].any()

    def _any_per_row(self, rows: npt.NDArray[int] = None, columns: npt.NDArray[int] = None) -> Row_DType:
        if rows is None and columns is None:
            return self.data.any(1)
        return self.data[rows, columns].any(1)

    def _any_per_column(self, rows: npt.NDArray[int] = None, columns: npt.NDArray[int] = None) -> Row_DType:
        if rows is None and columns is None:
            return self.data.any(0)
        return self.data[rows, columns].any(0)

    def _sum(self, rows: npt.NDArray[int] = None, columns: npt.NDArray[int] = None) -> int:
        if rows is None and columns is None:
            return self.data.sum()
        return self.data[rows, columns].sum()

    def _sum_per_row(self, rows: npt.NDArray[int] = None, columns: npt.NDArray[int] = None) -> npt.NDArray[int]:
        if rows is None and columns is None:
            return self.data.sum(1)
        return self.data[rows, columns].sum(1)

    def _sum_per_column(self, rows: npt.NDArray[int] = None, columns: npt.NDArray[int] = None) -> npt.NDArray[int]:
        if rows is None and columns is None:
            return self.data.sum(0)
        return self.data[rows, columns].sum(0)

    def __eq__(self, other: 'BinTableNumpy'):
        if self.height != other.height:
            return False
        if self.width != other.width:
            return False
        return (self.data == other.data).all()

    def __hash__(self):
        return hash(self.to_tuple())


class BinTableBitarray(AbstractBinTable):
    data: List[fbitarray]  # Updating type hint
    Row_DType = fbitarray

    @property
    def T(self) -> 'BinTableBitarray':
        return self.__class__([fbitarray(row) for row in zip(*self.data)])

    def all_i(self, axis: int, rows: List[int] = None, columns: List[int] = None) -> List[int]:
        flg_all = self.all(axis, rows, columns)
        return flg_all.search(1)

    def any_i(self, axis: int, rows: List[int] = None, columns: List[int] = None) -> List[int]:
        flg_any = self.any(axis, rows, columns)
        return flg_any.search(1)

    def _transform_data_fromlists(self, data: List[List[bool]]) -> List[Row_DType]:
        return [fbitarray(row) for row in data]

    def _validate_data(self, data: List[fbitarray]) -> bool:
        if len(data) == 0:
            return True

        l_ = len(data[0])
        for i, row in enumerate(data):
            if len(row) != l_:
                raise berrors.UnmatchedLengthError(i)

        return True

    def _all(self, rows: List[int] = None, columns: List[int] = None) -> bool:
        rows = range(self.height) if rows is None else rows
        if columns is None:
            for i in rows:
                row = self.data[i]
                if not row.all():
                    return False
        else:
            columns = set(columns)
            mask = fbitarray([j not in columns for j in range(self.width)])

            for i in rows:
                row = self.data[i]
                if not (row | mask).all():
                    return False

        return True

    def _all_per_row(self, rows: List[int] = None, columns: List[int] = None) -> Row_DType:
        rows = range(self.height) if rows is None else rows
        if columns is None:
            return fbitarray([self.data[i].all() for i in rows])

        columns = set(columns)
        mask = fbitarray([j not in columns for j in range(self.width)])

        return fbitarray([(self.data[i] | mask).all() for i in rows])

    def _all_per_column(self, rows: List[int] = None, columns: List[int] = None) -> Row_DType:
        rows = range(self.height) if rows is None else rows
        vals = bitarray(self.data[0] | (~self.data[0]))  # Bitarray of Trues
        if columns is None:
            for i in rows:
                vals &= self.data[i]
                if not vals.any():  # If all values are False
                    break
        else:
            columns_set = set(columns)
            mask = fbitarray([j in columns_set for j in range(self.width)])
            for i in rows:
                vals &= self.data[i]
                if not (vals & mask).any():  # If all values are False
                    break

            vals = fbitarray([vals[i] for i in columns])
        return vals

    def _any(self, rows: List[int] = None, columns: List[int] = None) -> bool:
        rows = range(self.height) if rows is None else rows
        if columns is None:
            for i in rows:
                if self.data[i].any():
                    return True
        else:
            columns = set(columns)
            mask = fbitarray([j in columns for j in range(self.width)])

            for i in rows:
                if (self.data[i] & mask).any():
                    return True

        return False

    def _any_per_row(self, rows: List[int] = None, columns: List[int] = None) -> Row_DType:
        rows = range(self.height) if rows is None else rows
        if columns is None:
            return fbitarray([self.data[i].any() for i in rows])

        columns = set(columns)
        mask = fbitarray([j in columns for j in range(self.width)])
        return fbitarray([(self.data[i] & mask).any() for i in rows])

    def _any_per_column(self, rows: List[int] = None, columns: List[int] = None) -> Row_DType:
        rows = range(self.height) if rows is None else rows

        vals = bitarray(self.data[0] & (~self.data[0]))  # Bitarray of all False
        if columns is None:
            for i in rows:
                vals |= self.data[i]
                if vals.all():
                    break
        else:
            columns_set = set(columns)
            mask = fbitarray([j not in columns_set for j in range(self.width)])

            for i in rows:
                vals |= self.data[i]
                if (vals | mask).all():
                    break

            vals = fbitarray([vals[i] for i in columns])
        return vals

    def _sum(self, rows: List[int] = None, columns: List[int] = None) -> int:
        return sum(self._sum_per_row(rows, columns))

    def _sum_per_row(self, rows: List[int] = None, columns: List[int] = None) -> List[int]:
        rows = range(self.height) if rows is None else rows
        if columns is None:
            return [self.data[i].count() for i in rows]

        columns = set(columns)
        mask = fbitarray([j in columns for j in range(self.width)])
        return [(self.data[i] & mask).count() for i in rows]

    def _sum_per_column(self, rows: List[int] = None, columns: List[int] = None) -> List[int]:
        rows = range(self.height) if rows is None else rows
        if columns is None:
            vals = [0] * self.width
            for i in rows:
                for j in self.data[i].search(1):
                    vals[j] += 1
        else:
            vals = [0] * len(columns)

            columns_set = set(columns)
            mask = fbitarray([j in columns_set for j in range(self.width)])
            for i in rows:
                for j in (self.data[i] & mask).search(1):
                    vals[j] += 1

        return vals

    def _get_row(self, row_idx: int, column_slicer: List[int] or slice = None) -> Row_DType:
        row = self.data[row_idx]
        if column_slicer:
            if isinstance(column_slicer, slice):
                return row[column_slicer]
            return fbitarray([row[col_i] for col_i in column_slicer])
        return row

    def _get_column(self, row_slicer: List[int] or slice, column_idx: int) -> Row_DType:
        if isinstance(row_slicer, slice):
            row_slicer = range(*row_slicer.indices(self.height))
        return fbitarray([self._data[row_i][column_idx] for row_i in row_slicer])

    def _get_subtable(self, row_slicer: List[int] or slice, column_slicer: List[int] or slice or None) \
            -> 'BinTableBitarray':
        if isinstance(row_slicer, slice):
            row_slicer = range(*row_slicer.indices(self.height))

        if column_slicer is None:
            subtable = [self.data[row_i] for row_i in row_slicer]
        elif isinstance(column_slicer, slice):
            subtable = [self.data[row_i][column_slicer] for row_i in row_slicer]
        else:
            subtable = [fbitarray([self.data[row_i][col_i] for col_i in column_slicer]) for row_i in row_slicer]

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

    def __invert__(self) -> 'BinTableBitarray':
        data_neg = [~row for row in self.data]
        return self.__class__(data_neg)


BINTABLE_CLASSES = {cl.__name__: cl for cl in [BinTableLists, BinTableNumpy, BinTableBitarray]}
BINTABLE_DEPENDENCY_DICT = {'BinTableBitarray': {'bitarray'}, 'BinTableNumpy': {'numpy'}, 'BinTableLists': set()}


def init_bintable(data: Collection, class_name: str = 'auto') -> 'AbstractBinTable':
    if class_name != 'auto':
        return BINTABLE_CLASSES[class_name](data)

    for class_name, deps in BINTABLE_DEPENDENCY_DICT.items():
        if all([LIB_INSTALLED[lib_name] for lib_name in deps]):
            return BINTABLE_CLASSES[class_name](data)
