"""
This module provides 'DecisionLatticeClassifier' and 'DecisionLatticeRegressor' classes
to use 'ConceptLattice' in a DecisionTree-like manner

"""

from fcapy.mvcontext.mvcontext import MVContext
from fcapy.lattice import ConceptLattice


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
            generators_algo='approximate', random_state=None
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

        self._lattice = ConceptLattice()
        self._use_generators = use_generators
        self._generators_algo = generators_algo
        self._algo_params = algo_params if algo_params is not None else dict()
        self._random_state = random_state if random_state is not None else 0
        self._algo_params['random_state'] = self._random_state

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
        bottom_concepts, _ = self._lattice.trace_context(
            context, use_object_indices=True, use_generators=self._use_generators, use_tqdm=use_tqdm)
        predictions = [self.average_concepts_predictions(bottom_concepts[g_i]) for g_i in range(context.n_objects)]
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
