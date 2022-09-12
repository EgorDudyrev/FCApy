import warnings


def check_installed_packages(package_descriptions):
    installed_dict = {}
    for name, desc in package_descriptions.items():
        try:
            exec(f"import {name}")
            installed_dict[name] = True
        except ModuleNotFoundError:
            warnings.warn(f'Package "{name}" is not found. {desc}')
            installed_dict[name] = False
    return installed_dict


PACKAGE_DESCRIPTION = {
    'pandas': "The package is used to create a FormalContext based on pandas.DataFrame and vice versa",
    'tqdm': "The package helps to track the progress of looped functions and estimate their time to complete",
    'numpy': "The package Uses C++ and vectorized matrix multiplication to speed up IntervalPS execution",
    'bitsets': "The package greatly optimizes BinTables execution",
    'bitarray': "The package greatly optimizes BinTables execution",
    'networkx': "The package to convert POSets to Graphs and to visualize them as graphs",
}
LIB_INSTALLED = check_installed_packages(PACKAGE_DESCRIPTION)
