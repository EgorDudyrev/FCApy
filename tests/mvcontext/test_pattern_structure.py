import pytest
from bitarray import frozenbitarray

from fcapy.mvcontext import pattern_structure
import math
from fcapy import LIB_INSTALLED
import numpy as np
from copy import deepcopy


def test_abstract_ps_repr():
    aps = pattern_structure.AbstractPS([1, 2, 'c', None], 'abstract_structure')
    assert aps.__repr__() == "AbstractPS 'abstract_structure'"


def test_abstract_ps_properties():
    aps = pattern_structure.AbstractPS([1, 2, 'c', None], 'abstract_structure')
    assert aps.name == 'abstract_structure', 'AbstractPS.name failed'
    assert aps.data == [1, 2, 'c', None], 'AbstractPS.data failed'

    with pytest.raises(AssertionError):
        aps.data = [1, 2]
    aps.data = [4, 5, 6, 7]
    assert aps.data == [4, 5, 6, 7], 'AbstractPS.data setter failed.'


def test_abstract_ps_extension_intention():
    aps = pattern_structure.AbstractPS([1, 2, 'c', None])
    with pytest.raises(NotImplementedError):
        aps.extension_i(None)
    with pytest.raises(NotImplementedError):
        aps.intention_i(None)


def test_abstract_ps_descriptions_tofrom_generators():
    aps = pattern_structure.AbstractPS([1, 2, 'c', None])
    with pytest.raises(NotImplementedError):
        aps.generators_to_description(None)
    with pytest.raises(NotImplementedError):
        aps.description_to_generators(None, None)


def test_abstract_ps_eq_hash():
    aps1 = pattern_structure.AbstractPS([1, 2, 'c', None])
    aps2 = pattern_structure.AbstractPS([1, 2, 'c'])
    assert aps1 == deepcopy(aps1)
    assert aps1 != aps2

    assert len({aps1, aps2, deepcopy(aps1)}) == 2


def test_abstract_ps_tofrom_json():
    aps = pattern_structure.AbstractPS
    assert aps.to_json(1) == '1'
    assert aps.from_json('1') == 1


def test_interval_ps_extension_intention():
    for cls in [pattern_structure.IntervalPS, pattern_structure.IntervalNumpyPS]:
        ips = cls([0, 1, 2, 3, 2])
        assert ips.extension_i(None) == [], f"{cls.__name__}.extension_i failed"
        assert ips.extension_i((2, 3)) == [2, 3, 4], f"{cls.__name__}.extension_i failed"
        # No longer applicable
        # assert ips.extension_i((2, 2)) == ips.extension_i(2), f"{cls.__name__}.extension_i failed"

        assert ips.extension_i((2, 3), [0, 1, 2, 3, 4]) == [2, 3, 4],  f"{cls.__name__}.extension_i failed"
        # No longer applicable
        # assert ips.extension_i((2, 3), frozenset([0, 1, 2, 3, 4])) == [2, 3, 4], f"{cls.__name__}.extension_i failed"
        # assert ips.extension_i((2, 3), np.array([0, 1, 2, 3, 4])) == [2, 3, 4], f"{cls.__name__}.extension_i failed"

        ips = cls([0, 1, 2, 3, 2])
        assert ips.intention_i([]) is None, f'{cls.__name__}.intention_i failed'
        assert ips.intention_i([0, 1, 3]) == (0, 3), f"{cls.__name__}.intention_i failed"
        assert ips.intention_i([2, 4]) == (2, 2), f"{cls.__name__}.intention_i failed"
        assert ips.extension_i(ips.intention_i([1, 2, 4])) == [1, 2, 4], f"{cls.__name__}.extension_i/intention_i failed"


def test_interval_ps_descriptions_tofrom_generators():
    for cls in [pattern_structure.IntervalPS, pattern_structure.IntervalNumpyPS]:
        ips = cls([])
        description_true = (1, 2)
        generators_true = [(-math.inf, 2), (1, math.inf)]

        assert ips.description_to_generators(description_true, projection_num=0) == [(-math.inf, math.inf)]

        assert ips.description_to_generators(description_true, projection_num=1) == generators_true,\
            f"{cls.__name__}.description_to_generators failed"
        assert ips.generators_to_description(generators_true) == description_true, \
            f"{cls.__name__}.generators_to_description failed"
        assert ips.description_to_generators(
            ips.generators_to_description(generators_true), projection_num=1) == generators_true,\
            f"{cls.__name__}.generators_to_description pipe failed"

        assert ips.description_to_generators(4, projection_num=1) == [(-math.inf, 4), (4, math.inf)],\
            f"{cls.__name__}.description_to_generators failed"
        assert ips.generators_to_description([(-math.inf, 4), (4, math.inf)]) == 4, \
            f"{cls.__name__}.generators_to_description failed"

        assert ips.description_to_generators(description_true, projection_num=2)[0] == description_true,\
            f"{cls.__name__}.generators_to_description failed"


