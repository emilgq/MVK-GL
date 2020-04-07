import pandas as pd
import xgboost as xgb
import numpy as np
import pickle
from numpy import loadtxt
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split, GridSearchCV, KFold, cross_val_score
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
    kFold = KFold(n_splits=5, shuffle=True, random_state=13)
    hp = [{'n_estimators' : [75,100,125], 'max_depth' : [2,4,6,8,10,12,14,16,18,20]}] 
    grid = GridSearchCV(estimator=model, param_grid= hp, cv= kFold, scoring= 'r2' )
    grid = grid.fit(X_train,y_train)
    print(grid.best_score_)
    print(grid.best_estimator_)
    print(grid.best_params_)
    print(grid.best_index_)
    print(evaluate_model(X_test, y_test, grid.best_estimator_))
    print(grid.cv_results_['mean_test_score'][grid.best_index_])
    model = RandomForestRegressor(n_estimators= 125, max_depth= 18)
    results = cross_val_score(model, X,y, cv=kFold)
    print("Accuracy: %.2f%% (%.2f%%)" % (results.mean()*100, results.std()*100))

    #model = xgb.XGBRegressor(grid.best_params_)

    

def getData(type):
    try:
        url = "http://35.228.239.24/api/v1/weather-"+type
        json_url = urlopen(url)
        data = json.loads(json_url.read())
        dataset = pd.DataFrame(data)
        dataset = dataset.dropna()
        return dataset
    except:
        # Something else here.
        print("Some URL error")

print(configurations['model-type'])

def fit_model(model,default_model, X_train, y_train):
    try:
        return model.fit(X_train, y_train)
    except (ValueError, XGBoost.core.XGBoostError):
        return default_model.fit(X_train, y_train)
    
# Compute the rmse by invoking the mean_squared_error function from sklearn's metrics module.
def evaluate_model(X_test, y_true, model):
    y_pred = model.predict(X_test)
    return np.sqrt(mean_squared_error(y_true, y_pred))


def predictModel(forecast, modelID):
    loaded_model = pickle.load(open('trained_models/' + modelID, 'rb'))
    dataset = getData('forecast')
    X = dataset.iloc[:,1:6]
    return loaded_model.predict(X)

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
        pickle.dump(trained_model, open('trained_models/' + modelID, 'wb'))
    except FileNotFoundError as error:
        raise FileNotFoundError(error)
        
    print(configurations['model-type'] + ' RMSE = %0.4f' % model_rmse)
    return model_rmse


# Only for testing
if __name__== '__main__':
    testCrossVal()
    #createModel(configurations, 'testCrossVal')
    