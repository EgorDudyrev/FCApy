# FCApy
A library to work with formal (and pattern) concexts, concepts, lattices

Created under the guidance of S.O.Kuznetsov and A.A.Neznanov of HSE Moscow.

The library will provide easy-to-use Python interface to work with Formal Concept Analysis (FCA) for both the scientists and ML practitioners.
In particular:
* formal (and pattern) contexts conversion from and to different formats (csv, cxt, etc.)
* construction of formal (and pattern) concepts via different algorithms for different needs (CbO, Sofia, etc.)
* construction and visualization of concept lattices
* a pipeline to use FCA as a supervised ML model

Functions to work with contexts, concepts and lattices will be placed in different subpackages. This will be done in order to minimize required dependencies if one would want to work with contexts or lattices only.
