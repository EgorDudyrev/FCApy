class POSet:
    def __init__(self, elements=None):
        raise NotImplementedError

    def join_elements(self, element_indexes=None):
        raise NotImplementedError

    def meet_elements(self, element_indexes=None):
        raise NotImplementedError

    def __getitem__(self, item):
        raise NotImplementedError

    def __and__(self, other):
        raise NotImplementedError

    def __or__(self, other):
        raise NotImplementedError

    def __xor__(self, other):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError

    def __add__(self, other):
        raise NotImplementedError

    def __delitem__(self, key):
        raise
