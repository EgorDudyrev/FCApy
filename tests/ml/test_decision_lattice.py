import pytest
from fcapy.lattice.concept_lattice import ConceptLattice
from fcapy.ml import decision_lattice as dl
from fcapy.mvcontext.mvcontext import MVContext
from fcapy.mvcontext import pattern_structure as ps

import numpy as np
from sklearn.datasets import load_iris, load_boston
from sklearn.metrics import accuracy_score, mean_squared_error, mean_absolute_error
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from xgboost import XGBRegressor


def test_dlpredictor():
    dlp = dl.DecisionLatticePredictor(algo_params={'L_max': 100})
    assert dlp.algo_params['L_max'] == 100, "DecisionLatticePredictor.__init__ failed"
    assert dlp._algo == 'Sofia', "DecisionLatticePredictor.__init__ failed"
    assert dlp.lattice is None, "DecisionLatticePredictor.__init__ failed"
    assert dlp.use_generators is False, "DecisionLatticePredictor.__init__ failed"

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
    mvctx_full = MVContext(data=X, target=Y, pattern_types=pattern_types, attribute_names=feature_names)

    np.random.seed(42)
    train_idxs = np.random.choice(range(len(Y)), 100, replace=False)
    test_idxs = sorted(set(range(len(Y))) - set(train_idxs))
    mvctx_train, mvctx_test = mvctx_full[train_idxs], mvctx_full[test_idxs]
    y_train, y_test = Y[train_idxs], Y[test_idxs]

    dlc = dl.DecisionLatticeClassifier(algo='Sofia', algo_params={'L_max': 10}, use_generators=True,
                                       generators_algo='exact')
    dlc.fit(mvctx_train)

    assert dlc.class_names == sorted(set(Y)), "DecisionLatticeClassifier.class_names failed"

    preds_train = dlc.predict(mvctx_train)
    preds_test = dlc.predict(mvctx_test)
    acc_train, acc_test = accuracy_score(y_train, preds_train), accuracy_score(y_test, preds_test)
    assert acc_train > 0.44, f"DecisionLatticeClassifier failed. To low train quality {acc_train}"
    assert acc_train > 0.44, f"DecisionLatticeClassifier failed. To low test quality {acc_test}"

    probs_train = np.array(dlc.predict_proba(mvctx_train))
    assert np.array(probs_train).sum(1).mean(),\
        "DecisionLatticeClassifier.predict_proba failed. Probabilities does not sum to 1"
    assert np.mean(np.argmax(probs_train, 1) == preds_train) == 1,\
        "DecisionLatticeClassifier.predict_proba failed. Probability predictions does not match class predictions"


def test_dlregressor():
    boston_data = load_boston()
    X_boston = boston_data['data'][:10]
    y_boston = boston_data['target'][:10]
    features_boston = [str(f) for f in boston_data['feature_names']]

    np.random.seed(42)
    train_idxs = np.random.choice(range(len(X_boston)), size=int(len(X_boston) * 0.8), replace=False)
    test_idxs = sorted(set(range(len(X_boston))) - set(train_idxs))

    pattern_types = {f: ps.IntervalPS for f in features_boston}
    mvctx_full = MVContext(X_boston,  pattern_types, target=y_boston, attribute_names=features_boston)
    mvctx_train, mvctx_test = mvctx_full[train_idxs], mvctx_full[test_idxs]

    y_train, y_test = y_boston[train_idxs], y_boston[test_idxs]

    dlc = dl.DecisionLatticeRegressor(algo_params={'L_max': 10}, use_generators=False)
    dlc.fit(mvctx_train)

    preds_train = dlc.predict(mvctx_train)
    preds_test = dlc.predict(mvctx_test)
    preds_test = [p if p is not None else np.mean(y_train) for p in preds_test]
    mse_train, mse_test = mean_squared_error(y_train, preds_train), mean_squared_error(y_test, preds_test)
    assert mse_train < 1, f"DecisionLatticeRegressor failed. To low train quality {mse_train}"
    assert mse_test < 29, f"DecisionLatticeRegressor failed. To low test quality {mse_test}"


def test_dlr_from_dtrees():
    boston_data = load_boston()
    X_boston = boston_data['data'][:100]
    y_boston = boston_data['target'][:100]
    features_boston = [str(f) for f in boston_data['feature_names']]

    np.random.seed(42)
    train_idxs = np.random.choice(range(len(X_boston)), size=int(len(X_boston) * 0.8), replace=False)
    test_idxs = sorted(set(range(len(X_boston))) - set(train_idxs))

    pattern_types = {f: ps.IntervalPS for f in features_boston}
    mvctx_full = MVContext(X_boston, pattern_types, target=y_boston, attribute_names=features_boston)
    mvctx_train, mvctx_test = mvctx_full[train_idxs], mvctx_full[test_idxs]

    y_train, y_test = y_boston[train_idxs], y_boston[test_idxs]

    model_func_dict = {
        DecisionTreeRegressor: dl.DecisionLatticeRegressor.from_decision_tree,
        RandomForestRegressor: dl.DecisionLatticeRegressor.from_random_forest,
        GradientBoostingRegressor: dl.DecisionLatticeRegressor.from_gradient_boosting,
        XGBRegressor: dl.DecisionLatticeRegressor.from_xgboost
    }

    for model_type in [DecisionTreeRegressor, RandomForestRegressor, GradientBoostingRegressor, XGBRegressor]:
        model_params = dict(random_state=42, max_depth=6)
        if model_type != DecisionTreeRegressor:
            model_params['n_estimators'] = 10

        model = model_type(**model_params)
        model.fit(X_boston[train_idxs], y_boston[train_idxs])

        func = model_func_dict[model_type]
        dlr = func(model, mvctx_train)

        preds_true = model.predict(X_boston[test_idxs])
        preds_dlr = dlr.predict(mvctx_test)
        err = mean_absolute_error(preds_true, preds_dlr) / preds_true.mean() * 100

        assert err < 1, f"DecisionLattice.{func.__name__} error. The prediction difference is too big ({err:.2e}%)"
