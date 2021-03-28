from collections.abc import Iterable
from numbers import Integral
from fcapy.utils.utils import slice_list


class BinTable:
    def __init__(self, data=None):
        self.data = data

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        if value is None or value == []:
            self._data = []
            self._height = 0
            self._width = 0
            return

        assert isinstance(value, list), \
            'BinTable.data.setter: "value" should have type "list"'
        assert len(value) > 0, 'BinTable.data.setter: "value" should have length > 0 (use [] for the empty data)'

        width = len(value[0])
        for row in value:
            assert len(row) == width, \
                'BinTable.data.setter: All rows of the "value" should have the same length'
            for column_val in row:
                assert type(column_val) == bool, 'BinTable.data.setter: "Value" should consist only of boolean number'

        self._data = value
        self._height = len(value)
        self._width = width

    def __len__(self):
        return len(self._data)

    def __getitem__(self, item):
        def fix_slice(slc: slice, stop_default: int):
            start = slc.start if slc.start is not None else 0
            stop = slc.stop if slc.stop is not None else stop_default
            return slice(start, stop)
        row_slice, column_slice = item if isinstance(item, tuple) else (item, slice(None, None))
        row_slice = fix_slice(row_slice, self._height) if isinstance(row_slice, slice) else row_slice
        column_slice = fix_slice(column_slice, self._width) if isinstance(column_slice, slice) else column_slice

        data = self._data

        if isinstance(row_slice, Integral) and isinstance(column_slice, Integral):
            data = data[row_slice][column_slice]
        elif isinstance(row_slice, Integral):
            # therefore column_slice is slice or Iterable
            data = data[row_slice]
            data = slice_list(data, column_slice)
        elif isinstance(column_slice, Integral):
            # therefore row_slice is slice or Iterable
            data = [row[column_slice] for row in data]
            data = data[row_slice]
        else:
            # therefore both row_slice and column_slice are slice or Iterable
            data = slice_list(data, row_slice)
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
        return self._data

    def __eq__(self, other):
        return self._data == other.data

    def __hash__(self):
        return hash(tuple([tuple(row) for row in self._data]))

    def all(self, axis=None):
        if axis is None:
            flag_all = True
            for row in self._data:
                if not all(row):
                    flag_all = False
                    break
        elif axis == 0:
            if self._height == 0 or self._width == 0:
                flag_all = [True for _ in range(self._width)]
            else:
                flag_all = [all(self[:, j]) for j in range(self.width)]
        elif axis == 1:
            if self._height == 0 or self._width == 0:
                flag_all = [True for _ in range(self._height)]
            else:
                flag_all = [all(row) for row in self._data]
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
