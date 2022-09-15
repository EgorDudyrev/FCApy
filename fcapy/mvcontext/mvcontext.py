"""
This module implements the class MVContext which is used to represent a Many Valued Context from FCA theory

"""
from collections.abc import Iterable
from frozendict import frozendict
from itertools import combinations
import zlib
from typing import Tuple
import json

from fcapy import LIB_INSTALLED
from fcapy.mvcontext import pattern_structure as PS


if LIB_INSTALLED['numpy']:
    import numpy as np


class MVContext:
    """
    A class used to represent Many Valued Context object from FCA theory.

    """
    def __init__(self, data=None, pattern_types=None, object_names=None, attribute_names=None, **kwargs):
        """Initialize the MVContext

        Parameters
        ----------
        data: `list` of `list` of `PatternStructure intents`
            The data for MVContext to work with
        pattern_types: `dict` of type {`name of an attribute`: `Pattern Structure type`}
            The types of PatternStructure to describe each "column" of the data
        object_names: `list` of `str`
            The names of objects (default values are ['0','1','2',...]
        attribute_names: `list` of `str`
            The names of attributes, i.e. pattern structures (default values are ['0', '1', '2', ...])
        kwargs:
            description: `str`
                A human readable description of the context
            target: `list` of `float`
                A target values to use in Supervised ML scenario

        """
        self._n_objects = len(data) if data is not None else None
        self._n_attributes = len(data[0]) if data is not None else None

        self.object_names = object_names
        self.attribute_names = attribute_names
        self._pattern_types = pattern_types
        self.pattern_structures = self.assemble_pattern_structures(data, pattern_types)
        self.description = kwargs.get('description')
        self._target = kwargs.get('target')

    @property
    def data(self):
        """The data for MVContext to work with. List of datas of Pattern Structures of the context"""
        data = [ps.data for ps in self._pattern_structures]
        data = [list(row) for row in zip(*data)]
        return data

    @property
    def object_names(self):
        """The names of objects in the context"""
        return self._object_names

    @object_names.setter
    def object_names(self, value):
        if value is None:
            self._object_names = [str(idx) for idx in range(self._n_objects)] if self._n_objects is not None else None
            return

        assert len(value) == self._n_objects,\
            'MVContext.object_names.setter: Length of new object names should match length of data'
        assert all(type(name) == str for name in value),\
            'MVContext.object_names.setter: Object names should be of type str'
        self._object_names = value

    @property
    def attribute_names(self):
        """The names of attributes (i.e. pattern structures) in the context"""
        return self._attribute_names

    @attribute_names.setter
    def attribute_names(self, value):
        if value is None:
            self._attribute_names = [str(idx) for idx in range(self._n_attributes)]\
                if self._n_attributes is not None else None
            return

        assert len(value) == self._n_attributes,\
            'MVContext.attribute_names.setter: Length of "value" should match length of data[0]'
        assert all(type(name) == str for name in value),\
            'MVContext.object_names.setter: Object names should be of type str'
        self._attribute_names = value

    @property
    def pattern_structures(self):
        """A list of pattern structures kept in a context"""
        return self._pattern_structures

    @pattern_structures.setter
    def pattern_structures(self, value):
        self._pattern_structures = value

    @property
    def pattern_types(self):
        """A dictionary to map the names of attributes (pattern structures) and their types"""
        return self._pattern_types

    @property
    def target(self):
        """A list of target values for Supervised ML scenarios"""
        return self._target

    def assemble_pattern_structures(self, data, pattern_types):
        """Return pattern_structures based on ``data`` and the ``pattern_types``"""
        if data is None:
            return None

        if pattern_types is not None:
            defined_patterns = set([attr_name for attr_names in pattern_types.keys()
                                    for attr_name in (attr_names if type(attr_names) != str else [attr_names])])
        else:
            defined_patterns = set()
        missed_patterns = set(self._attribute_names) - defined_patterns
        assert len(missed_patterns) == 0,\
            f'MVContext.assemble_pattern_structures error. Patterns are undefined for attributes {missed_patterns}'

        names_to_indexes_map = {m: m_i for m_i, m in enumerate(self._attribute_names)}
        pattern_structures = []
        for name, ps_type in pattern_types.items():
            m_i = names_to_indexes_map[name]
            ps_data = [row[m_i] for row in data]
            ps = ps_type(ps_data, name=name)
            pattern_structures.append(ps)
        return pattern_structures

    def extension_i(self, descriptions_i, base_objects_i=None):
        """Return a subset of objects of ``base_objects_i`` which falls into ``descriptions_i``

        Parameters
        ----------
        descriptions_i: `dict` of type {pattern_structure_index: description}
            Descriptions to filter objects
        base_objects_i: `list` of `int`
            Indexes of objects to select extension from (default value is the set of all object indexes)

        Returns
        -------
        extent_i: `list` of `int`
            A list of indexes of objects described by ``descriptions_i``

        """
        if base_objects_i is not None and len(base_objects_i) == 0:
            return []

        if not LIB_INSTALLED['numpy']:
            extent_i = range(self._n_objects) if base_objects_i is None else base_objects_i
        else:
            if base_objects_i is None:
                extent_i = np.arange(self._n_objects)
            elif not isinstance(base_objects_i, np.ndarray):
                if isinstance(base_objects_i, (tuple, list)):
                    extent_i = np.array(base_objects_i)
                else:
                    extent_i = np.array(list(base_objects_i))
            else:
                extent_i = base_objects_i

        for ps_i, description in descriptions_i.items():
            ps = self._pattern_structures[ps_i]
            extent_i = ps.extension_i(description, base_objects_i=extent_i)
            if len(extent_i) == 0:
                break

        if LIB_INSTALLED['numpy']:
            if type(extent_i) is np.ndarray:
                extent_i = extent_i.tolist()
        return extent_i

    def intention_i(self, object_indexes):
        """Return a common description of objects from ``object_indexes``. Pat. structures are denoted by their indexes"""
        description_i = {ps_i: ps.intention_i(object_indexes) for ps_i, ps in enumerate(self._pattern_structures)}
        return description_i

    def extension(self, descriptions, base_objects=None):
        """Return a subset of objects of ``base_objects_i`` which falls into ``descriptions``

        Parameters
        ----------
        descriptions: `dict` of type {pattern_structure_name: description}
            Descriptions to filter objects
        base_objects: `list` of `str`
            Names of objects to select extension from (default value is the set of all object names)

        Returns
        -------
        extent_i: `list` of `str`
            A list of names of objects described by ``descriptions_i``

        """
        ps_names_map = {ps.name: ps_i for ps_i, ps in enumerate(self._pattern_structures)}
        descriptions_i = {ps_names_map[ps_name]: description for ps_name, description in descriptions.items()}
        base_objects_i = {g_i for g_i, g in enumerate(self._object_names) if g in base_objects}\
            if base_objects is not None else None
        extension_i = self.extension_i(descriptions_i, base_objects_i=base_objects_i)
        objects = [self._object_names[g_i] for g_i in extension_i]
        return objects

    def intention(self, objects):
        """Return a common description of objects from ``objects``. Pat. structures are denoted by their names"""
        objects = set(objects)
        object_indexes = [g_i for g_i, g in enumerate(self._object_names) if g in objects]
        descriptions_i = self.intention_i(object_indexes)
        description = {self._pattern_structures[ps_i].name: description for ps_i, description in descriptions_i.items()}
        return description

    @property
    def n_objects(self):
        """Get the number of objects in the context (i.e. len(``MVContext.data``))"""
        return self._n_objects

    @property
    def n_attributes(self):
        """Get the number of pattern structures (attributes) in the context (i.e. len(``MVContext.pattern_structures``))"""
        return self._n_attributes

    @property
    def description(self):
        """Get or set the human readable description of the context

        JSON is the only file format to store this information.
        The description will be lost when saving context to .cxt or .csv

        Parameters
        ----------
        value : `str`, None
            The human readable description of the context

        Raises
        ------
        AssertionError
            If the given ``value`` is not None and not of type `str`

        """
        return self._description

    @description.setter
    def description(self, value):
        assert isinstance(value, (type(None), str)), 'FormalContext.description: Description should be of type `str`'

        self._description = value

    def write_json(self, path=None):
        """Convert the FormalContext into json file format (save if ``path`` is given)

        WARNING: Does not implemented yet

        Parameters
        ----------
        path : `str` or None
            Path to save a context

        Returns
        -------
        context : `str`
            If ``path`` is None, the string with .json file data is returned. If ``path`` is given - return None

        """
        metadata, object_info = {}, {}
        if self.description is not None:
            metadata['Description'] = self.description
        metadata['ObjNames'] = self.object_names
        metadata['Params'] = {}
        metadata['Params']['AttrNames'] = self.attribute_names
        metadata['Params']['PTypes'] = [type(ps).__name__ for ps in self.pattern_structures]

        object_info['Count'] = self.n_objects

        object_info['Data'] = [
            {'PValues': [ps.to_json(row[ps_i]) for ps_i, ps in enumerate(self.pattern_structures)]}
            for row in self.data
        ]
        file_data = json.dumps([metadata, object_info], separators=(',', ':'))

        if path is None:
            return file_data

        with open(path, 'w') as f:
            f.write(file_data)

    @staticmethod
    def read_json(path: str = None, json_data: str = None, pattern_types: Tuple[PS.AbstractPS] = None):
        """Read MVContext from .json file .json formatted string data

        Parameters
        ----------
        path: `str`
            A path to .json file
        json_data: `str`
            A json encoded data
        pattern_types: `tuple[AbstractPS]`
            Tuple of additional Pattern Structures not defined in fcapy.mvcontext.pattern_structure

        Returns
        -------
        mvK: `MVContext`

        """
        assert path is not None or json_data is not None,\
            'MVContext.read_json error. Either path or data should be given'

        if json_data is None:
            with open(path, 'r') as f:
                json_data = f.read()
        file_data = json.loads(json_data)

        metadata, objects_info = file_data

        description = metadata.get('Description')
        object_names = metadata.get('ObjNames')
        if 'Params' in metadata:
            attribute_names = metadata['Params'].get('AttrNames')
            ptype_names = metadata['Params']['PTypes']
        else:
            attribute_names, ptype_names = None, None

        pattern_types = {k: getattr(PS, v) if v in dir(PS) else pattern_types[v]
                         for k, v in zip(attribute_names, ptype_names)}

        patterns_list = [pattern_types[m] for m in attribute_names]

        data = [[p.from_json(v) for p, v in zip(patterns_list, g_data['PValues'])] for g_data in objects_info['Data']]

        mvK = MVContext(
            data, pattern_types,
            object_names=object_names, attribute_names=attribute_names, description=description
        )
        return mvK

    def read_csv(self, path=None, **kwargs):
        """Convert the MVContext into csv file format (save if ``path`` is given)

        WARNING: Does not implemented yet

        Parameters
        ----------
        path : `str` or None
            Path to save a context
        **kwargs :
            ``sep`` : `str`
                Field delimiter for the output file

        Returns
        -------
        context : `str`
            If ``path`` is None, the string with .csv file data is returned. If ``path`` is given - return None

        """
        raise NotImplementedError

    def to_pandas(self):
        """Convert the FormalContext into pandas.DataFrame object

        WARNING: Does not implemented yet

        Returns
        -------
        df : `pandas.DataFrame`
            The dataframe with boolean variables,
            ``object_names`` turned into ``df.index``, ``attribute_names`` turned into ``df.columns``

        """
        raise NotImplementedError

    @staticmethod
    def from_pandas(dataframe):
        """Create MVContext from Pandas ``dataframe``

        WARNING: Does not implemented yet

        """
        raise NotImplementedError

    def get_minimal_generators(self, intent, base_generator=None, base_objects=None, use_indexes=False,
                               ps_to_iterate=None, projection_to_start=1):
        """Get a set of minimal generators for closed intent ``intent``

        WARNING: The current algorithm looks for mimimUM generators instead of mimimAL

        Parameters
        ----------
        intent: `dict` with PatternStructure intents
            A dict of PatternStructure description to construct generators for.
        base_generator: `dict` with PatternStructure intents
            A dict of PatternStructure descriptions
            which should be included in each constructed generator
        base_objects: `list` of `string` or `int`
            A set of object names (or indexes if ``use_indexes`` set to True) used to check the generators
        use_indexes: `bool`
            A flag whether to use object and attribute names (if set to False) or indexes (otherwise)
        ps_to_iterate: `list` of `string` or `int`
            A list of pattern structures names (or indexes if ``use_indexes`` set to True) to construct generators on
        projection_to_start: `int`
            A number of PatternStructures projection to construct generators on

        Returns
        -------
        min_gens: `list` of `dict` of type {pattern_structure_index/name: description}
            A list of mimimUM generators of a closed ``intent``
        Notes
        -----
        An idea of generators for FormalContext is described in the function
        fcapy.context.formal_context.get_minimal_generators()

        """
        intent_i = {
            ps_i: intent[ps.name] for ps_i, ps in enumerate(self._pattern_structures)
            if ps.name in intent
        } if not use_indexes else intent.copy()

        if base_generator is not None:
            if not use_indexes:
                base_generator = {
                    ps_i: base_generator[ps.name] for ps_i, ps in enumerate(self._pattern_structures)
                    if ps.name in base_generator}
            base_generator = [(ps_i, descr) for ps_i, descr in base_generator.items()]
        else:
            base_generator = []

        if base_objects is None:
            base_objects_i = None
        elif not use_indexes:
            base_objects_i = [g_i for g_i, g in enumerate(self._object_names) if g in base_objects]
        else:
            base_objects_i = base_objects.copy()

        if not LIB_INSTALLED['numpy']:
            if base_objects_i is None:
                base_objects_i = list(range(self._n_objects))
            base_objects_i = frozenset(base_objects_i)
        else:
            if base_objects_i is None:
                base_objects_i = np.arange(self._n_objects)
            if not isinstance(base_objects_i, np.ndarray):
                if isinstance(base_objects_i, (list, tuple)):
                    base_objects_i = np.array(base_objects_i)
                else:
                    base_objects_i = np.array(list(base_objects_i))

        if ps_to_iterate is None:
            ps_to_iterate = range(len(self._pattern_structures))
        elif not use_indexes:
            ps_name_i_map = {ps.name: ps_i for ps_i, ps in enumerate(self._pattern_structures)}
            ps_to_iterate = [ps_name_i_map[ps_name] for ps_name in ps_to_iterate]
        else:
            ps_to_iterate = ps_to_iterate.copy()

        def get_generators(ps_i, descr, max_projection_num):
            return [gen for proj_num in range(projection_to_start, max_projection_num + 1)
                    for gen in self._pattern_structures[ps_i].description_to_generators(descr, proj_num)]

        ext_true = self.extension_i(intent_i)
        max_projection_num = projection_to_start
        min_gens = set()
        while len(min_gens) == 0:
            generators_to_iterate = [(ps_i, gen) for ps_i in ps_to_iterate
                                     for gen in get_generators(ps_i, intent_i[ps_i], max_projection_num)]
            generator_volumes = {}

            for comb_size in range(1, len(generators_to_iterate)):
                for comb in combinations(generators_to_iterate, comb_size):
                    comb = base_generator + list(comb)
                    pss_i = set([gen[0] for gen in comb])
                    gens = {ps_i: [gen[1] for gen in comb if gen[0] == ps_i] for ps_i in pss_i}
                    descr = {ps_i: self._pattern_structures[ps_i].generators_to_description(gen)
                             for ps_i, gen in gens.items()}
                    ext_ = self.extension_i(descr, base_objects_i=base_objects_i)
                    if comb_size == 1:
                        generator_volumes[comb[-1]] = len(ext_)

                    if ext_ == ext_true:
                        min_gens.add(frozendict(descr))

                if comb_size == 1:
                    base_objects_i_size = len(base_objects_i)
                    generators_to_iterate = [gen for gen in generators_to_iterate
                                             if generator_volumes[gen] < base_objects_i_size]
                    generators_to_iterate = sorted(generators_to_iterate, key=lambda gen: generator_volumes[gen])

                if len(min_gens) > 0:
                    break
            max_projection_num += 1

        if not use_indexes:
            min_gens = {frozendict({self._pattern_structures[ps_i].name: descr for ps_i, descr in mg.items()})
                        for mg in min_gens}
        min_gens = list(min_gens)
        return min_gens

    def __repr__(self):
        data_to_print = f'ManyValuedContext ' +\
                        f'({self.n_objects} objects, {self.n_attributes} attributes)'
        return data_to_print

    def __len__(self):
        return len(self.object_names)

    def __eq__(self, other):
        """Wrapper for the comparison method __eq__"""
        if not self.object_names == other.object_names:
            raise ValueError('Two MVContext objects can not be compared since they have different object_names')

        if not self.attribute_names == other.attribute_names:
            raise ValueError('Two MVContext objects can not be compared since they have different attribute_names')

        is_equal = self.pattern_structures == other.pattern_structures and self._target == other.target
        return is_equal

    def __ne__(self, other):
        """Wrapper for the comparison method __ne__"""
        if not self.object_names == other.object_names:
            raise ValueError('Two MVContext objects can not be compared since they have different object_names')

        if not self.attribute_names == other.attribute_names:
            raise ValueError('Two MVContext objects can not be compared since they have different attribute_names')

        is_not_equal = self.pattern_structures != other.pattern_structures or self._target != other.target
        return is_not_equal

    def __hash__(self):
        return hash((tuple(self._object_names), tuple(self._attribute_names), tuple(self._pattern_structures)))

    def hash_fixed(self):
        """Hash value of FormalContext which do not differ between sessions"""
        str_ = str(self._object_names)
        str_ += str(self._attribute_names)
        str_ += str(self.data)

        code = zlib.adler32(str_.encode())
        return code

    def __getitem__(self, item):
        if type(item) != tuple:
            item = (item, slice(0, self._n_attributes))

        def slice_list(lst, slicer):
            if isinstance(slicer, slice):
                lst = lst[slicer]
            elif isinstance(slicer, Iterable):
                lst = [lst[x] for x in slicer]
            else:
                lst = [lst[slicer]]
            return lst

        pattern_structures = slice_list(self._pattern_structures, item[1])
        data = [
            ps[item[0]] if isinstance(item[0], (slice, Iterable)) else
            [ps[item[0]]]
            for ps in pattern_structures]
        data = [list(row) for row in zip(*data)]

        if any([isinstance(i, slice) for i in item]):
            object_names = slice_list(self._object_names, item[0])
            attribute_names = slice_list(self._attribute_names, item[1])
            target = slice_list(self._target, item[0]) if self._target is not None else None
            if LIB_INSTALLED['numpy'] and isinstance(self._target, np.ndarray):
                target = np.array(target)
            pattern_types = {k: v for k, v in self._pattern_types.items() if k in attribute_names}
            data = MVContext(data, pattern_types, object_names, attribute_names, target=target)
        else:
            data = data[0][0]
        return data

    def to_numeric(self):
        """Return MVContext data in the form of numeric columns and their names"""
        pattern_nums = [ps.to_numeric() for ps in self._pattern_structures]
        if LIB_INSTALLED['numpy']:
            num_dat = np.hstack([pn[0] for pn in pattern_nums])
        else:
            num_dat = [[x for ps_i in range(len(self._pattern_structures)) for x in pattern_nums[ps_i][0][g_i]]
                       for g_i in range(self.n_objects)]
        names = [name for pn in pattern_nums for name in pn[1]]
        return num_dat, names

    def generators_by_intent_difference(self, new_intent, old_intent):
        """Return the set of generators to select the ``new_intent`` from ``old_intent``"""
        gens = [frozendict({ps_i: gen_}) for ps_i, ps in enumerate(self._pattern_structures)
                for gen_ in ps.generators_by_intent_difference(new_intent[ps_i], old_intent[ps_i])]
        return gens

    def leq_descriptions(self, a:dict, b:dict)->bool:
        """Check If description `a` is 'smaller' (more general) then description `b`"""
        for ps_i, descr in a.items():
            if ps_i not in b:
                continue
            if not self._pattern_structures[ps_i].leq_descriptions(descr, b[ps_i]):
                return False
        return True
