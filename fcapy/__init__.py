import warnings

try:
    import json
    del json
except ImportError:
    msg = 'The package `json` is not install. Thus all the functions to read/write json files will raise ImportError' +\
        "Run `pip install json` to solve the problem"
    warnings.warn(msg)
