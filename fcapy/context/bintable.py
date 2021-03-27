from collections.abc import Iterable
from numbers import Integral


class BinTable:
    def __init__(self, data):
        self._data = data

    @property
    def data(self):
        return self._data

    def __len__(self):
        return len(self._data)

    def __getitem__(self, item):
        if type(item) != tuple:
            row_slice = item
            column_slice = slice(0, self.shape[1])
        else:
            row_slice, column_slice = item

        data = self._data

        def slice_list(lst, slicer):
            if isinstance(slicer, slice):
                lst = lst[slicer]
            elif isinstance(slicer, Iterable):
                lst = [lst[x] for x in slicer]
            else:
                lst = [lst[slicer]]
            return lst

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
        return len(self._data[0])

    @property
    def shape(self):
        return self.height, self.width

    def to_list(self):
        return self._data

    def __eq__(self, other):
        return self._data == other.data

    def __hash__(self):
        return hash(tuple([tuple(row) for row in self._data]))
