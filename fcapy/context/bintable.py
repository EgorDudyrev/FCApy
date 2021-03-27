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

    def __len__(self):
        return len(self._data)

    def __getitem__(self, item):
        if type(item) != tuple:
            row_slice = item
            column_slice = slice(0, self.shape[1])
        else:
            row_slice, column_slice = item

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
        return data

    @property
    def height(self):
        return len(self._data)

    @property
    def width(self):
        return len(self._data[0]) if len(self._data) > 0 else 0

    @property
    def shape(self):
        return self.height, self.width

    def to_list(self):
        return self._data

    def __eq__(self, other):
        return self._data == other.data

    def __hash__(self):
        return hash(tuple([tuple(row) for row in self._data]))
