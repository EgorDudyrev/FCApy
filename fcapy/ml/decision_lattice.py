"""
This module provides 'DecisionLatticeClassifier' and 'DecisionLatticeRegressor' classes
to use 'ConceptLattice' in a DecisionTree-like manner

"""
from frozendict import frozendict
import numpy as np
from enum import Enum
from copy import deepcopy

from fcapy.mvcontext.mvcontext import MVContext
from fcapy.lattice.pattern_concept import PatternConcept
from fcapy.lattice import ConceptLattice
from fcapy.poset import POSet

from sklearn.tree import BaseDecisionTree
from xgboost import Booster


class PredictFunctions(Enum):
    AVGMAX = 'avg.max'
    SUMDIFF = 'sum.diff'


class DecisionLatticePredictor:
    """
    An abstract class to inherit 'DecisionLatticeClassifier' and 'DecisionLatticeRegressor' from

    Methods
    -------
    fit(context)  :noindex:
        Construct a concept lattice based on ``context``
        and calculate interestingness measures to predict the ``context.target`` values
    predict(context)  :noindex:
        Predict ``context.target`` variables based on ``context.data``

    """
    def __init__(
            self, algo='Sofia', use_generators=False, algo_params=None,
            generators_algo='approximate', random_state=None,
            prediction_func: PredictFunctions = PredictFunctions.AVGMAX
    ):
        """Initialize the DecisionLatticePredictor

        Parameters
        ----------
        algo: `str`
            Algorithm to construct a ConceptLattice.
            The possible values of ``algo`` are shown in `ConceptLattice.from_context()` function
        use_generators: `bool`
            A flag whether to use closed intents of concepts to describe objects (if False) or their generators (o/w)
        algo_params: `dict`
            A dictionary with specific parameters for an algorithm ``algo``.
        generators_algo: `str` in {'exact', 'approximate'}
            An algorithm to compute generators of closed intents.
            'exact' works in exponential time but shows good result
            `approximate` works in a matter of milliseconds but shows awful result
        random_state: `int`
            A random seed of an algorithms. It is used RandomForest algorithm only

        """
        self._algo = algo

        self._lattice = None
        self._use_generators = use_generators
        self._generators_algo = generators_algo
        self._algo_params = algo_params if algo_params is not None else dict()
        self._random_state = random_state if random_state is not None else 0
        self._algo_params['random_state'] = self._random_state
        self._prediction_func = prediction_func
        self._decisions = None

    def fit(self, context: MVContext, use_tqdm=False):
        """Fit a DecisionLattice to the ``context``

        Parameters
        ----------
        context: `FormalContext` or `MVContext`
            A training context. Target values should be kept in ``context.target`` property
        use_tqdm: `bool`
            A flag whether to visualize algorithm progress with `tqdm` bar

        Returns
        -------

        """
        self._lattice = ConceptLattice.from_context(context, algo=self._algo, use_tqdm=use_tqdm, **self._algo_params)
        if self._use_generators:
            self.compute_generators(context, self._generators_algo, use_tqdm)
        for c_i, c in enumerate(self._lattice):
            metrics = self.calc_concept_prediction_metrics(c_i, context.target)
            c.measures = dict(metrics, **c.measures)

    def predict(self, context: MVContext, use_tqdm=False):
        """Use fitted model to predict target values of a context

        Parameters
        ----------
        context: `FormalContext` or `MVContext`
            A context to predict
        use_tqdm: `bool`
            A flag whether to visualize algorithm progress with `tqdm` bar

        Returns
        -------
        predictions: `list` of `float`
            Prediction of target values for a given ``context``

        """
        bottom_concepts, traced_concepts, generators_extents = self._lattice.trace_context(
            context, use_object_indices=True, use_generators=self._use_generators, use_tqdm=use_tqdm,
            return_generators_extents=True)
        if self._prediction_func == PredictFunctions.AVGMAX:
            predictions = [self.average_concepts_predictions(bottom_concepts[g_i]) for g_i in range(context.n_objects)]
        elif self._prediction_func == PredictFunctions.SUMDIFF:
            predictions = self._sum_difference_predictions(generators_extents, n_objects=len(context.object_names))
        else:
            raise ValueError(f'Unsupported predict function: {self._prediction_func}')
        return predictions

    @property
    def lattice(self):
        """The ConceptLattice used by the DecisionLattice model"""
        return self._lattice

    @property
    def algo_params(self):
        """Dictionary of algorithm specific parameters"""
        return self._algo_params

    @property
    def use_generators(self):
        """A flag whether to use closed intents of concepts (if set False) or their generators (o/w)

        Can be changed after the model is fitted to the data
        """
        return self._use_generators

    @use_generators.setter
    def use_generators(self, val: bool):
        self._use_generators = val

    def compute_generators(self, context, algo, use_tqdm):
        """Compute generators of closed intents of concepts from the `ConceptLattice`

        Parameters
        ----------
        context: `FormalContext` or `MVContext`
            A context to compute generators on
        algo: `str` of {'exact', 'approximate'}
            An algorithm to compute generators of closed intents.
            'exact' works in exponential time but shows good result
            `approximate` works in a matter of milliseconds but shows awful result
        use_tqdm: `bool`
            A flag whether to visualize the progress of the algorithm by `tqdm` bar

        Returns
        -------

        """
        self._lattice._generators_dict = self._lattice.get_conditional_generators_dict(
                context, use_tqdm=use_tqdm, algo=algo)

    def calc_concept_prediction_metrics(self, c_i, Y):
        """Abstract function to instantiate in subclasses. Calculate the concept measure used for target prediction"""
        raise NotImplementedError

    def average_concepts_predictions(self, concepts_i):
        """Abstract function to instantiate in subclasses. Calculate an average prediction of a subset of concepts"""
        raise NotImplementedError

    def _sum_difference_predictions(self, generators_extents, n_objects):
        predictions = np.zeros(n_objects)
        for ge in generators_extents:
            predictions[list(ge['ext_'])] += self._decisions[(ge['superconcept_i'], ge['concept_i'], ge['gen'])]
        return predictions

    @staticmethod
    def _parse_dt_arrays_to_drules(children_left, children_right, feature, threshold, target,
                                   context: MVContext, eps):
        """Compute the set generalized decision rules data based on the generalized decision tree data

        Parameters
        ----------
        children_left: `list` of `int`
            A list of left children indexes of each node in the tree
        children_right: `list` of `int`
            A list of right children indexes of each node in the tree
        feature: `list` of `int`
            A list of indexes of features used for splitting in each node in the tree
        threshold: `list` of `float`
            A real valued threshold for splitting in each node in the tree
        target: `list` of `float`
            A real value to predict in each node in the tree
        context: `MVContext`
            A ManyValued context the tree was constructed
        eps: `float`
            A real value used in replacing semiclosed intervals of the tree by closed intervals of decision rules
            E.g. an interval [a, b) is replaced by an interval [a, b-eps]

        Returns
        -------
        direct_premises: `list` of `dict`
            The list of new premises of the children nodes compared to the premise of their parent nodes
        dtargets: `list` of `float`
            The list of deltas of children targets compared to their parent targets
        direct_children: `list` of `int`
            The list of indexes of nodes in the tree
        direct_parents: `list` of `int`
            The list of parents of the nodes
        children_dict: `dict` of type {`parent_i`: `set` of children indexes  }
            The dict mapping each node index to the indexes of its children
        premises: `list` of `frozendict`
            The full premises of each node
        """
        parents_dict_left = {child_i: parent_i for parent_i, child_i in enumerate(children_left) if child_i != -1}
        parents_dict_right = {child_i: parent_i for parent_i, child_i in enumerate(children_right) if child_i != -1}
        parents_dict = {**parents_dict_left, **parents_dict_right}

        n_rules = len(target)

        direct_parents = [None] + [parents_dict[node_i] for node_i in range(1, n_rules)]
        direct_children = list(range(len(target)))
        direct_premises = [frozendict({})]
        premises = [frozendict({})]

        for node_i in range(1, n_rules):
            is_left_child = node_i in parents_dict_left
            parent_i = parents_dict[node_i]

            descr = (-np.inf, threshold[parent_i]) if is_left_child else (threshold[parent_i] + eps, np.inf)
            premise = {feature[parent_i]: descr}
            direct_premises.append(frozendict(premise))

            for ps_i, parent_descr in premises[parent_i].items():
                premise[ps_i] = context.pattern_structures[ps_i].generators_to_description(
                    [parent_descr, descr]) if ps_i in premise else parent_descr
            premises.append(frozendict(premise))

        direct_subelements_dict = ConceptLattice._transpose_hierarchy(
            {child_i: {parent_i} for child_i, parent_i in parents_dict.items()})

        dtargets = np.concatenate([target[:1], target[1:] - target[direct_parents[1:]]])

        return direct_premises, dtargets, direct_children, direct_parents, direct_subelements_dict, premises

    @classmethod
    def _parse_dtsklearn_to_direct_drules(cls, dt, context: MVContext, eps=1e-9):
        """Parse a decision tree ``dt`` of sklearn package to the set of decision rules

        Parameters
        ----------
        dt: `sklearn.tree.DecisionTreeClassifier` or `sklearn.tree.DecisionTreeRegressor`
            A decision tree to parse
        context: `MVContext`
            A ManyValued context the tree was constructed
        eps: `float`
            A real value used in replacing semiclosed intervals of the tree by closed intervals of decision rules
            E.g. an interval [a, b) is replaced by an interval [a, b-eps]

        Returns
        -------
        direct_premises: `list` of `dict`
            The list of new premises of the children nodes compared to the premise of their parent nodes
        dtargets: `list` of `float`
            The list of deltas of children targets compared to their parent targets
        direct_children: `list` of `int`
            The list of indexes of nodes in the tree
        direct_parents: `list` of `int`
            The list of parents of the nodes
        children_dict: `dict` of type {`parent_i`: `set` of children indexes  }
            The dict mapping each node index to the indexes of its children
        premises: `list` of `frozendict`
            The full premises of each node

        """
        return cls._parse_dt_arrays_to_drules(
            dt.tree_.children_left, dt.tree_.children_right,
            dt.tree_.feature, dt.tree_.threshold, dt.tree_.value.flatten(),
            context, eps)

    @classmethod
    def _parse_xgbooster_to_direct_drules(cls, xgbooster, context: MVContext, eps=1e-9):
        """

        Parameters
        ----------
        xgbooster: `xgboost.Booster`
            An element of XGBoost ensembles to parse
        context: `MVContext`
            A ManyValued context the tree was constructed
        eps: `float`
            A real value used in replacing semiclosed intervals of the tree by closed intervals of decision rules
            E.g. an interval [a, b) is replaced by an interval [a, b-eps]

        Returns
        -------
        direct_premises: `list` of `dict`
            The list of new premises of the children nodes compared to the premise of their parent nodes
        dtarget: `list` of `float`
            The list of deltas of children targets compared to their parent targets
        direct_children: `list` of `int`
            The list of indexes of nodes in the tree
        direct_parents: `list` of `int`
            The list of parents of the nodes
        children_dict: `dict` of type {`parent_i`: `set` of children indexes  }
            The dict mapping each node index to the indexes of its children
        premises: `list` of `frozendict`
            The full premises of each node

        """
        trees_df = xgbooster.trees_to_dataframe()
        children_left = [int(n_id.split('-')[1]) if isinstance(n_id, str) else -1 for n_id in trees_df['Yes']]
        children_right = [int(n_id.split('-')[1]) if isinstance(n_id, str) else -1 for n_id in trees_df['No']]
        target = trees_df['Gain']
        threshold = trees_df['Split'].values
        feature = [int(f[1:]) if f != 'Leaf' else -2 for f in trees_df['Feature']]

        direct_premises, _, direct_children, direct_parents, direct_subelements_dict, premises =\
            cls._parse_dt_arrays_to_drules(children_left, children_right, feature, threshold, target, context, eps)

        target = (trees_df['Gain'] * (trees_df['Feature'] == 'Leaf')).values
        leaf_nodes = trees_df.index[trees_df['Feature'] == 'Leaf'].values
        parent_nodes = sorted(set(direct_parents[n_id] for n_id in leaf_nodes))
        while len(parent_nodes) > 0:
            n_id = parent_nodes.pop(0)
            if direct_parents[n_id] is not None:
                parent_nodes.append(direct_parents[n_id])

            target[n_id] = (target[children_left[n_id]] + target[children_right[n_id]]) / 2

        dtarget = np.concatenate([target[:1], target[1:] - target[direct_parents[1:]]])

        return direct_premises, dtarget, direct_children, direct_parents, direct_subelements_dict, premises

    def __iadd__(self, other):
        """Inplace summation of DecisionLattices

        S.t. the predictions of the sum equal to the sum of predictions of the summands
        """
        # 1. Uniting up the elements
        new_concepts = [c for c in other.lattice if c not in self.lattice]
        for c in new_concepts:
            self.lattice.add(c)

        other_self_c_i_map = {other_c_i: self.lattice.index(c) for other_c_i, c in enumerate(other.lattice)}

        # 2. Uniting the generators
        for other_c_i, other_gens in other.lattice._generators_dict.items():
            self_c_i = other_self_c_i_map[other_c_i]
            if self_c_i not in self.lattice._generators_dict:
                self.lattice._generators_dict[self_c_i] = {}

            for other_parent_i, gens in other_gens.items():
                sum_parent_i = other_self_c_i_map[other_parent_i]
                self.lattice._generators_dict[self_c_i][sum_parent_i] =\
                    self.lattice._generators_dict[self_c_i].get(sum_parent_i, []) + gens

        # 3. Uniting the decisions
        for old_key, dy in other._decisions.items():
            old_parent_i, old_c_i, gen = old_key
            self_key = (other_self_c_i_map.get(old_parent_i), other_self_c_i_map[old_c_i], gen)
            self._decisions[self_key] = self._decisions.get(self_key, 0) + dy

        return self

    def __add__(self, other):
        """Summation of DecisionLattices

        S.t. the predictions of the sum equal to the sum of predictions of the summands
        """
        dl_sum = deepcopy(self)
        dl_sum += other
        return dl_sum

    def __imul__(self, other: float):
        """Inplace multiplication of DecisionLattices by a number"""
        self._decisions = {k: v * other for k, v in self._decisions.items()}
        return self

    def __mul__(self, other: float):
        """Multiplication of DecisionLattices by a number"""
        dl_mul = deepcopy(self)
        dl_mul *= other
        return dl_mul

    def __itruediv__(self, other: float):
        """Inplace division of DecisionLattices by a number"""
        return self.__imul__(1/other)

    def __truediv__(self, other: float):
        """Division of DecisionLattices by a number"""
        return self.__mul__(1/other)

    @classmethod
    def from_decision_tree(cls, dtree, context: MVContext):
        raise NotImplementedError

    @classmethod
    def from_random_forest(cls, rf, context: MVContext):
        raise NotImplementedError

    @classmethod
    def from_gradient_boosting(cls, gb, context: MVContext):
        raise NotImplementedError

    def shap_values(self, context: MVContext):
        """WARNING!!! The function does not return True shap_values. Just the first approximation"""
        _, _, generators_extents = self._lattice.trace_context(
            context, use_object_indices=True, use_generators=True, use_tqdm=False,
            return_generators_extents=True)
        sv = np.zeros((len(context.object_names), len(context.attribute_names)))
        for ge in generators_extents:
            if ge['superconcept_i'] is None:
                continue
            ps_is = list(ge['gen'].keys())
            dy = self._decisions[(ge['superconcept_i'], ge['concept_i'], ge['gen'])]

            dy_norm = dy / len(ps_is)
            for ps_i in ps_is:
                sv[list(ge['ext_']), ps_i] += dy_norm

        bias = self._decisions[(None, self._lattice.top, frozendict({}))]
        return sv, bias


