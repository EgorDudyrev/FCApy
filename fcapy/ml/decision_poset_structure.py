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
    def __init__(self, decision_rules=None, premises=None, targets=None, use_cache: bool = True):
        if premises is not None and targets is not None:
            decision_rules = [DecisionRule(p, t) for p, t in zip(premises, targets)]
        elif decision_rules is None:
            raise ValueError(
                'Either `decision_rules` or a pair of (`premises`, `targets`) should be passed to DecisionPOSet')

        super(DecisionPOSet, self).__init__(elements=decision_rules, leq_func=compare_premise_function,
                                            use_cache=use_cache)

        assert len(set(self.premises)) == len(self.premises), 'All premises should be unique'

    @property
    def premises(self):
        premise_poset = POSet([drule.premise for drule in self._elements],
                              compare_set_function, use_cache=self._use_cache)
        if self._use_cache:
            for cache_name in ['leq', 'direct_subelements',
                               'direct_superelements', 'subelements', 'superelements']:
                cache_name = '_cache_' + cache_name
                premise_poset.__dict__[cache_name] = deepcopy(self.__dict__[cache_name])

        return premise_poset

    @property
    def targets(self):
        return [drule.target for drule in self._elements]

    @property
    def decision_rules(self):
        return self.elements

    def __repr__(self):
        k = 5
        is_big = len(self) > k
        elements_list = ', '.join([drule.tostr(False) for drule in self[:k]]) + (',...' if is_big else '')
        return f"{self.__class__.__name__}({len(self)} decision rules): [{elements_list}]"

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

        dposet_sum = DecisionPOSet(premises=prems_sum, targets=targets_sum, use_cache=self._use_cache)
        if self._use_cache:
            for cache_name in ['leq', 'direct_subelements',
                               'direct_superelements', 'subelements', 'superelements']:
                cache_name = '_cache_' + cache_name
                dposet_sum.__dict__[cache_name] = deepcopy(prems_sum.__dict__[cache_name])

        return dposet_sum

    def __mul__(self, other: float):
        dposet_mul = deepcopy(self)
        for drule_i, drule in enumerate(dposet_mul._elements):
            drule_new = drule * other

            dposet_mul._elements[drule_i] = drule_new
            del dposet_mul._elements_to_index_map[drule]
            dposet_mul._elements_to_index_map[drule_new] = drule_i

        return dposet_mul

    def differentiate(self):
        old_targets = self.targets

        diff_poset = deepcopy(self)
        for drule_i, drule in enumerate(diff_poset.decision_rules):
            dsup_rules_i = diff_poset.direct_super_elements(drule_i)

            del diff_poset._elements_to_index_map[drule]
            drule._target -= sum([old_targets[dsup_i] for dsup_i in dsup_rules_i])
            diff_poset._elements_to_index_map[drule] = drule_i
        return diff_poset

    def integrate(self):
        old_targets = self.targets

        int_poset = deepcopy(self)
        for drule_i, drule in enumerate(int_poset.decision_rules):
            sup_rules_i = int_poset.super_elements(drule_i)

            del int_poset._elements_to_index_map[drule]
            drule._target += sum([old_targets[sup_i] for sup_i in sup_rules_i])
            int_poset._elements_to_index_map[drule] = drule_i
        return int_poset


class DecisionLattice(DecisionPOSet, UpperSemiLattice):
    pass


class DecisionTree(DecisionLattice, BinaryTree):
    pass