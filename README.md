# FCApy
[![Travis (.com)](https://img.shields.io/travis/com/EgorDudyrev/FCApy)](https://travis-ci.com/github/EgorDudyrev/FCApy)
[![Read the Docs (version)](https://img.shields.io/readthedocs/fcapy/latest)](https://fcapy.readthedocs.io/en/latest/)
[![Codecov](https://img.shields.io/codecov/c/github/EgorDudyrev/FCApy)](https://codecov.io/gh/EgorDudyrev/FCApy)
[![GitHub](https://img.shields.io/github/license/EgorDudyrev/FCApy)](https://github.com/EgorDudyrev/FCApy/blob/main/LICENSE)

A python package to work with Formal Concept Analysis (FCA).

The package is written while working in ISSA laboratory of HSE Moscow.

## Install
FCApy can be installed from [PyPI](https://pypi.org/project/fcapy):

```console
pip install fcapy
```

The library has no strict dependencies. However, one would better install it with all the additional packages:
```console
pip install fcapy[all]
```

## Current state

The library implements the main artifacts from FCA theory:
* a formal context _(``context`` subpackage)_,
* and a concept lattice _(``lattice`` subpackage)_.

There are also some additional subpackages:
* ``visualizer`` to visualize the lattices,
* ``mvcontext`` implementing pattern structures and a many valued context,
* ``poset`` implementing partially ordered sets,
* and ``ml`` to test FCA in supervised machine learning scenario.

The following repositories complement the package:
* [FCApy_tutorials](https://github.com/EgorDudyrev/FCApy_tutorials)
* [FCApy_benchmarks](https://github.com/EgorDudyrev/FCApy_benchmarks)

### Formal context
The ``context`` subpackage implements a formal context from FCA theory.

Formal context `K = (G, M, I)` is a triple of set of objects `G`, set of attributes `M`, and mapping `I: G x M` between them. A natural way to represent a formal context is a binary table. The rows of such table represent objects `G`, columns represent attributes `M` and crosses in the table are elements from the mapping `I`.

`FormalContext` class provides two main functions:
* ``extension( attributes )`` - return a maximal set of objects which share ``attributes``
* ``intention( objects )`` - return a maximal set of attributes shared by ``objects``

These functions are also known as ''prime operations'' (denoted by `'`) or ``arrow operations''.

For example, 'animal_movement' context shows the connection between animals (objects) and actions (attributes) 
```python
!wget -q https://raw.githubusercontent.com/EgorDudyrev/FCApy/main/data/animal_movement.csv
from fcapy.context import FormalContext
K = FormalContext.read_csv('animal_movement.csv')

# Print the first five objects data
print(K[:5])
> FormalContext (5 objects, 4 attributes, 7 connections)
>      |fly|hunt|run|swim|
> dove |  X|    |   |    |
> hen  |   |    |   |    |
> duck |  X|    |   |   X|
> goose|  X|    |   |   X|
> owl  |  X|   X|   |    |
```
Now we can select all the animals who can both `fly` and `swim`: 
```python
print(K.extension( ['fly', 'swim'] ))
> ['duck', 'goose']
```
and all the actions both `dove` and `goose` can perform:
```python
print(K.intention( ['dove', 'goose'] ))
> ['fly']
```

So we state the following:
* the animals who can both `fly` and `swim` are only `duck` and `goose`;
* the only action both `dove` and `goose` do is `fly`.
At least, this is formally true in 'animal_movement' context. 


A detailed example is given in [this notebook](https://github.com/EgorDudyrev/FCApy_tutorials/blob/main/Formal%20Context.ipynb).
 
### Concept lattice

The `lattice` subpackage implements the concept lattice from FCA theory. The concept lattice `L` is a lattice of (formal) concepts.

A formal concept is a pair `(A, B)` of objects `A` and attributes `B`. Objects `A` are all the objects sharing attributes `B`. Attributes `B` are all the attributes describing objects `A`.

In other words:
* `A = extension(B)`
* `B = intention(A)` 

A concept `(A1, B1)` is bigger (more general) than a concept `(A2, B2)` if it describes the bigger set of objects (i.e. `A2` is a subset of `A1`, or, equivalently, `B1` is a subset of `B2`).

A lattice is an ordered set with the biggest and the smallest element. Thus the concept lattice is an ordered set of (formal) concepts with the biggest (most genereal) concept and the smallest (least general) concept.

Applied to 'animal_movement' context we get this ConceptLattice:
```python
# Load the formal context
!wget -q https://raw.githubusercontent.com/EgorDudyrev/FCApy/main/data/animal_movement.csv
from fcapy.context import FormalContext
K = FormalContext.read_csv('animal_movement.csv')

# Create the concept lattice
from fcapy.lattice import ConceptLattice
L = ConceptLattice.from_context(K)
```
The lattice contains 8 concepts:
```python
print(len(L))
> 8
```
with the most general and the most specific concepts indexes:
```python
print(L.top_concept_i, L.bottom_concept_i)
> 0, 7
```

One can draw Hasse diagram of the lattice by `visualizer` subpackage:
```python
import matplotlib.pyplot as plt
from fcapy.visualizer import ConceptLatticeVisualizer

plt.figure(figsize=(10, 5))

vsl = ConceptLatticeVisualizer(L)
vsl.draw_networkx(max_new_extent_count=5, draw_node_indices=True)

plt.xlim(-0.7,0.7)
plt.axis(False)
plt.tight_layout()
plt.show()
```
<p align="center">
  <img width="616" src="https://raw.githubusercontent.com/EgorDudyrev/FCApy/main/docs/images/animal_context_lattice.png" />
</p>

How to read the visualization:
* the concept #3 contains all the animals (objects) who can `fly`.
  These are `dove`, `goose` and `duck`. The latter two are taken from the more specific (smaller) concepts;
* the concept #4 represents all the animals who can both `run` (acc. to the more general concept #2) and `hunt` (acc. to the more general concept #1);
* etc.

### The other FCA artifacts

You can find more tutorials in [FCApy_tutorials](https://github.com/EgorDudyrev/FCApy_tutorials) repository.

They include some info on the use of FCA framework applied to non-binary data (MVContext), and supervised machine learning (DecisionLattice).
