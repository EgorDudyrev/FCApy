from fcapy.utils import utils


def test_powerset():
    ps = set(utils.powerset([1, 2, 3]))
    ps_true = {(), (1,), (2,), (3,), (1, 2), (1, 3), (2, 3), (1, 2, 3)}
    assert ps == ps_true, 'utils.powerset failed. Powerset does not give the expected result'
