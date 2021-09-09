"""
The legacy module that implements some ideas for E. Dudyrev master thesis (?)

Should be deleted or replaced soon
"""

from fcapy.ml.decision_poset_structure import DecisionPOSet, DecisionLattice, DecisionTree, DecisionRule
from fcapy.context import FormalContext
from fcapy.mvcontext import MVContext
from copy import deepcopy


def dposet_pred_avg_min(decision_poset, description):
    bottom_drules, _ = decision_poset.trace_element(DecisionRule(description, None), 'down')
    if len(bottom_drules) > 0:
        preds = [decision_poset.elements[drule_i].target for drule_i in bottom_drules]
        pred = sum(preds)/len(preds)
    else:
        pred = None
    return pred


def dposet_pred_sum(decision_poset, description):
    _, traced_drules = decision_poset.trace_element(DecisionRule(description, None), 'down')
    if len(traced_drules) > 0:
        preds = [decision_poset.elements[drule_i].target for drule_i in traced_drules]
        pred = sum(preds)
    else:
        pred = None
    return pred


class DecisionBasedModel:
    DECISION_POSET_TYPE = DecisionPOSet

    def __init__(self, decision_rules, predict_object_func, leq_premise_func):
        if not isinstance(decision_rules, self.DECISION_POSET_TYPE):
            decision_rules = self.DECISION_POSET_TYPE(
                list(decision_rules), use_cache=True, leq_premise_func=leq_premise_func)

        self._decision_rules = decision_rules
        self._predict_object_func = predict_object_func

    @property
    def decision_rules(self):
        return self._decision_rules

    @property
    def predict_object_func(self):
        return self._predict_object_func

    def predict_object(self, description):
        return self._predict_object_func(self._decision_rules, description)

    def fit(self, context, Y):
        raise NotImplementedError

    def predict(self, X: FormalContext or MVContext or list):
        if isinstance(X, (FormalContext, MVContext)):
            preds = [self.predict_object(list(x)) for x in X.data]
        else:
            preds = [self.predict_object(list(x)) for x in X]
        return preds

    def __mul__(self, other: float):
        model_mul = deepcopy(self)
        model_mul._decision_rules *= other
        return model_mul

    def __add__(self, other):
        assert type(self) == type(other), "Can only sum models if they are of the same type"

        model_sum = deepcopy(self)
        model_sum._decision_rules += other.decision_rules
        return model_sum


class DecisionPosetRegressor(DecisionBasedModel):
    def __init__(self, decision_rules, leq_premise_func):
        super(DecisionPosetRegressor, self).__init__(
            decision_rules, dposet_pred_avg_min, leq_premise_func=leq_premise_func)

    @classmethod
    def from_diff_decision_regressor(cls, diff_dposet_regressor):
        return cls(diff_dposet_regressor.decision_rules.integrate(),
                   diff_dposet_regressor.decision_rules.premises.leq_func)


class DiffDecisionPosetRegressor(DecisionBasedModel):
    def __init__(self, decision_rules, leq_premise_func):
        super(DiffDecisionPosetRegressor, self).__init__(
            decision_rules, dposet_pred_sum, leq_premise_func=leq_premise_func)

    @classmethod
    def from_decision_regressor(cls, dposet_regressor):
        return cls(dposet_regressor.decision_rules.differentiate(),
                   dposet_regressor.decision_rules.premises.leq_func)


class DecisionLatticeRegressor(DecisionPosetRegressor):
    DECISION_POSET_TYPE = DecisionLattice


class DiffDecisionLatticeRegressor(DiffDecisionPosetRegressor):
    DECISION_POSET_TYPE = DecisionLattice


class DecisionTreeRegressor(DecisionLatticeRegressor):
    DECISION_POSET_TYPE = DecisionTree


class DiffDecisionTreeRegressor(DiffDecisionLatticeRegressor):
    DECISION_POSET_TYPE = DecisionTree