def test_interval_ps_tofrom_json():
    for cls in [pattern_structure.IntervalPS, pattern_structure.IntervalNumpyPS]:
        ips = cls
        assert ips.to_json((1,1)) == '[1.0, 1.0]'
        assert ips.from_json('[1.0, 1.0]') == (1., 1.)


def test_set_ps_extension_intention():
    sps = pattern_structure.SetPS(['a', 'b', 'c', 'd'])
    assert sps.extension_i(None) == [], "SetPS.extension_i failed"
    assert sps.extension_i({'b', 'c'}) == [1, 2], "SetPS.extension_i failed"

    assert sps.intention_i([]) == set(), 'SetPS.intention_i failed'
    assert sps.intention_i([0, 1, 3]) == {'a', 'b', 'd'}, "SetPS.intention_i failed"
    assert sps.extension_i(sps.intention_i([1, 2, 3])) == [1, 2, 3], "SetPS.extension_i/intention_i failed"


def test_set_ps_tofrom_json():
    ips = pattern_structure.SetPS
    assert ips.to_json({'a', 'b', 'c'}) == '["a", "b", "c"]'
    assert ips.from_json('["a", "b", "c"]') == {'a', 'b', 'c'}


def test_attribute_ps_extension_intention():
    aps = pattern_structure.AttributePS([True, False, True, True])
    assert aps.extension_i(True) == [0, 2, 3], "AttributePS.extension_i failed"
    assert aps.extension_i(False) == [0, 1, 2, 3], "AttributePS.extension_i failed"

    assert aps.intention_i([]) is False, 'AttributePS.intention_i failed'
    assert aps.intention_i([0, 1, 3]) is False, "AttributePS.intention_i failed"
    assert aps.extension_i(aps.intention_i([0, 2, 3])) == [0, 2, 3], "AttributePS.extension_i/intention_i failed"


def test_attribute_ps_tofrom_json():
    ips = pattern_structure.AttributePS
    assert ips.to_json(True) == 'true'
    assert ips.to_json(False) == 'false'
    assert ips.from_json('false') is False


def test_attribute_ps_to_bin_attr_extents():
    aps = pattern_structure.AttributePS([True, False], 'attr')
    bin_extents_true = [('attr', frozenbitarray('10'))]
    assert list(aps.to_bin_attr_extents()) == bin_extents_true


def test_set_ps_to_bin_attr_extents():
    sps = pattern_structure.SetPS([{'a'}, {'b'}, {'c'}], 'set')
    bin_extents_true = [
        ('set: a, b, c', frozenbitarray('111')),
        ('set: a, b', frozenbitarray('110')),
        ('set: a, c', frozenbitarray('101')),
        ('set: b, c', frozenbitarray('011')),
        ('set: a', frozenbitarray('100')),
        ('set: b', frozenbitarray('010')),
        ('set: c', frozenbitarray('001')),
        ('set: ∅', frozenbitarray('000'))
    ]
    assert list(sps.to_bin_attr_extents()) == bin_extents_true


def test_interval_ps_to_bin_attr_extents():
    ips = pattern_structure.IntervalPS([1, 2, 3], 'ips')
    bin_extents_true = [
        ('ips: (1.0, 3.0)', frozenbitarray('111')),
        ('ips: (2.0, 3.0)', frozenbitarray('011')),
        ('ips: (3.0, 3.0)', frozenbitarray('001')),
        ('ips: (1.0, 2.0)', frozenbitarray('110')),
        ('ips: (1.0, 1.0)', frozenbitarray('100')),
        ('ips: ∅',          frozenbitarray('000'))
    ]
    assert list(ips.to_bin_attr_extents()) == bin_extents_true


def test_interval_numpy_ps_to_bin_attr_extents():
    nips = pattern_structure.IntervalNumpyPS([1, 2, 3], 'nips')
    bin_extents_true = [
        ('nips: (1.0, 3.0)', frozenbitarray('111')),
        ('nips: (2.0, 3.0)', frozenbitarray('011')),
        ('nips: (3.0, 3.0)', frozenbitarray('001')),
        ('nips: (1.0, 2.0)', frozenbitarray('110')),
        ('nips: (1.0, 1.0)', frozenbitarray('100')),
        ('nips: ∅',          frozenbitarray('000'))
    ]
    assert list(nips.to_bin_attr_extents()) == bin_extents_true
