"""
This module offers a class BinTable to work with binary table efficiently.

"""
from abc import ABCMeta, abstractmethod
from typing import List, Tuple, Optional, Collection, Union

from fcapy.context import bintable_errors as berrors
from fcapy import LIB_INSTALLED
#if LIB_INSTALLED['bitarray']:
from bitarray import frozenbitarray as fbarray, bitarray as barray, util as butil

#if LIB_INSTALLED['numpy']:
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
        return self.__class__([self._get_column(range(self.height), col_i) for col_i in range(self.width)])

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

    @staticmethod
    @abstractmethod
    def _transform_data_fromlists(data: List[List[bool]]) -> Collection[Row_DType]:
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
        if isinstance(data, list) and isinstance(data[0], fbarray):
            return 'BinTableBitarray'
        if isinstance(data, np.ndarray):
            return 'BinTableNumpy'
        if isinstance(data, tuple) and len(data) == 2 and isinstance(data[0], fbitarray) and isinstance(data[1], int):
            return 'BinTableBitarray'

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

    @staticmethod
    def _transform_data_fromlists(data: List[List[bool]]) -> List[Row_DType]:
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

    def all(self, axis: int = None, rows: npt.NDArray[int] = None, columns: npt.NDArray[int] = None)\
            -> Union[bool, Row_DType]:
        if axis not in {None, 0, 1}:
            raise berrors.UnknownAxisError(axis)

        data_slice = self.data
        if rows is not None:
            data_slice = data_slice[rows]
        if columns is not None:
            data_slice = data_slice[:, columns]

        if axis is None:
            return data_slice.all()
        return data_slice.all(axis).flatten()

    def any(self, axis: int = None, rows: npt.NDArray[int] = None, columns: npt.NDArray[int] = None)\
            -> Union[bool, Row_DType]:
        if axis not in {None, 0, 1}:
            raise berrors.UnknownAxisError(axis)

        data_slice = self.data
        if rows is not None:
            data_slice = data_slice[rows]
        if columns is not None:
            data_slice = data_slice[:, columns]

        if axis is None:
            return data_slice.any()
        return data_slice.any(axis).flatten()

    def sum(self, axis: int = None, rows: npt.NDArray[int] = None, columns: npt.NDArray[int] = None) \
            -> Union[bool, Row_DType]:
        if axis not in {None, 0, 1}:
            raise berrors.UnknownAxisError(axis)

        data_slice = self.data
        if rows is not None:
            data_slice = data_slice[rows]
        if columns is not None:
            data_slice = data_slice[:, columns]

        if axis is None:
            return data_slice.sum()
        return data_slice.sum(axis).flatten()

    def all_i(self, axis: int, rows: npt.NDArray[int] = None, columns: npt.NDArray[int] = None) -> npt.NDArray[int]:
        flg_all = self.all(axis, rows, columns)

        if axis == 0:
            full_ar = np.arange(self.width) if columns is None else columns
        else:  # axis == 1
            full_ar = np.arange(self.height) if rows is None else rows

        if not isinstance(full_ar, np.ndarray):
            full_ar = np.array(full_ar)

        return full_ar[flg_all]

    def any_i(self, axis: int, rows: npt.NDArray[int] = None, columns: npt.NDArray[int] = None) -> npt.NDArray[int]:
        flg_any = self.any(axis, rows, columns)

        if axis == 0:
            full_ar = np.arange(self.width) if columns is None else columns
        else:  # axis == 1
            full_ar = np.arange(self.height) if rows is None else rows

        if not isinstance(full_ar, np.ndarray):
            full_ar = np.array(full_ar)

        return full_ar[flg_any]

    def to_list(self) -> List[List[bool]]:
        return self.data.tolist()

    @staticmethod
    def _transform_data_fromlists(data: List[List[bool]]) -> npt.NDArray[bool]:
        return np.array(data)

    def _validate_data(self, data: npt.NDArray[bool]) -> bool:
        if len(data) == 0:
            return True

        if data.dtype != 'bool':
            raise berrors.NotBooleanValueError()

        if len(data.shape) != 2:
            raise berrors.UnmatchedLengthError()

        return True

    # The following function should never be called
    # as everything is implemented in public all(..), any(...), sum(...) functions
    def _all(self, rows: npt.NDArray[int] = None, columns: npt.NDArray[int] = None) -> bool:
        raise NotImplementedError

    def _all_per_row(self, rows: npt.NDArray[int] = None, columns: npt.NDArray[int] = None) -> Row_DType:
        raise NotImplementedError

    def _all_per_column(self, rows: npt.NDArray[int] = None, columns: npt.NDArray[int] = None) -> Row_DType:
        raise NotImplementedError

    def _any(self, rows: npt.NDArray[int] = None, columns: npt.NDArray[int] = None) -> bool:
        raise NotImplementedError

    def _any_per_row(self, rows: npt.NDArray[int] = None, columns: npt.NDArray[int] = None) -> Row_DType:
        raise NotImplementedError

    def _any_per_column(self, rows: npt.NDArray[int] = None, columns: npt.NDArray[int] = None) -> Row_DType:
        raise NotImplementedError

    def _sum(self, rows: npt.NDArray[int] = None, columns: npt.NDArray[int] = None) -> int:
        raise NotImplementedError

    def _sum_per_row(self, rows: npt.NDArray[int] = None, columns: npt.NDArray[int] = None) -> npt.NDArray[int]:
        raise NotImplementedError

    def _sum_per_column(self, rows: npt.NDArray[int] = None, columns: npt.NDArray[int] = None) -> npt.NDArray[int]:
        raise NotImplementedError

    def __eq__(self, other: 'BinTableNumpy'):
        if self.height != other.height:
            return False
        if self.width != other.width:
            return False
        return (self.data == other.data).all()

    def __hash__(self):
        return hash(self.to_tuple())


