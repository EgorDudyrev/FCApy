import pytest
from fcapy.mvcontext import pattern_structure


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


def test_interval_ps_extension_intention():
    ips = pattern_structure.IntervalPS([0, 1, 2, 3, 2])
    assert ips.extension_i((2, 3)) == [2, 3, 4], "IntervalPS.extension_i failed"
    assert ips.extension_i((2, 2)) == ips.extension_i(2), "IntervalPS.extension_i failed"
    assert ips.intention_i([0, 1, 3]) == (0, 3), "IntervalPS.intention_i failed"
    assert ips.intention_i([2, 4]) == 2, "IntervalPS.intention_i failed"
    assert ips.extension_i(ips.intention_i([1, 2, 4])) == [1, 2, 4], "IntervalPS.extension_i/intention_i failed"
