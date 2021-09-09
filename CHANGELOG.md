# Changelog

## [0.1.3] - 2021-09-09
### Added

_Partially ordered set_
* Add POSet subpackage to clean up the code of ConceptLattice class;
* And add POSet visualization.

_Concept lattice_
* Add Lindig algorithm to construct a concept lattice. Thanks to @MetaPostRocker;
* And add ConceptLattice.read_json/write_json functions.

_Visualization_
* Add FCART-like Hasse diagram layout. Thanks to @MetaPostRocker;
* And add a function to count line intersections in Hasse diagram.

_Many valued context_ 
* Add MVContext.read_json/write_json functions.
  
### Changed
* Move visualizer layouts to a specific python module;
* Rename load_<x>/save_<x> functions to read_<x>/write_<x>;
* And split the repository into FCApy, FCApy_tutorials, FCApy_benchmarks, FCApy_papers.

### Fixed
* Drop build files from git;
* Make FormalContext hash calculation stable among different python kernel runs;
* And fix the levels of elements calculation in POSetVisualizer.  

## [0.1.2] - 2021-03-29

Optimize FormalContext with bitsets

### Added
* Add fcapy.context.bintable.BinTable class to encapsulate binary data processing

## [0.1.1] - 2021-03-25

Concept Lattices, PatternStructures, Visualization and a bit of ML

### Added

* Write class implementations for ConceptLattice, Pattern Structures and Many Valued Context from FCA;
* Add simple Concept Lattice visualization with networkx and plotly package;
* and start developing tools to use ConceptLattice as a Supervised ML model.



## [0.1.0] - 2020-12-04

Formal Context functionality

### Added

* Create FormalContext class,
* Set up the pipelines for Travis CI/CD, Codecov,
* and write basic documentation in readthedocs.org .