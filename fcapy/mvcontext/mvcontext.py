from collections.abc import Iterable
from frozendict import frozendict
from itertools import combinations

from .. import LIB_INSTALLED
if LIB_INSTALLED['numpy']:
    import numpy as np


class MVContext:
    """
    A class used to represent Multi Valued Context object from FCA theory.

    """
    def __init__(self, data=None, pattern_types=None, object_names=None, attribute_names=None, **kwargs):
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
        data = [ps.data for ps in self._pattern_structures]
        data = [list(row) for row in zip(*data)]
        return data

    @property
    def object_names(self):
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
        return self._pattern_structures

    @pattern_structures.setter
    def pattern_structures(self, value):
        self._pattern_structures = value

    @property
    def pattern_types(self):
        return self._pattern_types

    @property
    def target(self):
        return self._target

    def assemble_pattern_structures(self, data, pattern_types):
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
        description_i = {ps_i: ps.intention_i(object_indexes) for ps_i, ps in enumerate(self._pattern_structures)}
        return description_i

    def extension(self, descriptions, base_objects=None):
        ps_names_map = {ps.name: ps_i for ps_i, ps in enumerate(self._pattern_structures)}
        descriptions_i = {ps_names_map[ps_name]: description for ps_name, description in descriptions.items()}
        base_objects_i = {g_i for g_i, g in enumerate(self._object_names) if g in base_objects}\
            if base_objects is not None else None
        extension_i = self.extension_i(descriptions_i, base_objects_i=base_objects_i)
        objects = [self._object_names[g_i] for g_i in extension_i]
        return objects

    def intention(self, objects):
        objects = set(objects)
        object_indexes = [g_i for g_i, g in enumerate(self._object_names) if g in objects]
        descriptions_i = self.intention_i(object_indexes)
        description = {self._pattern_structures[ps_i].name: description for ps_i, description in descriptions_i.items()}
        return description

    @property
    def n_objects(self):
        """Get the number of objects in the context (i.e. len(`data`))"""
        return self._n_objects

    @property
    def n_attributes(self):
        """Get the number of attributes in the context (i.e. len(`data[0]`)"""
        return self._n_attributes

    @property
    def description(self):
        """Get or set the human readable description of the context

        JSON is the only file format to store this information.
        The description will be lost when saving context to .cxt or .csv

        Parameters
        ----------
        value : `str, None
            The human readable description of the context

        Raises
        ------
        AssertionError
            If the given ``value`` is not None and not of type `str

        """
        return self._description

    @description.setter
    def description(self, value):
        assert isinstance(value, (type(None), str)), 'FormalContext.description: Description should be of type `str`'

        self._description = value

    def to_json(self, path=None):
        """Convert the FormalContext into json file format (save if ``path`` is given)

        Parameters
        ----------
        path : `str or None
            Path to save a context

        Returns
        -------
        context : `str
            If ``path`` is None, the string with .json file data is returned. If ``path`` is given - return None

        """
        raise NotImplementedError

    def to_csv(self, path=None, **kwargs):
        """Convert the FormalContext into csv file format (save if ``path`` is given)

        Parameters
        ----------
        path : `str or None
            Path to save a context
        **kwargs :
            ``sep`` : `str
                Field delimiter for the output file

        Returns
        -------
        context : `str
            If ``path`` is None, the string with .csv file data is returned. If ``path`` is given - return None

        """
        raise NotImplementedError

    def to_pandas(self):
        """Convert the FormalContext into pandas.DataFrame object

        Returns
        -------
        df : pandas.DataFrame
            The dataframe with boolean variables,
            ``object_names`` turned into ``df.index``, ``attribute_names`` turned into ``df.columns``

        """
        raise NotImplementedError

    @staticmethod
    def from_pandas(dataframe):
        raise NotImplementedError

    def get_minimal_generators(self, intent, base_generator=None, base_objects=None, use_indexes=False,
                               ps_to_iterate=None, projection_to_start=1):
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
        data_to_print = f'MultiValuedContext ' +\
                        f'({self.n_objects} objects, {self.n_attributes} attributes)'
        return data_to_print

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
            pattern_types = {k: v for k, v in self._pattern_types.items() if k in attribute_names}
            data = MVContext(data, pattern_types, object_names, attribute_names, target=target)
        else:
            data = data[0][0]
        return data
