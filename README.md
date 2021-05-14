# FCApy
[![Travis (.com)](https://img.shields.io/travis/com/EgorDudyrev/FCApy)](https://travis-ci.com/github/EgorDudyrev/FCApy)
[![Read the Docs (version)](https://img.shields.io/readthedocs/fcapy/latest)](https://fcapy.readthedocs.io/en/latest/)
[![Codecov](https://img.shields.io/codecov/c/github/EgorDudyrev/FCApy)](https://codecov.io/gh/EgorDudyrev/FCApy)
[![GitHub](https://img.shields.io/github/license/EgorDudyrev/FCApy)](https://github.com/EgorDudyrev/FCApy/blob/main/LICENSE)

A library to work with formal (and pattern) contexts, concepts, lattices

Created under the guidance of S.O.Kuznetsov and A.A.Neznanov of HSE Moscow.

## Install
FCApy can be installed from [PyPI](https://pypi.org/project/fcapy):

<pre>
pip install fcapy
</pre>

The library has no strict dependencies. However one would better install it with all the additional packages:
<pre>
pip install fcapy[all]
</pre>

## Current state

The library provides an implementation of the Formal Context idea from FCA. An example of this is given in [here](https://github.com/EgorDudyrev/FCApy/blob/main/notebooks/Formal%20Context.ipynb).

The library consists of 4 main subpackages:
* context
* lattice
* mvcontext
* ml

### Context
An implementation of Formal Context from FCA theory.

Formal Context K = (G, M, I) is a triple of set of objects G, set of attributes M and a mapping I between them. A natural way to represent a Formal Context is a binary table.

Formal Context provides two main functions:
* ``extension(attributes)`` - return a maximal set of objects which share ``attributes``
* ``intention(objects)`` - return a maximal set of attributes shared by ``objects``

These functions are also known as "prime (') operations", "arrow operations" 

For example, 'animal_movement' context shows the connection between animals (objects) and actions (attributes) 
```python
!wget https://raw.githubusercontent.com/EgorDudyrev/FCApy/main/data/animal_movement.csv
ctx = read_csv('animal_movement.csv')

print(ctx[:5])
> FormalContext (5 objects, 4 attributes, 7 connections)
>      |fly|hunt|run|swim|
> dove |  X|    |   |    |
> hen  |   |    |   |    |
> duck |  X|    |   |   X|
> goose|  X|    |   |   X|
> owl  |  X|   X|   |    |

print(ctx.extension(['fly', 'swim']))
> ['duck', 'goose']

print(ctx.intention(['dove', 'goose']))
> ['fly']
```

Thus we can state that all the animals who can both 'fly' and 'swim' are 'duck' and 'goose'. 
The only action both 'dove' and 'goose' can performs if 'fly'.
At least this is formally true in 'animal_movement' context. 


A detailed example is given this [notebook](https://github.com/EgorDudyrev/FCApy/blob/main/notebooks/Formal%20Context.ipynb).
 
### Lattice

An implementation of Concept Lattice object from FCA theory. That is a partially ordered set of Formal concepts.

A Formal Concept is a pair `(A, B)` of objects `A` and attributes `B` s.t. `A` contains all the objects which share attributes `B` and `B` contains all the attributes which shared by objects `A`.

In other words:
* `A = extension(B)`
* `B = intention(A)` 

A concept `(A1, B1)` is bigger (more general) than a concept `(A2, B2)` if it describes the bigger set of objects (i.e. `A2` is a subset of `A1`, or (which is the same) `B1` is a subset of `B2`)

Applied to 'animal_movement' context we get this ConceptLattice:
```python
from fcapy.lattice import ConceptLattice
ltc = ConceptLattice.from_context(ctx)
print(len(ltc.concepts))
> 8

import matplotlib.pyplot as plt
from fcapy.visualizer import Visualizer

plt.figure(figsize=(10, 5))
vsl = Visualizer(ltc)
vsl.draw_networkx(max_new_extent_count=5)
plt.xlim(-1,1.5)
plt.show()
```
<p align="center">
  <img width="616" src="https://raw.githubusercontent.com/EgorDudyrev/FCApy/main/docs/images/animal_context_lattice.png" />
</p>

In this Concept Lattice a concept #3 contains all the objects which can 'fly'. These are 'dove' plus objects from more specific concept #6: 'goose' and 'duck'.

A concept #4 represents all the animals who can 'run' (acc. to more general concept #2) and 'hunt' (acc. to more general concept #1).  

### MVContext

An implementation of Many Valued Context from FCA theory.

MVContext is a generalization of Formal Context. It allows FCA to work with any kind of object description defined by Pattern Structures.

Pattern Structure `D` is a set of descriptions s.t. we can use to it to run `extension` and `intention` operations. 

At this moment, only numerical features are supported.

```python
#load data from sci-kit learn
from sklearn.datasets import fetch_california_housing
california_data = fetch_california_housing(as_frame=True)
df = california_data['data'].round(3)

from fcapy.mvcontext import MVContext, PS
# define a specific type of PatternStructure for each column of a dataframe
pattern_types = {f: PS.IntervalPS for f in df.columns}
# create a MVContext
mvctx = MVContext(df.values, pattern_types=pattern_types, attribute_names=df.columns)
print( mvctx )
> ManyValuedContext (20640 objects, 8 attributes)

# Get the common description of the first 2 houses
print( mvctx.intention(['0', '1']) )
> {'MedInc': (8.301, 8.325), 'HouseAge': (21.0, 41.0), 'AveRooms': (6.238, 6.984),
> 'AveBedrms': (0.972, 1.024), 'Population': (322.0, 2401.0), 'AveOccup': (2.11, 2.556),
> 'Latitude': (37.86, 37.88), 'Longitude': (-122.23, -122.22)}

# Get a number of houses with an age in a closed interval [10, 21]
print( len(mvctx.extension({'HouseAge': (10, 21)})) )
> 5434
```

### ML

A number of algorithms to use FCA in a supervised ML scenario.

```python
#load data from sci-kit learn
from sklearn.datasets import fetch_california_housing
california_data = fetch_california_housing(as_frame=True)
df = california_data['data']
y = california_data['target']

from fcapy.mvcontext import MVContext, PS
# define a specific type of PatternStructure for each column of a dataframe
pattern_types = {f: PS.IntervalPS for f in df.columns}
# create a MVContext
mvctx = MVContext(
    df.values, target=y.values,
    pattern_types=pattern_types, attribute_names=df.columns
)
print( mvctx )
> ManyValuedContext (20640 objects, 8 attributes)

# split to train and test set
mvctx_train, mvctx_test = mvctx[:16000], mvctx[16000:]

# Initialize a DecisionLattice model (which uses RandomForest in the construction process)
from fcapy.ml.decision_lattice import DecisionLatticeRegressor
rf_params = {'n_estimators':5, 'max_depth':10}
dlr = DecisionLatticeRegressor(algo='RandomForest', algo_params={'rf_params':rf_params})

# Fit the model
%time dlr.fit(mvctx_train, use_tqdm=True)
> CPU times: user 43.1 s, sys: 67.8 ms, total: 43.1 s
> Wall time: 43.1 s

# Predict the values
preds_train_dlr = dlr.predict(mvctx_train)
preds_test_dlr = dlr.predict(mvctx_test)

## sometimes a test object can not be described by any concept from ConceptLattice
## in this case the model predicts None. We replace it with mean target value over the train context
preds_test_dlr = [p if p is not None else mvctx_train.target.mean() for p in preds_test_dlr]

# Calculate the MSE
from sklearn.metrics import mean_squared_error
mean_squared_error(mvctx_train.target, preds_train_dlr), mean_squared_error(mvctx_test.target, preds_test_dlr)
> (0.15651125729264054, 0.5543609802892809)

# Fit a Random Forest model for the comparison
from sklearn.ensemble import RandomForestRegressor
rf = RandomForestRegressor(**rf_params)
%time rf.fit(df[:16000], y[:16000])
> CPU times: user 240 ms, sys: 0 ns, total: 240 ms
> Wall time: 238 ms

preds_train_rf = rf.predict(df[:16000])
preds_test_rf = rf.predict(df[16000:])

mean_squared_error(mvctx_train.target, preds_train_rf), mean_squared_error(mvctx_test.target, preds_test_rf)
> (0.16501598118202618, 0.48447718343174856)
```

DecisionLattice works slower and gives less accurate test predictions than a Random Forest. For now...
 
## Plans
* Refactor the library to make it more easy-to-use
* Optimize the library to make it work faster (e.g. add parallelization)
