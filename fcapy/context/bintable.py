"""
This module offers a class BinTable to work with binary table efficiently.

"""
from numbers import Integral
from fcapy.utils.utils import slice_list

from fcapy import LIB_INSTALLED
if LIB_INSTALLED['bitsets']:
    import bitsets


class BinTable:
    """
    A class to encapsulate the work with binary tables in an efficient way

    Methods
    -------
    all(self, axis=None)  :noindex:
        Return whether all elements (``axis`` =0), rows in columns (``axis`` =1), columns in rows (``axis`` =2) are True
    any(self, axis=None)  :noindex:
        Return whether any element (``axis`` =0), row in columns (``axis`` =1), column in rows (``axis`` =2) is True
    sum(self, axis=None)  :noindex
        Return sum of all elements (``axis`` =0), rows in columns (``axis`` =1), columns in rows (``axis`` =2)
    arrow_up(self, row_indexes, base_columns=None)  :noindex:
        Return the maximal set of columns in which all rows (``row_indexes``) are True
    arrow_down(self, column_indexes, base_rows=None)  :noindex:
        Return the maximal set of rows in which all columns (``column_indexes``) are True

    """
    def __init__(self, data=None):
        """Initialize the BinTable

        Parameters
        ----------
        data: `list` of `list` or `bitsets.bases.BitSets`
            Data for the BinTable to store

        """
        self.data = data

    @property
    def data(self):
        """Data for the BinTable to store"""
        return self._data

    @data.setter
    def data(self, value: list):
        """Set the data property of BinTable"""
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
        """Compute length of a table, i.e. a number of rows"""
        return len(self._data)

    def __getitem__(self, item):
        """Select either a subset of a BinTable if ``item`` is a `slice` or a single row/column if ``item`` is `int`"""
        def fix_slice(slc: slice, stop_default: int):
            start = slc.start if slc.start is not None else 0
            stop = slc.stop if slc.stop is not None else stop_default
            return slice(start, stop)

        def slice_to_range(slc: slice):
            return range(slc.start, slc.stop)

        def is_slice_number(slc):
            return isinstance(slc, Integral) and not isinstance(slc, bitsets.bases.BitSet)

        row_slice, column_slice = item if isinstance(item, tuple) else (item, slice(None, None))
        row_slice = fix_slice(row_slice, self._height) if isinstance(row_slice, slice) else row_slice
        column_slice = fix_slice(column_slice, self._width) if isinstance(column_slice, slice) else column_slice

        is_row_slice_number = is_slice_number(row_slice)
        is_column_slice_number = is_slice_number(column_slice)
        if is_row_slice_number and is_column_slice_number:
            data = self._data[row_slice]

            if LIB_INSTALLED['bitsets']:
                data = (data & (2**column_slice)) > 0
            else:
                data = data[column_slice]

        elif is_row_slice_number:
            # therefore column_slice is slice or Iterable
            data = self._data[row_slice]

            if LIB_INSTALLED['bitsets']:
                column_slice = slice_to_range(column_slice) if isinstance(column_slice, slice) else column_slice
                data = data.intersection(column_slice)
            else:
                data = slice_list(data, column_slice)

        elif is_column_slice_number:
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
        """Number of rows in the table"""
        return self._height

    @property
    def width(self):
        """Number of columns in the table"""
        return self._width

    @property
    def shape(self):
        """Shape of the table"""
        return self.height, self.width

    def to_list(self):
        """Return BinTable data as a `list` of `list`"""
        if LIB_INSTALLED['bitsets']:
            list_data = [list(row.bools()) for row in self._data]
        else:
            list_data = self._data

        return list_data

    def __eq__(self, other):
        """Compare is this BinTable is equal to the ``other`` """
        return self._data == other.data

    def __hash__(self):
        return hash(tuple([tuple(row) for row in self._data]))

    def all(self, axis=None):
        """Check if all rows in columns (``axis`` =1), columns in rows (``axis`` =2), or both (``axis`` =0) are True"""
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
                if LIB_INSTALLED['bitsets']:
                    flag_all = self._data_rows[0]
                    for row in self._data_rows[1:]:
                        flag_all &= row
                    flag_all = list(self._column_members.fromint(flag_all).bools())
                else:
                    flag_all = [all(self[:, j]) for j in range(self.width)]
        elif axis == 1:
            if self._height == 0 or self._width == 0:
                flag_all = [True for _ in range(self._height)]
            else:
                if LIB_INSTALLED['bitsets']:
                    flag_all = self._data_columns[0]
                    for column in self._data_columns[1:]:
                        flag_all &= column
                    flag_all = list(self._row_members.fromint(flag_all).bools())
                else:
                    flag_all = [all(row) for row in self._data]
        else:
            raise ValueError(f"BinTable.all error. `axis` value can only be None, 0 or 1 (got {axis})")

        return flag_all

    def any(self, axis=None):
        """Check if any element (``axis`` =0), row in columns (``axis`` =1), column in rows (``axis`` =2) is True"""
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
        """Return sum of all elements (``axis`` =0), rows in columns (``axis`` =1), columns in rows (``axis`` =2)"""
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

    def arrow_up(self, row_indexes, base_columns=None):
        """Return the maximal set of columns in which all rows (``row_indexes``) are True

        Parameters
        ----------
        row_indexes: `list` of `int`
            Indexes of rows to process
        base_columns: `list` or `int`
            List of columns to select ''arrowed up'' columns from. Default value: all the columns.

        Returns
        -------
        columns: `list` of `int`
        """
        if LIB_INSTALLED['bitsets']:
            if len(row_indexes) > 0:
                columns = self._column_members(base_columns) if base_columns is not None else None
                for row_i in row_indexes:
                    if columns is None:
                        columns = self._data_rows[row_i]
                    else:
                        columns &= self._data_rows[row_i]

                    if columns == 0:
                        break
                columns = self._column_members.fromint(columns)

            else:
                base_columns = range(self._width) if base_columns is None else base_columns
                columns = self._column_members(base_columns)

        else:
            base_columns = range(self._width) if base_columns is None else base_columns
            columns = list(base_columns)
            for row_i in row_indexes:
                column_vals = slice_list(self._data[row_i], columns)
                columns = [col_i for col_i, col_val in zip(columns, column_vals) if col_val]
                if len(columns) == 0:
                    break

        return columns

    def arrow_down(self, column_indexes, base_rows=None):
        """Return the maximal set of rows in which all columns (``column_indexes``) are True

        Parameters
        ----------
        column_indexes: `list` of `int`
            Indexes of columns to process
        base_rows: `list` or `int`
            List of rows to select ''arrowed down'' rows from. Default value: all the rows.

        Returns
        -------
        rows: `list` of `int`
        """
        if LIB_INSTALLED['bitsets']:
            if len(column_indexes) > 0:
                rows = self._row_members(base_rows) if base_rows is not None else None
                for column_i in column_indexes:
                    if rows is None:
                        rows = self._data_columns[column_i]
                    else:
                        rows &= self._data_columns[column_i]

                    if rows == 0:
                        break
                rows = self._row_members.fromint(rows)
            else:
                base_rows = range(self._height) if base_rows is None else base_rows
                rows = self._row_members(base_rows)

        else:
            base_rows = range(self._height) if base_rows is None else base_rows
            rows = list(base_rows)
            for column_i in column_indexes:
                row_vals = [row[column_i] for row in slice_list(self._data, rows)]
                rows = [row_i for row_i, row_val in zip(rows, row_vals) if row_val]
                if len(rows) == 0:
                    break

        return rows
