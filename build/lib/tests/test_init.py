import pytest
from fcapy import check_installed_packages


def test_check_package():
    func_name = f'fcapy.{check_installed_packages.__name__}'
    installed_dict = check_installed_packages({'json': 'Save and load json files'})
    assert installed_dict['json'], f'{func_name} failed. It said "json" package is not installed'

    with pytest.warns(Warning) as record:
        installed_dict = check_installed_packages({'json123': 'Fake package'})
    assert not installed_dict['json123'], f'{func_name} failed. It said fake "json1234" package is installed'
    assert record[0].message.args[0] == 'Package "json123" is not found. Fake package',\
        f'{func_name} failed. Check warning message format'
