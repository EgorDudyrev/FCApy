"""
The module that implements the experiment part of a paper "Summation of decision trees" by E.Dudyrev, S.O.Kuznetsov

Should be deleted or replaced soon
"""
from fcapy.poset import POSet, UpperSemiLattice, BinaryTree
from copy import deepcopy


def compare_set_function(a, b):
    return set(b) & set(a) == set(b)


def compare_premise_function(a, b):
    return compare_set_function(a.premise, b.premise)


class DecisionRule:
    def __init__(self, premise, target):
        self._premise = premise
        self._target = target

    @property
    def premise(self):
        return self._premise

    @property
    def target(self):
        return self._target

    def __repr__(self):
        return self.to_str(show_class_name=True)

    def to_str(self, show_class_name=True):
        class_name = self.__class__.__name__ if show_class_name else ''
        return f"{class_name}({self.premise},{self.target})"

    def __mul__(self, other: float):
        return DecisionRule(self.premise, self.target * other)

    def __rmul__(self, other: float):
        return self.__mul__(other)

    def __eq__(self, other):
        return self.premise == other.premise and self.target == other.target

    def __hash__(self):
        return hash((self._premise, self._target))


class DecisionPOSet(POSet):
    def __init__(self, decision_rules=None, premises=None, targets=None,
                 use_cache: bool = True, leq_premise_func=None, children_dict=None):
        #if premises is not None and targets is not None:
        #    decision_rules = [DecisionRule(p, t) for p, t in zip(premises, targets)]
        #elif decision_rules is None:
        if decision_rules is not None:
            premises = [drule.premise for drule in decision_rules]
            targets = [drule.target for drule in decision_rules]
        elif premises is None or targets is None:
            raise ValueError(
                'Either `decision_rules` or a pair of (`premises`, `targets`) should be passed to DecisionPOSet')

        if not isinstance(premises, POSet):
            premises = POSet(
                elements=premises, leq_func=leq_premise_func,
                use_cache=use_cache, children_dict=children_dict
            )

        assert len(set(premises)) == len(premises), 'All premises should be unique'

        self._premises = premises
        self._targets = targets

        self._elements_to_index_map = {p: p_i for p_i, p in enumerate(premises)}

        #if decision_rules is None:
        #    decision_rules = [DecisionRule(p, t) for p, t in zip(premises, targets)]
        #super(DecisionPOSet, self).__init__(
        #    elements=decision_rules, leq_func=compare_premise_function,
        #    use_cache=use_cache, children_dict=children_dict
        #)

    @property
    def premises(self):
        return self._premises

    @property
    def targets(self):
        return self._targets

    @property
    def elements(self):
        return self.decision_rules

    @property
    def decision_rules(self):
        return [DecisionRule(p, t) for p, t in zip(self.premises, self.targets)]

    def index(self, element):
        p_i = self.premises.index(element.premise)
        if self._targets[p_i] == element.target:
            return p_i
        else:
            return None

    def leq_elements(self, a_index: int, b_index: int):
        return self.premises.leq_elements(a_index, b_index)

    def __repr__(self):
        k = 5
        is_big = len(self) > k
        elements_list = ', '.join([drule.to_str(False) for drule in self[:k]]) + (',...' if is_big else '')
        return f"{self.__class__.__name__}({len(self)} decision rules): [{elements_list}]"

    def __and__(self, other):
        raise NotImplementedError

    def __or__(self, other):
        raise NotImplementedError

    def __xor__(self, other):
        raise NotImplementedError

    def __sub__(self, other):
        raise NotImplementedError

    def __len__(self):
        return len(self.premises)

    def __delitem__(self, key):
        raise NotImplementedError

    def add(self, element, fill_up_cache=True):
        raise NotImplementedError

    def __eq__(self, other):
        raise NotImplementedError

    def trace_element(self, element, direction: str):
        raise NotImplementedError

    def __add__(self, other):
        assert type(self) == type(other), 'Models to sum up should be of the same type'

        prems_a = self.premises
        prems_b = other.premises

        targets_a = self.targets
        targets_b = other.targets

        prems_sum = prems_a | prems_b

        targets_sum = []
        for p in prems_sum:
            t_a = targets_a[prems_a.index(p)] if p in prems_a else 0
            t_b = targets_b[prems_b.index(p)] if p in prems_b else 0
            targets_sum.append(t_a + t_b)

        dposet_sum = DecisionPOSet(premises=prems_sum, targets=targets_sum, use_cache=self._use_cache,
                                   children_dict=self.__dict__.get('_cache_children'))

        return dposet_sum

    def __mul__(self, other: float):
        dposet_mul = deepcopy(self)
        dposet_mul._targets = [t * other for t in dposet_mul._targets]
        return dposet_mul

    def differentiate(self):
        old_targets = self.targets

        diff_poset = deepcopy(self)
        for drule_i, drule in enumerate(diff_poset.decision_rules):
            dsup_rules_i = diff_poset.parents(drule_i)

            del diff_poset._elements_to_index_map[drule]
            drule._target -= sum([old_targets[dsup_i] for dsup_i in dsup_rules_i])
            diff_poset._elements_to_index_map[drule] = drule_i
        return diff_poset

    def integrate(self):
        old_targets = self.targets

        int_poset = deepcopy(self)
        for drule_i, drule in enumerate(int_poset.decision_rules):
            sup_rules_i = int_poset.ancestors(drule_i)

            del int_poset._elements_to_index_map[drule]
            drule._target += sum([old_targets[sup_i] for sup_i in sup_rules_i])
            int_poset._elements_to_index_map[drule] = drule_i
        return int_poset


class DecisionLattice(DecisionPOSet, UpperSemiLattice):
    pass


class DecisionTree(DecisionLattice, BinaryTree):
    pass