class DecisionLatticeClassifier(DecisionLatticePredictor):
    """
    A class which combines DecisionTree ideas with Concept Lattice to solve Classification tasks

    Methods
    -------
    fit(context)  :noindex:
        Construct a concept lattice based on ``context``
        and calculate interestingness measures to predict the ``context.target`` values
        (Inherited from `DecisionLatticePredictor` class)
    predict(context)  :noindex:
        Predict ``context.target`` labels based on ``context.data``
        (Inherited from `DecisionLatticePredictor` class)
    predict_proba(context)  :noindex:
        Predict probabilities of ``context.target`` labels based on ``context.data``

    """
    def calc_concept_prediction_metrics(self, c_i, Y):
        """Calculate the target prediction for concept ``c_i`` based on ground truth targets ``Y``"""
        extent_i = self._lattice[c_i].extent_i

        classes = sorted(set(Y))
        self._class_names = classes

        def calc_class_probability(class_, extent_i, Y):
            return sum([Y[g_i] == class_ for g_i in extent_i])/len(extent_i) if len(extent_i) > 0 else None

        if len(extent_i) > 0:
            class_probs = [calc_class_probability(class_, extent_i, Y) for class_ in classes]
            max_prob = max(class_probs)
            max_class = [class_ for class_, class_prob in zip(classes, class_probs) if class_prob==max_prob]
            if len(max_class) == 1:
                max_class = max_class[0]
        else:
            class_probs = None
            max_prob = None
            max_class = None
        metrics = {
            'class_probabilities': class_probs,
            'most_probable_class': max_class,
            'maximum_class_probability': max_prob
        }
        return metrics

    def average_concepts_predictions(self, concepts_i):
        """Average label predictions of elements with indexes ``concepts_i`` to get a final prediction"""
        if len(concepts_i) == 0:
            return None

        probs_per_class = self.average_concepts_class_probabilities(concepts_i)
        max_prob = max(probs_per_class)
        max_class = [class_ for class_, prob in zip(self._class_names, probs_per_class) if prob == max_prob ]
        if len(max_class) == 1:
            max_class = max_class[0]
        return max_class

    def _sum_difference_predictions_proba(self, generators_extents, n_objects):
        return super(DecisionLatticeClassifier, self).sum_difference_predictions_proba(generators_extents, n_objects)

    def _sum_difference_predictions(self, generators_extents, n_objects):
        predictions = super(DecisionLatticeClassifier, self).sum_difference_predictions(generators_extents, n_objects)
        return predictions >= 0.5

    def average_concepts_class_probabilities(self, concepts_i):
        """Average predictions of elements with indexes ``concepts_i`` to get a final probability prediction"""
        if len(concepts_i) == 0:
            return None

        predictions = [self._lattice[c_i].measures['class_probabilities'] for c_i in concepts_i]
        probs_per_class = [sum(row) / len(row) if len(row) > 0 else None for row in zip(*predictions)]  # transpose data
        return probs_per_class

    def predict_proba(self, context: MVContext):
        """Predict a target probability prediction for objects of context ``context``"""
        bottom_concepts, _ = self._lattice.trace_context(context, use_object_indices=True)
        predictions = [self.average_concepts_class_probabilities(bottom_concepts[g_i])
                       for g_i in range(context.n_objects)]
        return predictions

    @property
    def class_names(self):
        """Class names of the target values"""
        return self._class_names


