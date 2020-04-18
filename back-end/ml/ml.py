import pandas as pd
import xgboost as xgb
import numpy as np
import pickle
from numpy import loadtxt
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split, GridSearchCV, KFold, cross_val_score, RandomizedSearchCV
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn import svm
import urllib, json
from urllib.request import urlopen


configurations = {
    "learning-rate": 0.1,
    "max-depth": 12,
    "n-estimators": 100,
    "kernel": 'poly',
    "c": 10,
    "model-type": 'XGBoost',
    "train-split": 0.80,
    "validation-split": 0.20   
}


def testCrossVal():
    dataset = getData('data')
    X = dataset.iloc[:,1:6]
    y = dataset.iloc[:,7]
    model = RandomForestRegressor()
    X_train, X_test, y_train, y_test = train_test_split(X, y,)
    kFold = KFold(n_splits=3, shuffle=True, random_state=13)

    n_estimators = [int(x) for x in np.linspace(start = 200, stop = 2000, num = 10)]

    max_features = ['auto', 'sqrt']
    max_depth = [int(x) for x in np.linspace(10, 110, num = 11)]
    max_depth.append(None)
    min_samples_split = [2, 5, 10]
    min_samples_leaf = [1, 2, 4]
    bootstrap = [True, False]

    

    random_grid = {'n_estimators': n_estimators,
               'max_features': max_features,
               'max_depth': max_depth,
               'min_samples_split': min_samples_split,
               'min_samples_leaf': min_samples_leaf,
               'bootstrap': bootstrap}

    rf_random = RandomizedSearchCV(estimator = model, param_distributions = random_grid, n_iter = 50, cv = kFold, verbose=2, random_state=42, n_jobs = -1)

    hp = [{
        'n_estimators' : [75,125, 200, 400],
        'max_depth' : [80,90,100,110],
        'bootstrap': [True],
        'max_features': ['auto','sqrt'],
        'min_samples_leaf': [1,4],
        'min_samples_split': [2,10]
        }] 
    # grid = GridSearchCV(estimator=model, param_grid= hp, cv= kFold, scoring= 'r2' )
    # grid = grid.fit(X_train,y_train)
    # print(grid.best_score_)
    # print(grid.best_estimator_)
    # print(grid.best_params_)
    # print(grid.best_index_)
    # print(evaluate_model(X_test, y_test, grid.best_estimator_))
    # print(grid.cv_results_['mean_test_score'][grid.best_index_])

    rf_random.fit(X_train, y_train)
    print("RMSE with radnomsearch: " + str(evaluate_model(X_test,y_test, rf_random.best_estimator_)))

    model = RandomForestRegressor(n_estimators= 125, max_depth= 18)
    print("RMSE without ranbomsearch: " + str(evaluate_model(X_test, y_test, model.fit(X_train, y_train))))
    # results = cross_val_score(model, X,y, cv=kFold)
    # print("Accuracy: %.2f%% (%.2f%%)" % (results.mean()*100, results.std()*100))

    #model = xgb.XGBRegressor(grid.best_params_)
   

def getData(type):
    try:
        url = "http://35.228.239.24/api/v1/weather-"+type
        json_url = urlopen(url)
        data = json.loads(json_url.read())
        dataset = pd.DataFrame(data)
        dataset = dataset.dropna()
        return dataset
    except Exception as e:
        # Something else here.
        print(e)

def fit_model(model,default_model, X_train, y_train):
    try:
        return model.fit(X_train, y_train)
    except (ValueError, xgb.core.XGBoostError):
        return default_model.fit(X_train, y_train)
    
# Compute the rmse by invoking the mean_squared_error function from sklearn's metrics module.
def evaluate_model(X_test, y_true, model):
    y_pred = model.predict(X_test)
    return np.sqrt(mean_squared_error(y_true, y_pred))


def predictModel(modelID):
    loaded_model = pickle.load(open('/home/emil/KTH/year2/MVK/MVK-GL/back-end/ml/trained_models/' + str(modelID), 'rb'))
    dataset = getData('forecast')
    X = dataset.iloc[:,1:6]
    return list(loaded_model.predict(X))

def createModel(configurations, modelID):
    if configurations['model-type'] == "XGBoost":
        model = xgb.XGBRegressor(learning_rate = configurations['learning-rate'], max_depth = configurations['max-depth'])
        default_model = xgb.XGBRegressor()
    if configurations['model-type'] == "LinearRegression":
        model = LinearRegression()
    if configurations['model-type'] == "RandomForest":
        model = RandomForestRegressor(max_depth=configurations['max-depth'], n_estimators = configurations['n-estimators'])
        default_model = RandomForestRegressor()
    if configurations['model-type'] == "SVR":
        model = svm.SVR(kernel = configurations['kernel'], C = configurations['c'])
        default_model = svm.SVR()
   
    dataset = getData('data')
    # Split data
    X = dataset.iloc[:,1:6]
    y = dataset.iloc[:,7]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=configurations['validation-split'], random_state=123)
    
    # Train model
    trained_model = fit_model(model, default_model, X_train, y_train)
    model_rmse = evaluate_model(X_test, y_test, trained_model)
    
    # Save model to local file
    try:
        pickle.dump(trained_model, open('/home/emil/KTH/year2/MVK/MVK-GL/back-end/ml/trained_models/' + str(modelID), 'wb'))
    except FileNotFoundError as error:
        raise FileNotFoundError(error)
        
    print(configurations['model-type'] + ' RMSE = %0.4f' % model_rmse)
    return model_rmse


# Only for testing
if __name__== '__main__':
    testCrossVal()
    