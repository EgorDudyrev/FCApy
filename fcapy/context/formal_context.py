class FormalContext:
    def __init__(self, **kwargs):
        self.data = kwargs.get('data')

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        if value is None:
            self._data = None
            return

        assert isinstance(value, list), 'FormalContext.data.setter: "value" should have type "list"'
        assert len(value) > 0, 'FormalContext.data.setter: "value" should have length > 0 (use [[]] for the empty data)'

        length = len(value[0])
        for g_ms in value:
            assert len(g_ms) == length, 'FormalContext.data.setter: All sublists of the "value" should have the same length'
            for m in g_ms:
                assert m in {0, 1}, 'FormalContext.data.setter: "Value" should consist only of numbers 0 and 1'

        self._data = value

    def extension_i(self, attributes):
        return [g_idx for g_idx, g_ms in enumerate(self._data) if all([g_ms[m] for m in attributes])]

    def intention_i(self, objects):
        return [m_idx for m_idx in range(len(self._data[0])) if all([self._data[g_idx][m_idx] for g_idx in objects])]
