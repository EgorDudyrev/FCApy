import pytest
from fcapy.lattice.concept_lattice import ConceptLattice
from fcapy.ml import decision_lattice as dl
from fcapy.mvcontext.mvcontext import MVContext
from fcapy.mvcontext import pattern_structure as ps
import numpy as np
from sklearn.datasets import load_iris, load_boston
from sklearn.metrics import accuracy_score, mean_squared_error


def test_dlpredictor():
    dlp = dl.DecisionLatticePredictor(L_max=100)
    assert dlp._L_max == 100, "DecisionLatticePredictor.__init__ failed"
    assert dlp._algo == 'Sofia', "DecisionLatticePredictor.__init__ failed"
    assert dlp.lattice == ConceptLattice(), "DecisionLatticePredictor.__init__ failed"

    with pytest.raises(NotImplementedError):
        dlp.average_concepts_predictions(None)
    with pytest.raises(NotImplementedError):
        dlp.calc_concept_prediction_metrics(None, None)


def test_dlclassifier():
    iris_data = load_iris()
    iris_data.keys()

    X = iris_data['data']
    Y = iris_data['target']
    feature_names = iris_data['feature_names']

    pattern_types = {f: ps.IntervalPS for f in feature_names}
    mvctx_full = MVContext(data=X, pattern_types=pattern_types, attribute_names=feature_names)

    np.random.seed(42)
    train_idxs = np.random.choice(range(len(Y)), 100, replace=False)
    test_idxs = sorted(set(range(len(Y))) - set(train_idxs))
    mvctx_train, mvctx_test = mvctx_full[train_idxs], mvctx_full[test_idxs]
    y_train, y_test = Y[train_idxs], Y[test_idxs]

    dlc = dl.DecisionLatticeClassifier(L_max=100)
    dlc.fit(mvctx_train, y_train)

    assert dlc.class_names == sorted(set(Y)), "DecisionLatticeClassifier.class_names failed"

    preds_train = dlc.predict(mvctx_train)
    preds_test = dlc.predict(mvctx_test)
    acc_train, acc_test = accuracy_score(y_train, preds_train), accuracy_score(y_test, preds_test)
    assert acc_train > 0.65, f"DecisionLatticeClassifier failed. To low train quality {acc_train}"
    assert acc_train > 0.5, f"DecisionLatticeClassifier failed. To low test quality {acc_test}"

    probs_train = np.array(dlc.predict_proba(mvctx_train))
    assert np.array(probs_train).sum(1).mean(),\
        "DecisionLatticeClassifier.predict_proba failed. Probabilities does not sum to 1"
    assert np.mean(np.argmax(probs_train, 1) == preds_train) == 1,\
        "DecisionLatticeClassifier.predict_proba failed. Probability predictions does not match class predictions"


def test_dlregressor():
    boston_data = load_boston()
    X_boston = boston_data['data']
    y_boston = boston_data['target']
    features_boston = [str(f) for f in boston_data['feature_names']]

    np.random.seed(42)
    train_idxs = np.random.choice(range(len(X_boston)), size=int(len(X_boston) * 0.8), replace=False)
    test_idxs = sorted(set(range(len(X_boston))) - set(train_idxs))

    pattern_types = {f: ps.IntervalPS for f in features_boston}
    mvctx_full = MVContext(X_boston, pattern_types, attribute_names=features_boston)
    mvctx_train, mvctx_test = mvctx_full[train_idxs], mvctx_full[test_idxs]

    y_train, y_test = y_boston[train_idxs], y_boston[test_idxs]

    dlc = dl.DecisionLatticeRegressor(L_max=50)
    dlc.fit(mvctx_train, y_train)

    preds_train = dlc.predict(mvctx_train)
    preds_test = dlc.predict(mvctx_test)
    preds_test = [p if p is not None else np.mean(y_train) for p in preds_test]
    mse_train, mse_test = mean_squared_error(y_train, preds_train), mean_squared_error(y_test, preds_test)
    assert mse_train < 85, f"DecisionLatticeRegressor failed. To low train quality {mse_train}"
    assert mse_test < 70, f"DecisionLatticeRegressor failed. To low test quality {mse_test}"
