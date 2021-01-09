class MVContext:
    """
    A class used to represent Multi Valued Context object from FCA theory.

    """

    def __init__(self, data=None, object_names=None, attribute_names=None, pattern_types=None, **kwargs):
        self.data = data
        self.object_names = object_names
        self.attribute_names = attribute_names
        self.description = kwargs.get('description')
        self.pattern_types = pattern_types

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        if value is None:
            self._data = None
            self._n_objects = None
            self._n_attributes = None
            return

        assert isinstance(value, list), 'FormalContext.data.setter: "value" should have type "list"'
        assert len(value) > 0, 'FormalContext.data.setter: "value" should have length > 0 (use [[]] for the empty data)'

        length = len(value[0])
        for g_ms in value:
            assert len(g_ms) == length,\
                'FormalContext.data.setter: All sublists of the "value" should have the same length'
            for m in g_ms:
                assert type(m) == bool, 'FormalContext.data.setter: "Value" should consist only of boolean number'

        self._data = value
        self._n_objects = len(value)
        self._n_attributes = length

    @property
    def object_names(self):
        return self._object_names

    @object_names.setter
    def object_names(self, value):
        if value is None:
            self._object_names = [str(idx) for idx in range(self.n_objects)] if self.data is not None else None
            return

        assert len(value) == len(self._data),\
            'FormalContext.object_names.setter: Length of "value" should match length of data'
        assert all(type(name) == str for name in value),\
            'FormalContext.object_names.setter: Object names should be of type str'
        self._object_names = value

    @property
    def attribute_names(self):
        return self._attribute_names

    @attribute_names.setter
    def attribute_names(self, value):
        if value is None:
            self._attribute_names = [str(idx) for idx in range(self.n_attributes)] if self.data is not None else None
            return

        assert len(value) == len(self._data[0]),\
            'FormalContext.attribute_names.setter: Length of "value" should match length of data[0]'
        assert all(type(name) == str for name in value),\
            'FormalContext.object_names.setter: Object names should be of type str'
        self._attribute_names = value

    @property
    def pattern_types(self):
        return self._pattern_types

    @pattern_types.setter
    def pattern_types(self, value: dict):
        self._pattern_types = value

    def extension_i(self, attribute_indexes):
        raise NotImplementedError

    def intention_i(self, object_indexes):
        raise NotImplementedError

    def intention(self, objects):
        raise NotImplementedError

    def extension(self, attributes):
        raise NotImplementedError

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

    def __repr__(self):
        data_to_print = f'MultiValuedContext ' +\
                        f'({self.n_objects} objects, {self.n_attributes} attributes, '
        return data_to_print

    def __eq__(self, other):
        """Wrapper for the comparison method __eq__"""
        if not self.object_names == other.object_names:
            raise ValueError('Two FormalContext objects can not be compared since they have different object_names')

        if not self.attribute_names == other.attribute_names:
            raise ValueError('Two FormalContext objects can not be compared since they have different attribute_names')

        is_equal = self.data == other.data
        return is_equal

    def __ne__(self, other):
        """Wrapper for the comparison method __ne__"""
        if not self.object_names == other.object_names:
            raise ValueError('Two FormalContext objects can not be compared since they have different object_names')

        if not self.attribute_names == other.attribute_names:
            raise ValueError('Two FormalContext objects can not be compared since they have different attribute_names')

        is_not_equal = self.data != other.data
        return is_not_equal

    def __hash__(self):
        raise NotImplementedError
