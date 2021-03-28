from collections.abc import Iterable
from numbers import Integral
from fcapy.utils.utils import slice_list

from fcapy import LIB_INSTALLED
if LIB_INSTALLED['bitsets']:
    import bitsets


class BinTable:
    def __init__(self, data=None):
        self.data = data

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value: list):
        if value is None or value == []:
            self._data = []
            self._height = 0
            self._width = 0
            return

        assert isinstance(value, list), \
            'BinTable.data.setter: "value" should have type "list"'
        height = len(value)
        assert height > 0, 'BinTable.data.setter: "value" should have length > 0 (use [] for the empty data)'

        assert len({type(row) for row in value}) == 1,\
            'BinTable.data.setter: rows of the given `data` should be of the same type'

        is_bitset = isinstance(value[0], bitsets.bases.BitSet)

        if not is_bitset:
            width = len(value[0])
            for row in value:
                assert len(row) == width, \
                    'BinTable.data.setter: All rows of the "value" should have the same length'
                for column_val in row:
                    assert type(column_val) == bool,\
                        'BinTable.data.setter: "Value" should consist only of boolean number'
        else:
            width = len(value[0].bools())

        if LIB_INSTALLED['bitsets']:
            self._row_members = bitsets.bitset('Rows', range(height)) if height > 0 else None
            self._column_members = bitsets.bitset('Columns', range(width)) if width > 0 else None
            if height > 0 and width > 0:
                if is_bitset:
                    self._data_rows = value
                    self._data_columns = [self._row_members([idx for idx, row in enumerate(value) if j in row])
                                          for j in range(width)]
                else:
                    self._data_rows = [self._column_members.frombools(row) for row in value]
                    self._data_columns = [self._row_members.frombools(column) for column in zip(*value)]
            else:
                self._data_rows = value
                self._data_columns = value
            self._data = self._data_rows
        else:
            self._data = value
        self._height = height
        self._width = width

    def __len__(self):
        return len(self._data)

    def __getitem__(self, item):
        def fix_slice(slc: slice, stop_default: int):
            start = slc.start if slc.start is not None else 0
            stop = slc.stop if slc.stop is not None else stop_default
            return slice(start, stop)

        def slice_to_range(slc: slice):
            return range(slc.start, slc.stop)

        row_slice, column_slice = item if isinstance(item, tuple) else (item, slice(None, None))
        row_slice = fix_slice(row_slice, self._height) if isinstance(row_slice, slice) else row_slice
        column_slice = fix_slice(column_slice, self._width) if isinstance(column_slice, slice) else column_slice

        if isinstance(row_slice, Integral) and isinstance(column_slice, Integral):
            data = self._data[row_slice]

            if LIB_INSTALLED['bitsets']:
                data = (data & (2**column_slice)) > 0
            else:
                data = data[column_slice]
        elif isinstance(row_slice, Integral):
            # therefore column_slice is slice or Iterable
            data = self._data[row_slice]

            if LIB_INSTALLED['bitsets']:
                column_slice = slice_to_range(column_slice) if isinstance(column_slice, slice) else column_slice
                data = data.intersection(column_slice)
            else:
                data = slice_list(data, column_slice)
        elif isinstance(column_slice, Integral):
            # therefore row_slice is slice or Iterable
            if LIB_INSTALLED['bitsets']:
                data = self._data_columns[column_slice]
                row_slice = slice_to_range(row_slice) if isinstance(row_slice, slice) else row_slice
                data = data.intersection(row_slice)
            else:
                data = [row[column_slice] for row in self._data]
                data = data[row_slice]
        else:
            # therefore both row_slice and column_slice are slice or Iterable
            data = slice_list(self._data, row_slice)
            if LIB_INSTALLED['bitsets']:
                column_slice = slice_to_range(column_slice) if isinstance(column_slice, slice) else column_slice
                #data = [row.intersection(column_slice) for row in data]
                data = [slice_list(row.bools(), column_slice) for row in data]
            else:
                data = [slice_list(row, column_slice) for row in data]

            data = BinTable(data)

            def calc_slice_size(slc):
                return slc.stop-slc.start if isinstance(slc, slice) else len(slc)
            data._height = calc_slice_size(row_slice)
            data._width = calc_slice_size(column_slice)

        return data

    @property
    def height(self):
        return self._height

    @property
    def width(self):
        return self._width

    @property
    def shape(self):
        return self.height, self.width

    def to_list(self):
        if LIB_INSTALLED['bitsets']:
            list_data = [list(row.bools()) for row in self._data]
        else:
            list_data = self._data

        return list_data

    def __eq__(self, other):
        return self._data == other.data

    def __hash__(self):
        return hash(tuple([tuple(row) for row in self._data]))

    def all(self, axis=None):
        def check_all_true(ar):
            return ar.all() if LIB_INSTALLED['bitsets'] and isinstance(ar, bitsets.bases.BitSet) else all(ar)

        if axis is None:
            flag_all = True
            for row in self._data:
                if not check_all_true(row):
                    flag_all = False
                    break
        elif axis == 0:
            if self._height == 0 or self._width == 0:
                flag_all = [True for _ in range(self._width)]
            else:
                flag_all = [check_all_true(self[:, j]) for j in range(self.width)]
        elif axis == 1:
            if self._height == 0 or self._width == 0:
                flag_all = [True for _ in range(self._height)]
            else:
                flag_all = [check_all_true(row) for row in self._data]
        else:
            raise ValueError(f"BinTable.all error. `axis` value can only be None, 0 or 1 (got {axis})")

        return flag_all

    def any(self, axis=None):
        if axis is None:
            flag_any = False
            for row in self._data:
                if any(row):
                    flag_any = True
                    break
        elif axis == 0:
            if self._height == 0 or self._width == 0:
                flag_any = [False for _ in range(self._width)]
            else:
                flag_any = [any(self[:, j]) for j in range(self.width)]
        elif axis == 1:
            if self._height == 0 or self._width == 0:
                flag_any = [False for _ in range(self._height)]
            else:
                flag_any = [any(row) for row in self._data]
        else:
            raise ValueError(f"BinTable.all error. `axis` value can only be None, 0 or 1 (got {axis})")

        return flag_any

    def sum(self, axis=None):
        def sum_ar(ar):
            return len(ar) if LIB_INSTALLED['bitsets'] and isinstance(ar, bitsets.bases.BitSet) else sum(ar)

        if axis is None:
            s = sum([sum_ar(row) for row in self._data])
        elif axis == 0:
            if self._height == 0 or self._width == 0:
                s = [0 for _ in range(self._width)]
            else:
                s = [sum_ar(self[:, j]) for j in range(self.width)]
        elif axis == 1:
            if self._height == 0 or self._width == 0:
                s = [0 for _ in range(self._height)]
            else:
                s = [sum_ar(row) for row in self._data]
        else:
            raise ValueError(f"BinTable.all error. `axis` value can only be None, 0 or 1 (got {axis})")

        return s