class BinTableBitarray(AbstractBinTable):
    data: List[fbarray]  # Updating type hint
    Row_DType = fbarray

    def all_i(self, axis: int, rows: List[int] = None, columns: List[int] = None) -> List[int]:
        flg_all = self.all(axis, rows, columns)

        idxs = flg_all.itersearch(1)
        if axis == 0:
            output = [columns[i] for i in idxs] if columns is not None else list(idxs)
        else:  # axis == 1
            output = [rows[i] for i in idxs] if rows is not None else list(idxs)
        return output

    def any_i(self, axis: int, rows: List[int] = None, columns: List[int] = None) -> List[int]:
        flg_any = self.any(axis, rows, columns)

        idxs = flg_any.itersearch(1)
        if axis == 0:
            output = [columns[i] for i in idxs] if columns is not None else list(idxs)
        else:  # axis == 1
            output = [rows[i] for i in idxs] if rows is not None else list(idxs)
        return output

    @staticmethod
    def _transform_data_fromlists(data: List[List[bool]]) -> List[Row_DType]:
        return [fbarray(row) for row in data]

    def _validate_data(self, data: List[fbarray]) -> bool:
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
            mask = fbarray([j not in columns for j in range(self.width)])

            for i in rows:
                row = self.data[i]
                if not (row | mask).all():
                    return False

        return True

    def _all_per_row(self, rows: List[int] = None, columns: List[int] = None) -> Row_DType:
        rows = range(self.height) if rows is None else rows
        if columns is None:
            return fbarray([self.data[i].all() for i in rows])

        columns = set(columns)
        mask = fbarray([j not in columns for j in range(self.width)])

        return fbarray([(self.data[i] | mask).all() for i in rows])

    def _all_per_column(self, rows: List[int] = None, columns: List[int] = None) -> Row_DType:
        rows = range(self.height) if rows is None else rows
        vals = ~butil.zeros(self.width)
        if columns is None:
            for i in rows:
                vals &= self.data[i]
                if not vals.any():  # If all values are False
                    break
        else:
            columns_set = set(columns)
            mask = fbarray([j in columns_set for j in range(self.width)])
            for i in rows:
                vals &= self.data[i]
                if not (vals & mask).any():  # If all values are False
                    break

            vals = fbarray([vals[i] for i in columns])
        return vals

    def _any(self, rows: List[int] = None, columns: List[int] = None) -> bool:
        rows = range(self.height) if rows is None else rows
        if columns is None:
            for i in rows:
                if self.data[i].any():
                    return True
        else:
            columns = set(columns)
            mask = fbarray([j in columns for j in range(self.width)])

            for i in rows:
                if (self.data[i] & mask).any():
                    return True

        return False

    def _any_per_row(self, rows: List[int] = None, columns: List[int] = None) -> Row_DType:
        rows = range(self.height) if rows is None else rows
        if columns is None:
            return fbarray([self.data[i].any() for i in rows])

        columns = set(columns)
        mask = fbarray([j in columns for j in range(self.width)])
        return fbarray([(self.data[i] & mask).any() for i in rows])

    def _any_per_column(self, rows: List[int] = None, columns: List[int] = None) -> Row_DType:
        rows = range(self.height) if rows is None else rows

        vals = butil.zeros(self.width)
        if columns is None:
            for i in rows:
                vals |= self.data[i]
                if vals.all():
                    break
        else:
            columns_set = set(columns)
            mask = fbarray([j not in columns_set for j in range(self.width)])

            for i in rows:
                vals |= self.data[i]
                if (vals | mask).all():
                    break

            vals = fbarray([vals[i] for i in columns])
        return vals

    def _sum(self, rows: List[int] = None, columns: List[int] = None) -> int:
        return sum(self._sum_per_row(rows, columns))

    def _sum_per_row(self, rows: List[int] = None, columns: List[int] = None) -> List[int]:
        rows = range(self.height) if rows is None else rows
        if columns is None:
            return [self.data[i].count() for i in rows]

        columns = set(columns)
        mask = fbarray([j in columns for j in range(self.width)])
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
            mask = fbarray([j in columns_set for j in range(self.width)])
            for i in rows:
                for j in (self.data[i] & mask).search(1):
                    vals[j] += 1

        return vals

    def _get_row(self, row_idx: int, column_slicer: List[int] or slice = None) -> Row_DType:
        row = self.data[row_idx]
        if column_slicer:
            if isinstance(column_slicer, slice):
                return row[column_slicer]
            return fbarray([row[col_i] for col_i in column_slicer])
        return row

    def _get_column(self, row_slicer: List[int] or slice, column_idx: int) -> Row_DType:
        if isinstance(row_slicer, slice):
            row_slicer = range(*row_slicer.indices(self.height))
        return fbarray([self._data[row_i][column_idx] for row_i in row_slicer])

    def _get_subtable(self, row_slicer: List[int] or slice, column_slicer: List[int] or slice or None) \
            -> 'BinTableBitarray':
        if isinstance(row_slicer, slice):
            row_slicer = range(*row_slicer.indices(self.height))

        if column_slicer is None:
            subtable = [self.data[row_i] for row_i in row_slicer]
        elif isinstance(column_slicer, slice):
            subtable = [self.data[row_i][column_slicer] for row_i in row_slicer]
        else:
            subtable = [fbarray([self.data[row_i][col_i] for col_i in column_slicer]) for row_i in row_slicer]

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


