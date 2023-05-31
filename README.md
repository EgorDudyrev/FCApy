# FCApy

[![PyPi](https://img.shields.io/pypi/v/fcapy)](https://pypi.org/project/fcapy)
[![GitHub Workflow](https://img.shields.io/github/actions/workflow/status/EgorDudyrev/caspailleur/python-package.yml?logo=github)](https://github.com/EgorDudyrev/fcapy/actions/workflows/python-package.yml)
[![Read the Docs (version)](https://img.shields.io/readthedocs/fcapy/latest)](https://fcapy.readthedocs.io/en/latest/)
[![Codecov](https://img.shields.io/codecov/c/github/EgorDudyrev/FCApy)](https://codecov.io/gh/EgorDudyrev/FCApy)
[![GitHub](https://img.shields.io/github/license/EgorDudyrev/FCApy)](https://github.com/EgorDudyrev/FCApy/blob/main/LICENSE)

A python package to work with Formal Concept Analysis (FCA).

## Install
FCApy can be installed from [PyPI](https://pypi.org/project/fcapy):

```console
pip install fcapy[all]
```

*The appendix [all] installs additional packages like numpy and scikit-learn
(see more in [setup.py](https://github.com/EgorDudyrev/FCApy/blob/main/setup.py)).*

*This option is preferred, but not obligatory.*


## Gentle Intro to Formal Concept Analysis  

**Formal Concept Analysis (FCA)** is a mathematical framework aimed at simplifying the data analysis.

To achieve so, FCA introduces a **concept lattice**: a hierarchical representation of the dataset.
A concept lattice can be visualized in an appealing tree-like manner,
while keeping all the dependencies of the corresponding binary dataset.

The following Figure compares the tabular, Formal Context-based data representation (on the left),
with the hierarchical, Concept Lattice-based data representation on the right. Both representations describe the same ["Live in water"](https://upriss.github.io/fca/examples.html) dataset.
But the right subfigure also unravels the dichotomy between the ones who "can move" (i.e. animals) and the ones who "needs chlorophyll" (i.e. plants).

![Live in water representation comparison](https://github.com/EgorDudyrev/FCApy/blob/main/docs/images/live_in_water_representation_comparison.png?raw=true  "Live in water representation comparison")

The right subfigure highlights 'the structure' of the data.
Yet, it still contains exactly the same dependencies as the tabular view on the left.
For example, the table says that a "fish leech" is something that "needs water to live", "lives in water", and "can move".
The same description can be derived from the diagram:
a "fish leech" "can move" and "needs water to live" as it derives from the respectively entitled nodes,
and a "fish leech" "lives in water" since its node is coloured blue.

Formal Concept Analysis concentrates on analysing binary datasets.
However, there are many extensions to analyse more complex data:
e.g. Pattern Structures, Relational Concept Analysis, Fuzzy Concept Analysis, etc.
Also, in general, any kind of data can be binarized to some extent.
For example, decision tree algorithms intrinsically binarize the data all the time.  

*[Source code to generate Figure](https://github.com/EgorDudyrev/FCApy_tutorials/blob/main/Lattice%20Visualization/Visualizing_lattice.ipynb)* 


## Current state of FCApy

The library implements the main artifacts from FCA theory:
* a formal context _(``context`` subpackage)_, and
* a concept lattice _(``lattice`` subpackage)_.

There are also some additional subpackages:
* ``visualizer`` to visualize the lattices,
* ``mvcontext`` implementing pattern structures and a many valued context,
* ``poset`` implementing partially ordered sets, and
* ``ml`` to test FCA in supervised machine learning scenario.

The following repositories complement the package:
* [FCApy_tutorials](https://github.com/EgorDudyrev/FCApy_tutorials)
* [FCApy_benchmarks](https://github.com/EgorDudyrev/FCApy_benchmarks)


### Formal context
***NB:** The following code suits the current GitHub version of the package.
If it does not run well on package installed from PyPi,
please consider the corresponding README available on PyPi.*

The ``context`` subpackage implements a formal context from FCA theory.

Formal context `K = (G, M, I)` is a triplet of set of objects `G`, set of attributes `M`, and mapping `I: G x M` between them.
A natural way to represent a formal context is a binary table.
The rows of such table represent objects `G`, columns represent attributes `M` and crosses in the table are elements from the mapping `I`.

`FormalContext` class provides two main functions:
* ``extension( attributes )`` - return a maximal set of objects which share ``attributes``
* ``intention( objects )`` - return a maximal set of attributes shared by ``objects``

These functions are also known as ''prime operations'' (denoted by `'`) or ``arrow operations''.

For example, 'animal_movement' context shows the connection between animals (objects) and actions (attributes) 
```python
import pandas as pd
from fcapy.context import FormalContext
url = 'https://raw.githubusercontent.com/EgorDudyrev/FCApy/main/data/animal_movement.csv'
K = FormalContext.from_pandas(pd.read_csv(url, index_col=0))

# Print the first five objects data
print(K[:5])
```
> <pre>
> FormalContext (5 objects, 4 attributes, 7 connections) 
>      |fly|hunt|run|swim|
> dove |  X|    |   |    |
> hen  |   |    |   |    |
> duck |  X|    |   |   X|
> goose|  X|    |   |   X|
> owl  |  X|   X|   |    |
> </pre>


Now we can select all the animals who can both `fly` and `swim`: 
```python
print(K.extension( ['fly', 'swim'] ))
```
> ['duck', 'goose']

and all the actions both `dove` and `goose` can perform:
```python
print(K.intention( ['dove', 'goose'] ))
```
> ['fly']

So we state the following:
* the animals who can both `fly` and `swim` are only `duck` and `goose`;
* the only action both `dove` and `goose` do is `fly`.
At least, this is formally true in 'animal_movement' context. 


A detailed example is given in
[this notebook](https://github.com/EgorDudyrev/FCApy_tutorials/blob/main/Formal%20Context.ipynb).
 

### Concept lattice

The `lattice` subpackage implements the concept lattice from FCA theory.
The concept lattice `L` is a lattice of (formal) concepts.

A formal concept is a pair `(A, B)` of objects `A` and attributes `B`.
Objects `A` are all the objects sharing attributes `B`.
Attributes `B` are all the attributes describing objects `A`.

In other words:
* `A = extension(B)`
* `B = intention(A)` 

A concept `(A1, B1)` is bigger (more general) than a concept `(A2, B2)`
if it describes the bigger set of objects (i.e. `A2` is a subset of `A1`, or, equivalently, `B1` is a subset of `B2`).

A lattice is an ordered set with the biggest and the smallest element.
Thus the concept lattice is an ordered set of (formal) concepts
with the biggest (most genereal) concept and the smallest (least general) concept.

Applied to 'animal_movement' context we get this ConceptLattice:
```python
# Load the formal context
import pandas as pd
from fcapy.context import FormalContext
url = 'https://raw.githubusercontent.com/EgorDudyrev/FCApy/main/data/animal_movement.csv'
K = FormalContext.from_pandas(pd.read_csv(url, index_col=0))

# Create the concept lattice
from fcapy.lattice import ConceptLattice
L = ConceptLattice.from_context(K)
```

The lattice contains 8 concepts:
```python
print(len(L))
```
> 8

with the most general and the most specific concepts indexes:

```python
print(L.top, L.bottom)
```
> 0, 7

One can draw line diagram of the lattice by `visualizer` subpackage:
```python
import matplotlib.pyplot as plt
from fcapy.visualizer import LineVizNx
fig, ax = plt.subplots(figsize=(10, 5))
vsl = LineVizNx()
vsl.draw_concept_lattice(L, ax=ax, flg_node_indices=True)
ax.set_title('"Animal movement" concept lattice', fontsize=18)
plt.tight_layout()
plt.show()
```

> ![Animal Movement concept lattice](https://github.com/EgorDudyrev/FCApy/blob/main/docs/images/animal_context_lattice.png?raw=true  "Animal movement concept lattice")

How to read the visualization:
* the concept #3 contains all the animals (objects) who can `fly`.
  These are `dove`, `goose` and `duck`. The latter two are taken from the more specific (smaller) concepts;
* the concept #4 represents all the animals who can both `run` (acc. to the more general concept #2) and `hunt` (acc. to the more general concept #1);
* etc.

### The other FCA artifacts

You can find tutorials in [FCApy_tutorials](https://github.com/EgorDudyrev/FCApy_tutorials) repository.

They include some info on the use of FCA framework applied to non-binary data (MVContext),
and supervised machine learning (DecisionLattice).
