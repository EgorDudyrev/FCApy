"""
This is the main module of subpackage `context`.
It contains a class FormalContext which represents a Formal Context object from FCA theory

"""
from itertools import combinations
from numbers import Integral
from typing import Tuple, Iterable, List, Collection, Set, Union

from frozendict import frozendict
import zlib

from fcapy.context.bintable import init_bintable, BINTABLE_CLASSES, AbstractBinTable
from fcapy.utils.utils import slice_list


class FormalContext:
    """
    A class used to represent Formal Context object from FCA theory.

    Methods
    -------
    intention(objects)  :noindex:
        Return maximal set of attributes which are shared by given ``objects``
    extension(attributes)  :noindex:
        Return maximal set of objects which share given ``attributes``
    intention_i(object_indexes)  :noindex:
        Offer the same logic as intention(...) but objects and attributes are defined by their indexes
    extension_i(attribute_indexes)  :noindex:
        Offer the same logic as extension(...) but objects and attributes are defined by their indexes

    write_cxt(path=None)  :noindex:
        Convert the FormalContext into cxt file format (save if ``path`` is given)
    write_json(path=None)  :noindex:
        Convert the FormalContext into json file format (save if ``path`` is given)
    write_csv(path=None, **kwargs)  :noindex:
        Convert the FormalContext into csv file format (save if ``path`` is given)
    to_pandas()  :noindex:
        Convert the FormalContext into pandas.DataFrame object

    Notes
    -----
    Formal Context K = (G, M, I) - is a triplet of:
    1. set of objects G (the property ``object_names`` in this class)
    2. set of attributes M (the property ``attribute_names`` in this class)
    3. binary relation I between G and M (i.e. "gIm holds True" means "object g has an attribute m")
     (the property ``data`` in this class)

    """
    def __init__(
            self, data: Collection[bool] or AbstractBinTable = None, object_names=None, attribute_names=None,
            description: str = None, target=None, backend: BINTABLE_CLASSES = 'auto'
    ):
        """
        Parameters
        ----------
        data : `list` of `list`
            Two dimensional list of bool variables.
            "data[i][j] = True" represents that i-th object shares j-th attribute
        object_names : `list` of `str`, optional
            Names of objects (rows) of the FormalContext
        attribute_names : `list` of `str`, optional
            Names of attributes (columns) of the FormalContext
        description: `str`, optional
            Human readable description of the FormalContext (stored only in json file format)
        backend: `str`, optional
            Name of BinTable class to work with data

        """
        self._data = init_bintable(data, backend)
        self.object_names = object_names
        self.attribute_names = attribute_names
        self.description = description
        self._target = target

    @property
    def data(self) -> AbstractBinTable:
        """Get or set the data with relations between objects and attributes (`list` of `list`)

        Parameters
        ----------
        value : `list` of `list`
            value[i][j] represents whether i-th object shares j-th attribute

        Raises
        ------
        AssertionError
            If ``value`` is not a `list`
            If ``value`` of type `list` is given (should be `list` of `list`)
            If some lists ``value[i]`` and ``value[j]`` have different length (should be the same for any ``value[i]``)
            If any ``value[i][j]`` is not of type `bool`

        """
        return self._data

    @property
    def object_names(self) -> List[str]:
        """Get or set the names of the objects in the context

        Parameters
        ----------
        value : `list` of `str`
            The list of names for the objects (default are '0','1',...,'`n_objects`-1')

        Raises
        ------
        AssertionError
            If the number of names in the ``value`` does not equal to the number of objects in the context
            If the the elements of ``value`` are not of type str

        """
        return self._object_names

    @object_names.setter
    def object_names(self, value):
        """Set the names of objects in the context"""
        if self.data is None:
            self._object_names = None
            self._object_names_i_map = None

        if value is None:
            self._object_names = tuple([str(idx) for idx in range(self.n_objects)])
        else:
            value = tuple(value)

            assert len(value) == len(self._data),\
                'FormalContext.object_names.setter: Length of "value" should match length of data'
            assert all(type(name) == str for name in value),\
                'FormalContext.object_names.setter: Object names should be of type str'
            self._object_names = value

        self._object_names_i_map = frozendict({name: idx for idx, name in enumerate(self._object_names)})

    @property
    def attribute_names(self) -> List[str]:
        """Get or set the names of the attributes in the context

        Parameters
        ----------
        value : `list` of `str`
            The list of names for the attributes (default are "0","1",...,"`n_attributes`-1")

        Raises
        ------
        AssertionError
            If the number of names in the ``value`` does not equal to the number of attributes in the context
            If the the elements of ``value`` are not of type str

        """
        return self._attribute_names

    @attribute_names.setter
    def attribute_names(self, value):
        """Set the names of the attributes in the context"""
        if self.data is None:
            self._attribute_names = None
            self._attribute_names_i_map = None
            return

        if value is None:
            self._attribute_names = tuple([str(idx) for idx in range(self.n_attributes)])
        else:

            value = tuple(value)

            assert len(value) == self._data.shape[1],\
                'FormalContext.attribute_names.setter: Length of "value" should match number of columns in ``data``'
            assert all(type(name) == str for name in value),\
                'FormalContext.object_names.setter: Object names should be of type str'
            self._attribute_names = value

        self._attribute_names_i_map = {name: idx for idx, name in enumerate(self._attribute_names)}

    @property
    def target(self):
        """A set of target values for supervised ML tasks"""
        return self._target

    @property
    def backend(self) -> str:
        return type(self.data).__name__

    def extension_i(self, attribute_indexes: Collection[int], base_objects_i: Collection[int] = None) -> List[int]:
        """Return indexes of maximal set of objects which share given ``attribute_indexes``

        Parameters
        ----------
        attribute_indexes : `list` of `int`
            Indexes of the attributes (from [0, ``n_attributes``-1])
        base_objects_i : `list` of `int`
            Indexes of set of objects on which to look for extension_i
        Returns
        -------
        extension_indexes : `tuple` of `int`
            Indexes of maximal set of objects which share ``attribute_indexes``

        """
        if len(attribute_indexes) == 0:
            return list(range(self.n_objects)) if base_objects_i is None else list(base_objects_i)

        attribute_indexes = list(attribute_indexes)

        return list(self.data.all_i(1, base_objects_i, attribute_indexes))

    def extension_monotone_i(self, attribute_indexes: Collection[int], base_objects_i: Collection[int] = None)\
            -> List[int]:
        if len(attribute_indexes) == self.n_attributes:
            return list(range(self.n_objects)) if base_objects_i is None else base_objects_i

        return list(self.data.any_i(1, base_objects_i, attribute_indexes))

    def extension(self, attributes: Collection[str], base_objects: Collection[str] = None, is_monotone: bool = False)\
            -> List[str]:
        """Return maximal set of objects which share given ``attributes``

        Parameters
        ----------
        attributes : `list` of `str`
            Names of the attributes (subset of ``attribute_names``)
        base_objects : `list` of `str`
            Set of objects to look for extension on. Default value: all the objects.
        is_monotone: `bool` (def. False)
            A flag whether to use antimonotone extension (as default) or the monotone one
        Returns
        -------
        extension : `tuple` of `str`
            Names of the maximal set of objects which share given ``attributes``

        """
        attr_indices = []
        for m in attributes:
            try:
                attr_indices.append(self._attribute_names_i_map[m])
            except KeyError as e:
                raise KeyError(f'FormalContext.extension: Context does not have an attribute "{m}"')

        if base_objects is not None:
            base_objects_i = []
            for g in base_objects:
                try:
                    base_objects_i.append(self._object_names_i_map[g])
                except KeyError as e:
                    raise KeyError(f'FormalContext.extension: Context does not have an object "{g}"')
        else:
            base_objects_i = list(range(self.n_objects))

        extension_i = self.extension_i(attr_indices, base_objects_i)\
            if not is_monotone else self.extension_monotone_i(attr_indices, base_objects_i)
        extension = [self._object_names[g_idx] for g_idx in extension_i]
        return extension

    def intention_i(self, object_indexes: Iterable[int], base_attrs_i: Iterable[int] = None) -> List[int]:
        """Return indexes of maximal set of attributes which are shared by given ``object_indexes``

        Parameters
        ----------
        object_indexes : `list` of `int`
            Indexes of the objects (from [0, ``n_objects``-1])
        base_attrs_i : `list` of `int`
            Indexes of attribute indexes to compute the intention on. Default value: indexes of all the attributes

        Returns
        -------
        intention_i : `tuple` of `int`
            Indexes of maximal set of attributes which are shared by ``objects_indexes``

        """
        if len(object_indexes) == 0:
            return list(range(self.n_attributes)) if base_attrs_i is None else list(base_attrs_i)

        object_indexes = list(object_indexes)
        return list(self.data.all_i(0, object_indexes, base_attrs_i))

    def intention_monotone_i(self, object_indexes: Iterable[int], base_attrs_i: Iterable[int] = None)\
            -> List[int]:
        """Return indexes of maximal set of attributes shared by any of given ``object_indexes``"""
        attr_iterator = range(self.n_attributes) if base_attrs_i is None else base_attrs_i

        if len(object_indexes) == self.n_objects:
            return list(attr_iterator)

        object_indexes = set(object_indexes)
        inv_objs_i = [g_i for g_i in range(self.n_objects) if g_i not in object_indexes]
        inv_attrs_i = set(self.data.any_i(0, inv_objs_i, base_attrs_i))
        return [m_i for m_i in attr_iterator if m_i not in inv_attrs_i]

    def intention(self, objects: Iterable[str], is_monotone: bool = False) -> List[str]:
        """Return maximal set of attributes which are shared by given ``objects``

        Parameters
        ----------
        objects : `list` of `str`
            Names of the objects (subset of ``object_names``)
        is_monotone: `bool` (def. False)
            Return monotone intention if set True else return antimonotone intention (as in classical FCA)

        Returns
        -------
        intention: `list` of `str`
            Names of maximal set of attributes which are shared by given ``objects``


        Notes
        -----
        Antimonotone intention views the common description of objects as intersection of their descriptions.
        That is, an attribute belongs to antimonotone intention if it is shared by _all_ the given objects.

        Monotone intention view the common description of objects as union of their descriptions.
        So, an attribute belongs to monotone intention if it is shared by _any_ of the given objects.
        """
        obj_indices = []
        for g in objects:
            try:
                obj_indices.append(self._object_names_i_map[g])
            except KeyError as e:
                raise KeyError(f'FormalContext.intention: Context does not have an object "{g}"')

        intention_i = self.intention_i(obj_indices) if not is_monotone else self.intention_monotone_i(obj_indices)
        intention = [self._attribute_names[m_idx] for m_idx in intention_i]
        return intention

    @property
    def n_objects(self) -> int:
        """Get the number of objects in the context (i.e. len(`data`))"""
        return self.data.height

    @property
    def n_attributes(self) -> int:
        """Get the number of attributes in the context (i.e. len(`data[0]`)"""
        return self.data.width

    @property
    def size(self) -> Tuple[int, int]:
        """Get the size of the context (num. of objects and num. of attributes)"""
        return self.data.height, self.data.width

    @property
    def description(self) -> str:
        """Get or set the human readable description of the context

        JSON is the only file format to store this information.
        The description will be lost when saving context to .cxt or .csv

        Parameters
        ----------
        value : `str` or None
            The human readable description of the context

        Raises
        ------
        AssertionError
            If the given ``value`` is not None and not of type `str`

        """
        return self._description

    @description.setter
    def description(self, value):
        """Set the description of the context"""
        assert isinstance(value, (type(None), str)), 'FormalContext.description: Description should be of type `str`'

        self._description = value

    @property
    def T(self) -> 'FormalContext':
        """Transpose the context"""
        return self.__class__(self.data.T.data, self.attribute_names, self.object_names, backend=self.backend)

    def write_cxt(self, path=None):
        """Convert the FormalContext into cxt file format (save if ``path`` is given)

        Parameters
        ----------
        path : `str` or None
            Path to save a context

        Returns
        -------
        context : `str`
            If ``path`` is None, the string with .cxt file data is returned. If ``path`` is given - return None

        """
        from fcapy.context.converters import write_cxt
        return write_cxt(self, path)

    @staticmethod
    def read_cxt(path=None, data=None):
        """Read the context from .cxt file placed in ``path`` or from the .cxt formatted ``data``"""
        from fcapy.context.converters import read_cxt
        return read_cxt(path, data)

    def write_json(self, path=None):
        """Convert the FormalContext into json file format (save if ``path`` is given)

        Parameters
        ----------
        path : `str` or None
            Path to save a context

        Returns
        -------
        context : `str`
            If ``path`` is None, the string with .json file data is returned. If ``path`` is given - return None

        """
        from fcapy.context.converters import write_json
        return write_json(self, path)

    @staticmethod
    def read_json(path=None, data=None):
        from fcapy.context.converters import read_json
        return read_json(path, data)

    def write_csv(self, path=None, **kwargs):
        """Convert the FormalContext into csv file format (save if ``path`` is given)

        Parameters
        ----------
        path : `str` or None
            Path to save a context
        **kwargs :
            ``sep`` : `str`
                Field delimiter for the output file
            ``word_true`` : `str`
                A placeholder to put instead of 'True' for data[i][j]==True (default 'True')
            ``word_false`` : `str`
                A placeholder to put instead of 'False' for data[i][j]==False (default 'False')

        Returns
        -------
        context : `str`
            If ``path`` is None, the string with .csv file data is returned. If ``path`` is given - return None

        """
        from fcapy.context.converters import write_csv
        return write_csv(self, path=path, **kwargs)

    @staticmethod
    def read_csv(path, sep=',', word_true='True', word_false='False'):
        """Read the context from .csv file placed in ``path`` or from the .csv formatted ``data``

        Parameters
        ----------
        path: `str`
            Path to the file to load
        sep: `str`
            A separator used in .csv file
        word_true: `str`
            A placeholder for True values used in .csv file
        word_false: `str`
            A placeholder for False values used in .csv file

        Returns
        -------
        `FormalContext` loaded from .csv file
        """
        """"""

        from fcapy.context.converters import read_csv
        return read_csv(path, sep, word_true, word_false)

    def to_pandas(self):
        """Convert the FormalContext into pandas.DataFrame object

        Returns
        -------
        df : `pandas.DataFrame`
            The dataframe with boolean variables,
            ``object_names`` turned into ``df.index``, ``attribute_names`` turned into ``df.columns``

        """
        from fcapy.context.converters import to_pandas
        return to_pandas(self)

    @staticmethod
    def from_pandas(dataframe):
        """Construct a FormalContext from a binarized pandas dataframe

        Parameters
        ----------
        dataframe : `pandas.DataFrame`
            The dataframe with boolean values to construct a FormalContext

        Returns
        -------
        context : `FormalContext`
            A FormalContext corresponding to ``dataframe``

        """
        from fcapy.context.converters import from_pandas
        return from_pandas(dataframe)

    def __repr__(self):
        data_to_print = f'FormalContext ' +\
                        f'({self.n_objects} objects, {self.n_attributes} attributes, ' +\
                        f'{self.data.sum()} connections)\n'
        data_to_print += self.print_data(max_n_objects=20, max_n_attributes=10)
        return data_to_print

    def print_data(self, max_n_objects=20, max_n_attributes=10):
        """Get the FormalContext date in the string formatted as the table

        Parameters
        ----------
        max_n_objects : `int`
            Maximal number of objects to print. If it is less then ``n_objects`` then print ``max_n_objects/2``
            objects from the "top" and the "bottom" of the context
        max_n_attributes : `int`
            Maximal number of attributes to print. If it is less then ``n_attributes`` then print ``max_n_attributes/2``
            attributes from the "left" and the "right" part of the context

        Returns
        -------
        data_to_print : `str`
            A string with the context data formatted as the table

        """
        objs_to_print = list(self.object_names)
        attrs_to_print = list(self.attribute_names)
        data_to_print = self.data.to_list()
        plot_objs_line = False

        if self.n_attributes > max_n_attributes:
            attrs_to_print = attrs_to_print[:max_n_attributes//2]\
                             + ['...'] + attrs_to_print[-max_n_attributes//2:]
            data_to_print = [line[:max_n_attributes//2]+['...']+line[-max_n_attributes//2:] for line in data_to_print]

        if self.n_objects > max_n_objects:
            objs_to_print = objs_to_print[:max_n_objects//2] + objs_to_print[-max_n_objects//2:]
            data_to_print = data_to_print[:max_n_objects//2] + data_to_print[-max_n_objects//2:]
            plot_objs_line = True

        max_obj_name_len = max([len(g) for g in objs_to_print])

        header = ' ' * max_obj_name_len + '|'
        header += '|'.join([m for m in attrs_to_print])
        header += '|'

        lines = []
        for idx in range(len(data_to_print)):
            g_name = objs_to_print[idx]
            g_ms = data_to_print[idx]

            if plot_objs_line and idx == max_n_objects//2:
                line = '.' * (max_obj_name_len + 1 + sum([len(m) + 1 for m in attrs_to_print]))
                lines += [line] * 2

            line = g_name + ' ' * (max_obj_name_len - len(g_name)) + '|'
            line += '|'.join([(' ' * (len(m_name) - 1) + ('X' if m_val else ' ')) if m_val != '...' else '...'
                              for m_name, m_val in zip(attrs_to_print, g_ms)])
            line += '|'
            lines.append(line)

        data_to_print = '\n'.join([header] + lines)
        return data_to_print

    def get_minimal_generators(
            self,
            intent: Union[List[str], List[int]],
            base_generator: Union[List[str], List[int]] = None,
            base_objects: Union[List[str], List[int]] = None,
            use_indexes: bool = False
    ) -> List[Tuple]:
        r"""Get a set of minimal generators for closed intent ``intent``

        WARNING: The current algorithm looks for mimimUM generators instead of mimimAL

        Parameters
        ----------
        intent :
            A set of attribute names (or indexes if ``use_indexes`` set to True) to construct generators for.
        base_generator :
            A set of attribute names (or indexes if ``use_indexes`` set to True)
            which should be included in each constructed generator
        base_objects :
            A set of object names (or indexes if ``use_indexes`` set to True) used to check the generators
        use_indexes :
            A flag whether to use object and attribute names (if set to False) or indexes (otherwise)
        Returns
        -------
        min_gens : `list` of `tuple`
            A set of miminUM generators of the closed intent

        Notes
        -----
        A generator D \\subseteq M of a closed description (intent) B \\subseteq M
        is a subset of attributes with the same closed description as B: D'' = B

        A mimimAL generator D \\subseteq M of a closed description (intent) B \\subseteq M
        is a generator of B s.t. there is no generator E \\subseteq M of B smaller than D:
        D'' = B, \\nexists E \\subset D, E''=B

        A mimimUM generator D \\subseteq M of a closed description (intent) B \\subseteq M
        is a generator of B s.t. there is no generator E \\subseteq M of B with the smaller size:
        D'' = B, \\nexists E \\subset B, | E | < | D |

        """
        if use_indexes:
            return self.get_minimal_generators_i(intent, base_generator, base_objects)

        intent_i = [m_i for m_i, m in enumerate(self.attribute_names) if m in intent]

        base_generator = list(base_generator) if base_generator is not None else []
        base_generator = [m_i for m_i, m in enumerate(self.attribute_names) if m in base_generator]

        if base_objects is None:
            base_objects_i = list(range(self.n_objects))
        else:
            base_objects_i = [g_i for g_i, g in enumerate(self._object_names) if g in base_objects]

        min_gens = self.get_minimal_generators_i(intent_i, base_generator, base_objects_i)

        min_gens = [tuple([self.attribute_names[m_i] for m_i in mg]) for mg in min_gens]
        return min_gens

    def get_minimal_generators_i(
            self,
            intent_i: List[int],
            base_generator: List[int] = None,
            base_objects_i: List[int] = None
    ) -> List[Tuple[int, ...]]:
        intent_i = set(intent_i)
        base_generator = list(base_generator) if base_generator is not None else []
        base_objects_i = list(base_objects_i)

        attrs_to_iterate = [m_i for m_i in range(self.n_attributes) if m_i not in base_generator]
        min_gens = set()
        for n_projection in range(0, len(attrs_to_iterate) + 1):
            for comb in combinations(attrs_to_iterate, n_projection):
                comb = base_generator + list(comb)
                ext_i = self.extension_i(comb, base_objects_i=base_objects_i)
                int_i = self.intention_i(ext_i)
                if set(int_i) == intent_i:
                    min_gens.add(tuple(sorted(comb)))

            if len(min_gens) > 0:
                break

        return list(min_gens)

    def __eq__(self, other):
        """Wrapper for the comparison method __eq__"""
        if not self.object_names == other.object_names:
            raise ValueError('Two FormalContext objects can not be compared since they have different object_names')

        if not self.attribute_names == other.attribute_names:
            raise ValueError('Two FormalContext objects can not be compared since they have different attribute_names')

        is_equal = self.data == other.data and self._target == other.target
        return is_equal

    def __ne__(self, other):
        """Wrapper for the comparison method __ne__"""
        if not self.object_names == other.object_names:
            raise ValueError('Two FormalContext objects can not be compared since they have different object_names')

        if not self.attribute_names == other.attribute_names:
            raise ValueError('Two FormalContext objects can not be compared since they have different attribute_names')

        is_not_equal = self.data != other.data or self._target != other.target
        return is_not_equal

    def __hash__(self):
        return hash((tuple(self._object_names), tuple(self._attribute_names), hash(self._data)))

    def __len__(self):
        return len(self.object_names)

    def hash_fixed(self):
        """Hash value of FormalContext which do not differ between sessions"""
        str_ = str(self._object_names)
        str_ += str(self._attribute_names)
        str_ += str(self._data.to_list())

        code = zlib.adler32(str_.encode())
        return code

    def __getitem__(self, item):
        if type(item) != tuple:
            row_slice = item
            column_slice = slice(0, self.n_attributes)
        else:
            row_slice, column_slice = item

        data = self.data[row_slice, column_slice]

        if not (isinstance(row_slice, Integral) and isinstance(column_slice, Integral)):
            object_names = slice_list(self._object_names, row_slice)
            attribute_names = slice_list(self._attribute_names, column_slice)
            target = slice_list(self._target, row_slice) if self._target is not None else None
            data = self.__class__(data, object_names, attribute_names, target=target, backend=self.backend)

        return data

    def __invert__(self):
        data_inv = ~self.data
        attrs_inv = [m[4:] if m.startswith('not ') else 'not ' + m for m in self.attribute_names]
        return self.__class__(data_inv, self.object_names, attrs_inv, target=self.target, backend=self.backend)

    def to_numeric(self):
        """A method to extract the data of the context in a numerical form (and the names of numerical attributes)

        The method is less straightforward for MVContext class

        Returns
        -------
        data : `list` of `list` of `bool`
            Binary data of connections between objects and attributes
        attribute_names : `list` of `str`
            Name of attributes from the context

        """
        return self._data.to_list(), self._attribute_names
