# FCApy
[![Travis (.com)](https://img.shields.io/travis/com/EgorDudyrev/FCApy)](https://travis-ci.com/github/EgorDudyrev/FCApy)
[![Read the Docs (version)](https://img.shields.io/readthedocs/fcapy/latest)](https://fcapy.readthedocs.io/en/latest/)
[![Codecov](https://img.shields.io/codecov/c/github/EgorDudyrev/FCApy)](https://codecov.io/gh/EgorDudyrev/FCApy)
[![GitHub](https://img.shields.io/github/license/EgorDudyrev/FCApy)](https://github.com/EgorDudyrev/FCApy/blob/main/LICENSE)

A library to work with formal (and pattern) concexts, concepts, lattices

Created under the guidance of S.O.Kuznetsov and A.A.Neznanov of HSE Moscow.

## Current state

The library provides an implementation of the Formal Context idea from FCA. An example of this is given in [here](../blob/main/notebooks/Formal%20Context.ipynb).

## Install
FCApy can be installed from [PyPI](https://pypi.org/project/shap):

<pre>
pip install fcapy
</pre>

The library has no strict dependencies. However one would better install it with the additional packages:
<pre>
pip install fcapy[all]
</pre> 

## Plans
The library will provide easy-to-use Python interface to work with Formal Concept Analysis (FCA) for both the scientists and ML practitioners.
In particular:
* formal (and pattern) contexts conversion from and to different formats (csv, cxt, etc.)
* construction of formal (and pattern) concepts via different algorithms for different needs (CbO, Sofia, etc.)
* construction and visualization of concept lattices
* a pipeline to use FCA as a supervised ML model

Functions to work with contexts, concepts and lattices will be placed in different subpackages. This will be done in order to minimize required dependencies if one would want to work with contexts or lattices only.
