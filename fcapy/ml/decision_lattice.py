"""
This module provides 'DecisionLatticeClassifier' and 'DecisionLatticeRegressor' classes
to use 'ConceptLattice' in a DecisionTree-like manner

"""
from frozendict import frozendict
import numpy as np
from enum import Enum

from fcapy.mvcontext.mvcontext import MVContext
from fcapy.lattice.pattern_concept import PatternConcept
from fcapy.lattice import ConceptLattice
from fcapy.poset import POSet


class PredictFunctions(Enum):
    AVGMAX = 'avg.max'
    SUMDIFF = 'sum.diff'


class DecisionLatticePredictor:
    """
    An abstract class to inherit 'DecisionLatticeClassifier' and 'DecisionLatticeRegressor' from

    Methods
    -------
    fit(context):
        Construct a concept lattice based on ``context``
        and calculate interestingness measures to predict the ``context.target`` values
    predict(context)
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
        for c_i, c in enumerate(self._lattice.concepts):
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

    @classmethod
    def from_decision_tree(cls, dtree, context: MVContext):
        def concept_from_descr_i(descr_i, context: MVContext, context_hash=None):
            ext_i = context.extension_i(descr_i)
            int_i = context.intention_i(ext_i)

            if context_hash is None:
                context_hash = context.hash_fixed()

            ext_ = [context.object_names[g_i] for g_i in ext_i]
            int_ = {context.attribute_names[m_i]: v for m_i, v in int_i.items()}
            c = PatternConcept(ext_i, ext_, int_i, int_, context.pattern_types, context_hash=context_hash)
            return c

        # parse all the data from the decision tree
        direct_premises, dtargets, direct_children, direct_parents, direct_subelements_dict, premises = \
            cls._parse_dtsklearn_to_direct_drules(dtree, context)

        # Construct concepts based on premises of decision tree
        hash_ = context.hash_fixed()
        concepts = [concept_from_descr_i(p, context, hash_) for p in premises]

        # Check if concepts make a lattice. If not, add a bottom concept
        bottom_elements = POSet(concepts, direct_subelements_dict=direct_subelements_dict).bottom_elements
        if len(bottom_elements) > 1:
            bottom_concept = concept_from_descr_i(context.intention_i([]), context)
            bottom_concept_i = len(concepts)
            concepts.append(bottom_concept)
            for old_bottom_i in bottom_elements:
                direct_subelements_dict[old_bottom_i].add(bottom_concept_i)
            direct_subelements_dict[bottom_concept_i] = set()
        bottom_elements = POSet(concepts, direct_subelements_dict=direct_subelements_dict,).bottom_elements
        assert len(bottom_elements) == 1

        L = ConceptLattice(concepts, subconcepts_dict=direct_subelements_dict)
        L._generators_dict = {c_i: {parent: [dp]} if parent is not None else dp for c_i, (parent, dp) in
                              enumerate(zip(direct_parents, direct_premises))}

        DL = cls(use_generators=True, random_state=dtree.random_state, prediction_func=PredictFunctions.SUMDIFF)
        DL._lattice = L
        DL._decisions = {(parent_i, child_i, dpremise): dy
                         for child_i, (parent_i, dpremise, dy)
                         in enumerate(zip(direct_parents, direct_premises, dtargets))}
        return DL

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
    def _parse_dtsklearn_to_direct_drules(dt, context: MVContext, eps=1e-9):
        tree = dt.tree_

        targets = tree.value.flatten()
        parents_dict_left = {child_i: parent_i for parent_i, child_i in enumerate(tree.children_left) if child_i != -1}
        parents_dict_right = {child_i: parent_i for parent_i, child_i in enumerate(tree.children_right) if
                              child_i != -1}
        parents_dict = {**parents_dict_left, **parents_dict_right}

        direct_parents = [None] + [parents_dict[node_i] for node_i in range(1, len(targets))]
        direct_children = list(range(len(targets)))
        direct_premises = [frozendict({})]
        premises = [frozendict({})]

        for node_i in range(1, len(targets)):
            is_left_child = node_i in parents_dict_left
            parent_i = parents_dict[node_i]

            descr = (-np.inf, tree.threshold[parent_i]) if is_left_child else (tree.threshold[parent_i]+eps, np.inf)
            premise = {tree.feature[parent_i]: descr}
            direct_premises.append(frozendict(premise))

            for ps_i, parent_descr in premises[parent_i].items():
                premise[ps_i] = context.pattern_structures[ps_i].generators_to_description(
                    [parent_descr, descr]) if ps_i in premise else parent_descr
            premises.append(frozendict(premise))

        direct_subelements_dict = ConceptLattice._transpose_hierarchy(
            {child_i: {parent_i} for child_i, parent_i in parents_dict.items()})

        dtargets = np.concatenate([targets[:1], targets[1:] - targets[direct_parents[1:]]])

        return direct_premises, dtargets, direct_children, direct_parents, direct_subelements_dict, premises


class DecisionLatticeClassifier(DecisionLatticePredictor):
    """
    A class which combines DecisionTree ideas with Concept Lattice to solve Classification tasks

    Methods
    -------
    fit(context):
        Construct a concept lattice based on ``context``
        and calculate interestingness measures to predict the ``context.target`` values
        (Inherited from `DecisionLatticePredictor` class)
    predict(context)
        Predict ``context.target`` labels based on ``context.data``
        (Inherited from `DecisionLatticePredictor` class)
    predict_proba(context)
        Predict probabilities of ``context.target`` labels based on ``context.data``

    """
    def calc_concept_prediction_metrics(self, c_i, Y):
        """Calculate the target prediction for concept ``c_i`` based on ground truth targets ``Y``"""
        extent_i = self._lattice.concepts[c_i].extent_i

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
        """Average label predictions of concepts with indexes ``concepts_i`` to get a final prediction"""
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
        """Average predictions of concepts with indexes ``concepts_i`` to get a final probability prediction"""
        if len(concepts_i) == 0:
            return None

        predictions = [self._lattice.concepts[c_i].measures['class_probabilities'] for c_i in concepts_i]
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
    fit(context):
        Construct a concept lattice based on ``context``
        and calculate interestingness measures to predict the ``context.target`` values
        (Inherited from `DecisionLatticePredictor` class)
    predict(context)
        Predict context.target labels based on context.data
        (Inherited from `DecisionLatticePredictor` class)

    """
    def calc_concept_prediction_metrics(self, c_i, Y):
        """Calculate the target prediction for concept ```c_i`` based on ground truth targets ``Y``"""
        extent_i = self._lattice.concepts[c_i].extent_i
        metrics = {"mean_y": sum([Y[g_i] for g_i in extent_i])/len(extent_i) if len(extent_i) else None}
        return metrics

    def average_concepts_predictions(self, concepts_i):
        """Average label predictions of concepts with indexes ``concepts_i`` to get a final prediction"""
        if len(concepts_i) == 0:
            return None
        predictions = [self._lattice.concepts[c_i].measures['mean_y'] for c_i in concepts_i]
        avg_prediction = sum(predictions)/len(predictions) if len(predictions) > 0 else None
        return avg_prediction
