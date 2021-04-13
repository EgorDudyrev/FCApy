"""
This module provides a POSet class. It may be considered as the main module (and class) of poset subpackage

POSet (Partialy Ordered Set) is a set in which some elements are bigger then other,
some are smaller and some are incomparable
"""


class POSet:
    def __init__(self, elements=None, leq_func=None):
        raise NotImplementedError

    @property
    def elements(self):
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

    def __delitem__(self, key):
        raise NotImplementedError

    def add(self, other):
        raise NotImplementedError

    def remove(self, other):
        raise NotImplementedError

    def __eq__(self, other):
        raise NotImplementedError