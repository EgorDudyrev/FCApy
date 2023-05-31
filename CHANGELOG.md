# Changelog

## [0.1.4.2] - 2022-06-01

Elaborate Pattern Structures.
Rewrite Sofia algorithm to mine hundreds of most stable concepts on big data.
Add IntervalPS and SetPS to basic pattern structures.

## [0.1.4.1] - 2022-12-03

OSDA toolkit edition.
This version introduces monotonic concepts that are (among all)
relevant for Ordered Sets in Data Analysis course in HSE University

### Changed

* Add monotonic concepts support: a.k.a. "disjunctive" formal concepts*;
* Start refactoring BinTables: a class to work efficiently with tables of binary values. 

\* _A disjunctive formal concept `(A, B)` is a pair of objects `A` and attributes `B`. 
 The sets are s.t. each attribute from `B` describes at least one of the objects from `A`. 
 And `A` is the maximal set of objects corresponding to specific `B`._

## [0.1.4] - 2022-07-04

Pretty and easier-to-use visualizations via NetworkX.

### Added

Rewrite visualizer submodule to make visualizations more versatile and easy to use.
* Add LineVizNx: a class to visualize POSets and Concept Lattices via NetworkX  
* Add Mover: a class to simplify the positioning of nodes in a visualization
* Add many NetworkX-like parameters to AbstractLineViz to form an interface for future visualization extensions 

_Disclaimer_: The release was in production for too much time.
So something may not work properly (although it should).
I will try to publish the following releases more often.


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