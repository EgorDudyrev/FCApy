import pytest
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
    with pytest.raises(NotImplementedError):
        aps.to_json(1)
    with pytest.raises(NotImplementedError):
        aps.from_json('1')


def test_interval_ps_extension_intention():
    LIB_INSTALLED['numpy'] = False
    ips = pattern_structure.IntervalPS([0, 1, 2, 3, 2])
    assert ips.extension_i(None) == [], "IntervalPS.extension_i failed"
    assert ips.extension_i((2, 3)) == [2, 3, 4], "IntervalPS.extension_i failed"
    assert ips.extension_i((2, 2)) == ips.extension_i(2), "IntervalPS.extension_i failed"

    LIB_INSTALLED['numpy'] = True
    ips = pattern_structure.IntervalPS([0, 1, 2, 3, 2])
    assert (ips.extension_i(None) == np.array([])).all(), "IntervalPS.extension_i failed"
    assert (ips.extension_i((2, 3)) == np.array([2, 3, 4])).all(), "IntervalPS.extension_i failed"
    assert (ips.extension_i((2, 2)) == np.array(ips.extension_i(2))).all(), "IntervalPS.extension_i failed"

    assert (ips.extension_i((2, 3), [0, 1, 2, 3, 4]) == np.array([2, 3, 4])).all(), "IntervalPS.extension_i failed"
    assert (ips.extension_i((2, 3), frozenset([0, 1, 2, 3, 4])) == np.array([2, 3, 4])).all(),\
        "IntervalPS.extension_i failed"
    assert (ips.extension_i((2, 3), np.array([0, 1, 2, 3, 4])) == np.array([2, 3, 4])).all(), \
        "IntervalPS.extension_i failed"

    ips = pattern_structure.IntervalPS([0, 1, 2, 3, 2])
    assert ips.intention_i([]) is None, 'IntervalPS.intention_i failed'
    assert ips.intention_i([0, 1, 3]) == (0, 3), "IntervalPS.intention_i failed"
    assert ips.intention_i([2, 4]) == (2, 2), "IntervalPS.intention_i failed"
    assert (ips.extension_i(ips.intention_i([1, 2, 4])) == [1, 2, 4]).all(), "IntervalPS.extension_i/intention_i failed"


def test_interval_ps_descriptions_tofrom_generators():
    ips = pattern_structure.IntervalPS([])
    description_true = (1, 2)
    generators_true = [(-math.inf, 2), (1, math.inf)]

    assert ips.description_to_generators(description_true, projection_num=0) == [(-math.inf, math.inf)]

    assert ips.description_to_generators(description_true, projection_num=1) == generators_true,\
        "IntervalPS.description_to_generators failed"
    assert ips.generators_to_description(generators_true) == description_true, \
        "IntervalPS.generators_to_description failed"
    assert ips.description_to_generators(
        ips.generators_to_description(generators_true), projection_num=1) == generators_true,\
        "IntervalPS.generators_to_description pipe failed"

    assert ips.description_to_generators(4, projection_num=1) == [(-math.inf, 4), (4, math.inf)],\
        "IntervalPS.description_to_generators failed"
    assert ips.generators_to_description([(-math.inf, 4), (4, math.inf)]) == 4, \
        "IntervalPS.generators_to_description failed"

    assert ips.description_to_generators(description_true, projection_num=2)[0] == description_true,\
        "IntervalPS.generators_to_description failed"


def test_interval_ps_tofrom_json():
    ips = pattern_structure.IntervalPS
    assert ips.to_json((1,1)) == '[1.0, 1.0]'
    assert ips.from_json('[1.0, 1.0]') == (1,1)
