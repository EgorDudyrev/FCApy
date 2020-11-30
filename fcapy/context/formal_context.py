class FormalContext:
    def __init__(self, **kwargs):
        self.data = kwargs.get('data')
        self.object_names = kwargs.get('object_names')
        self.attribute_names = kwargs.get('attribute_names')
        self.description = kwargs.get('description')

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

    def extension_i(self, attributes):
        return [g_idx for g_idx, g_ms in enumerate(self._data) if all([g_ms[m] for m in attributes])]

    def intention_i(self, objects):
        return [m_idx for m_idx in range(len(self._data[0])) if all([self._data[g_idx][m_idx] for g_idx in objects])]

    def intention(self, objects):
        obj_idx_dict = {g: g_idx for g_idx, g in enumerate(self._object_names)}
        obj_indices = []
        for g in objects:
            try:
                obj_indices.append(obj_idx_dict[g])
            except KeyError as e:
                raise KeyError(f'FormalContext.intention: Context does not have an object "{g}"')

        intention_i = self.intention_i(obj_indices)
        intention = [self._attribute_names[m_idx] for m_idx in intention_i]
        return intention

    def extension(self, attributes):
        attr_idx_dict = {m: m_idx for m_idx, m in enumerate(self._attribute_names)}
        attr_indices = []
        for m in attributes:
            try:
                attr_indices.append(attr_idx_dict[m])
            except KeyError as e:
                raise KeyError(f'FormalContext.extension: Context does not have an attribute "{m}"')

        extension_i = self.extension_i(attr_indices)
        extension = [self._object_names[g_idx] for g_idx in extension_i]
        return extension

    @property
    def n_objects(self):
        return self._n_objects

    @property
    def n_attributes(self):
        return self._n_attributes

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        assert isinstance(value, (type(None), str)), 'FormalContext.description: Description should be of type `str`'

        self._description = value

    def to_cxt(self, path=None):
        from fcapy.context.converters import write_cxt
        return write_cxt(self, path)

    def to_json(self, path=None):
        from fcapy.context.converters import write_json
        return write_json(self, path)

    def to_csv(self, path=None, **kwargs):
        from fcapy.context.converters import write_csv
        return write_csv(self, path=path, **kwargs)

    def __repr__(self):
        data_to_print = f'FormalContext '+\
                        f'({self.n_objects} objects, {self.n_attributes} attributes, '+\
                        f'{sum([sum(l) for l in self.data])} connections)\n'
        data_to_print += self.print_data()
        return data_to_print

    def print_data(self):
        if not (self.n_attributes < 10 and self.n_objects < 20):
            raise NotImplementedError

        max_obj_name_len = max([len(g) for g in self.object_names])

        header = ' ' * max_obj_name_len + '|'
        header += '|'.join([m for m in self.attribute_names])
        header += '|'

        lines = []
        for g_name, g_ms in zip(self.object_names, self.data):
            line = g_name + ' ' * (max_obj_name_len - len(g_name)) + '|'
            line += '|'.join([' ' * (len(m_name) - 1) + ('X' if m_val else ' ') for m_name, m_val in
                              zip(self.attribute_names, g_ms)])
            line += '|'
            lines.append(line)

        data_to_print = '\n'.join([header] + lines)
        return data_to_print