class BinTableOneBitarray(AbstractBinTable):
    """WORK IN PROGRESS"""

    data: Tuple[fbarray, int]  # Updating type hint  (bitarray, number of rows)
    Row_DType = fbarray

    @property
    def T(self) -> 'BinTableOneBitarray':
        bars_trans = [self.data[0][j::self.width] for j in range(self.width)]
        data_T = self._transform_data_fromlists(bars_trans)
        return self.__class__(data_T)

    def all_i(self, axis: int, rows: List[int] = None, columns: List[int] = None) -> List[int]:
        flg_all = self.all(axis, rows, columns)

        idxs = flg_all.itersearch(1)  # Use itersearch to speed up obtaining the indices
        if axis == 0 and columns is not None:
            output = (columns[i] for i in idxs)
        elif axis == 1 and rows is not None:
            output = (rows[i] for i in idxs)
        else:
            output = idxs
        return list(output)

    def any_i(self, axis: int, rows: List[int] = None, columns: List[int] = None) -> List[int]:
        flg_any = self.any(axis, rows, columns)

        idxs = flg_any.itersearch(1)  # Use itersearch to speed up obtaining the indices
        if axis == 0 and columns is not None:
            output = (columns[i] for i in idxs)
        elif axis == 1 and rows is not None:
            output = (rows[i] for i in idxs)
        else:
            output = idxs
        return list(output)

    @staticmethod
    def _transform_data_inherent(data) -> Tuple[Collection, int, int]:
        return data, data[1], len(data[0])//data[1]

    @staticmethod
    def _transform_data_fromlists(data: List[List[bool]]) -> Tuple[fbarray, int]:
        h, w = len(data), len(data[0])
        bar = butil.zeros(h*w)

        offset = 0
        for i in range(h):
            bar[offset:offset + w] |= fbarray(data[i])
            offset += w

        return fbarray(bar), h

    def _validate_data(self, data: Tuple[fbarray, int]) -> bool:
        bar, h = data
        if len(bar) == 0:
            return True

        w = len(bar) / h
        if int(w) != w:
            raise berrors.UnmatchedLengthError()

        return True

    def _all(self, rows: List[int] = None, columns: List[int] = None) -> bool:
        if rows is None and columns is None:
            return self.data[0].all()

        # at least one of `rows` and `columns` is given

        if rows is None:  # i.e. only columns are given
            iterator = (self._get_column(rows, j) for j in columns)
        elif columns is None:  # i.e. only rows are given
            iterator = (self._get_row(i, columns) for i in rows)
        else:  # if both rows and columns are given
            iterator = (self._get_row(i, columns) for i in rows)

        for bar in iterator:
            if not bar.all():
                return False

        return True

    def _all_per_row(self, rows: List[int] = None, columns: List[int] = None) -> Row_DType:
        rows = range(self.height) if rows is None else rows

        return fbarray([self._get_row(i, columns).all() for i in rows])

    def _all_per_column(self, rows: List[int] = None, columns: List[int] = None) -> Row_DType:
        columns = range(self.width) if columns is None else columns

        return fbarray([self._get_column(rows, j).all() for j in columns])

    def _any(self, rows: List[int] = None, columns: List[int] = None) -> bool:
        if rows is None and columns is None:
            return self.data[0].any()

        # at least one of `rows` and `columns` is given

        if rows is None:  # i.e. only columns are given
            iterator = (self._get_column(rows, j) for j in columns)
        elif columns is None:  # i.e. only rows are given
            iterator = (self._get_row(i, columns) for i in rows)
        else:  # if both rows and columns are given
            iterator = (self._get_row(i, columns) for i in rows)

        for bar in iterator:
            if bar.any():
                return True

        return False

    def _any_per_row(self, rows: List[int] = None, columns: List[int] = None) -> Row_DType:
        rows = range(self.height) if rows is None else rows

        return fbarray([self._get_row(i, columns).any() for i in rows])

    def _any_per_column(self, rows: List[int] = None, columns: List[int] = None) -> Row_DType:
        columns = range(self.width) if columns is None else columns

        return fbarray([self._get_column(rows, j).any() for j in columns])

    def _sum(self, rows: List[int] = None, columns: List[int] = None) -> int:
        if rows is None and columns is None:
            return self.data[0].count()

        # at least one of `rows` and `columns` is given

        if rows is None:  # i.e. only columns are given
            iterator = (self._get_column(rows, j) for j in columns)
        elif columns is None:  # i.e. only rows are given
            iterator = (self._get_row(i, columns) for i in rows)
        else:  # if both rows and columns are given
            iterator = (self._get_row(i, columns) for i in rows)

        return sum((bar.count() for bar in iterator))

    def _sum_per_row(self, rows: List[int] = None, columns: List[int] = None) -> List[int]:
        rows = range(self.height) if rows is None else rows

        return [self._get_row(i, columns).count() for i in rows]

    def _sum_per_column(self, rows: List[int] = None, columns: List[int] = None) -> List[int]:
        columns = range(self.width) if columns is None else columns

        return [self._get_column(rows, j).count() for j in columns]

    def _get_row(self, row_idx: int, column_slicer: List[int] or slice or None = None) -> Row_DType:
        row = self.data[0][row_idx*self.width][:self.width]

        if column_slicer is None:
            return row

        if isinstance(column_slicer, slice):
            return row[column_slicer]

        return fbarray([row[col_i] for col_i in column_slicer])

    def _get_column(self, row_slicer: List[int] or slice or None, column_idx: int) -> Row_DType:
        column = self.data[0][column_idx::self.width]

        if row_slicer is None:
            return column

        if isinstance(row_slicer, slice):
            return column[row_slicer]

        return fbarray([column[row_i] for row_i in row_slicer])

    def _get_subtable(self, row_slicer: List[int] or slice or None, column_slicer: List[int] or slice or None) \
            -> 'BinTableOneBitarray':
        if row_slicer is None and column_slicer is None:
            return self.__class__(self.data)

        if isinstance(row_slicer, slice):
            row_slicer = range(*row_slicer.indices(self.height))
        subtable = [self._get_row(row_i, column_slicer) for row_i in row_slicer]
        return self.__class__((subtable, len(row_slicer)))

    def __eq__(self, other: 'BinTableOneBitarray'):
        if self.height != other.height:
            return False
        if self.width != other.width:
            return False
        return self.data[0] == other.data[0]

    def __hash__(self):
        return hash(self.data)

    def __and__(self, other: 'BinTableOneBitarray') -> 'BinTableOneBitarray':
        return self.__class__((self.data[0] & other.data[0], self.data[1]))

    def __or__(self, other: 'BinTableOneBitarray') -> 'BinTableOneBitarray':
        return self.__class__((self.data[0] | other.data[0], self.data[1]))

    def __invert__(self) -> 'BinTableOneBitarray':
        return self.__class__((~self.data[0], self.data[1]))


BINTABLE_CLASSES = {cl.__name__: cl for cl in [
    BinTableLists, BinTableNumpy, BinTableBitarray,  # BinTableOneBitarray
]}
BINTABLE_DEPENDENCY_DICT = {
    'BinTableBitarray': {'bitarray'},
    'BinTableNumpy': {'numpy'},
    'BinTableLists': set(),
    # 'BinTableOneBitarray': {'bitarray'},
}


def init_bintable(data: Collection, class_name: str = 'auto') -> 'AbstractBinTable':
    if class_name == 'auto':
        for class_name, deps in BINTABLE_DEPENDENCY_DICT.items():
            if all([LIB_INSTALLED[lib_name] for lib_name in deps]):
                return BINTABLE_CLASSES[class_name](data)

    if data.__class__.__name__ == class_name:
        return data

    if isinstance(data, AbstractBinTable):  # convert data from one BinTable class to another
        return BINTABLE_CLASSES[class_name](data.data)

    return BINTABLE_CLASSES[class_name](data)