class DecisionLatticeRegressor(DecisionLatticePredictor):
    """
    A class which combines DecisionTree ideas with Concept Lattice to solve Regression tasks

    Methods
    -------
    fit(context)  :noindex:
        Construct a concept lattice based on ``context``
        and calculate interestingness measures to predict the ``context.target`` values
        (Inherited from `DecisionLatticePredictor` class)
    predict(context)  :noindex:
        Predict context.target labels based on context.data
        (Inherited from `DecisionLatticePredictor` class)

    """
    def calc_concept_prediction_metrics(self, c_i, Y):
        """Calculate the target prediction for concept ```c_i`` based on ground truth targets ``Y``"""
        extent_i = self._lattice[c_i].extent_i
        metrics = {"mean_y": sum([Y[g_i] for g_i in extent_i])/len(extent_i) if len(extent_i) else None}
        return metrics

    def average_concepts_predictions(self, concepts_i):
        """Average label predictions of concepts with indexes ``concepts_i`` to get a final prediction"""
        if len(concepts_i) == 0:
            return None
        predictions = [self._lattice[c_i].measures['mean_y'] for c_i in concepts_i]
        avg_prediction = sum(predictions)/len(predictions) if len(predictions) > 0 else None
        return avg_prediction

    @classmethod
    def from_decision_tree(cls, dtree, context: MVContext, random_state=None):
        """Construct the DecisionLattice from the sklearn decision tree ``dt`` model fitted on ``context`` data"""
        def concept_from_descr_i(descr_i, context: MVContext, context_hash=None):
            ext_i = context.extension_i(descr_i)
            int_i = context.intention_i(ext_i)

            if context_hash is None:
                context_hash = context.hash_fixed()

            ext_ = [context.object_names[g_i] for g_i in ext_i]
            int_ = {context.attribute_names[m_i]: v for m_i, v in int_i.items()}
            c = PatternConcept(
                ext_i, ext_, int_i, int_,
                context.pattern_types, context.attribute_names, context_hash=context_hash
            )
            return c

        # parse all the data from the decision tree
        if isinstance(dtree, BaseDecisionTree):
            direct_premises, dtargets, direct_children, direct_parents, direct_subelements_dict, premises = \
                cls._parse_dtsklearn_to_direct_drules(dtree, context)
        elif isinstance(dtree, Booster):
            direct_premises, dtargets, direct_children, direct_parents, direct_subelements_dict, premises = \
                cls._parse_xgbooster_to_direct_drules(dtree, context)
        else:
            raise TypeError(f'Decision Tree of type {type(dtree)} is not supported')


        # Construct elements based on premises of decision tree
        hash_ = context.hash_fixed()
        concepts = [concept_from_descr_i(p, context, hash_) for p in premises]

        # Check if elements make a lattice. If not, add a bottom concept
        bottom_elements = POSet(concepts, children_dict=direct_subelements_dict).bottoms
        if len(bottom_elements) > 1:
            bottom_concept = concept_from_descr_i(context.intention_i([]), context)
            bottom_concept_i = len(concepts)
            concepts.append(bottom_concept)
            for old_bottom_i in bottom_elements:
                direct_subelements_dict[old_bottom_i] = set(direct_subelements_dict[old_bottom_i])
                direct_subelements_dict[old_bottom_i].add(bottom_concept_i)
            direct_subelements_dict[bottom_concept_i] = set()
        bottom_elements = POSet(concepts, children_dict=direct_subelements_dict, ).bottoms
        assert len(bottom_elements) == 1

        L = ConceptLattice(concepts, subconcepts_dict=direct_subelements_dict)
        L._generators_dict = {c_i: {parent: [dp]} if parent is not None else dp for c_i, (parent, dp) in
                              enumerate(zip(direct_parents, direct_premises))}

        DL = cls(use_generators=True, random_state=random_state, prediction_func=PredictFunctions.SUMDIFF)
        DL._lattice = L
        DL._decisions = {(parent_i, child_i, dpremise): dy
                         for child_i, (parent_i, dpremise, dy)
                         in enumerate(zip(direct_parents, direct_premises, dtargets))}
        return DL

    @classmethod
    def from_random_forest(cls, rf, context: MVContext):
        """Construct the DecisionLattice from the sklearn Random Forest ``rf`` model fitted on ``context`` data"""
        dl_rf = cls.from_decision_tree(rf.estimators_[0], context, random_state=rf.estimators_[0].random_state)
        for dtree in rf.estimators_[1:]:
            dl_rf += cls.from_decision_tree(dtree, context, random_state=dtree.random_state)
        dl_rf /= rf.n_estimators
        return dl_rf

    @classmethod
    def from_gradient_boosting(cls, gb, context: MVContext):
        """Construct the DecisionLattice from the sklearn gradient boosting ``gb`` model fitted on ``context`` data"""
        estimators = gb.estimators_.flatten()

        dl_gb = cls.from_decision_tree(estimators[0], context, random_state=estimators[0].random_state)
        for dtree in estimators[1:]:
            dl_gb += cls.from_decision_tree(dtree, context, random_state=dtree.random_state)
        dl_gb *= gb.learning_rate
        dl_gb._decisions[(None, dl_gb.lattice.top, frozendict({}))] += gb.init_.constant_[0, 0]
        return dl_gb

    @classmethod
    def from_xgboost(cls, xgb, context: MVContext):
        """Construct the DecisionLattice from the xgboost ``xgb`` model fitted on ``context`` data"""
        boosters = list(xgb.get_booster())
        bias = xgb.get_params()['base_score']

        dl_xgb = cls.from_decision_tree(boosters[0], context)
        for booster in boosters[1:]:
            dl_xgb += cls.from_decision_tree(booster, context)
        dl_xgb._decisions[(None, dl_xgb.lattice.top, frozendict({}))] += bias
        return dl_xgb
