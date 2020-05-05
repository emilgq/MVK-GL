import pandas as pd
import xgboost as xgb
import numpy as np
import datetime as dt
import pickle
from numpy import loadtxt
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split, GridSearchCV, KFold, cross_val_score, RandomizedSearchCV
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn import svm
import urllib, json
from urllib.request import urlopen

# Beta-version
# If we use randomsearch we will need to have more values.
# Not all of the hyperparametrs are used, maybe add more later. 
def hyperTuneModel(modelType, X_train, X_test, y_train, y_test):
    kFold = KFold(n_splits=3, shuffle=True, random_state=13)

    # Need to optimize to find the best intervall of parameters.
    if modelType == "RandomForest":
        model = RandomForestRegressor()
        # Set the different values
        n_estimators = [int(x) for x in np.linspace(start = 200, stop = 2000, num = 10)]
        max_features = ['auto', 'sqrt']
        max_depth = []
        max_depth.append(None)
        min_samples_split = [int(x) for x in np.linspace(10, 110, num = 11)]
        min_samples_leaf = [1, 2, 4]
        bootstrap = [True, False]
        random_grid = {
            'n_estimators': n_estimators,
            'max_features': max_features,
            'max_depth': max_depth,
            'min_samples_split': min_samples_split,
            'min_samples_leaf': min_samples_leaf,
            'bootstrap': bootstrap}
    if modelType == "XGBoost":
        #Maybe needs to change depending on random/grid search.
        model = xgb.XGBRegressor()
        learning_rate = [0.05,0.1,0.2,0.25,0.3]
        min_split_loss = [0.5,1]
        max_depth = [4,6,8,9,10]
        max_depth = [7,8,9]
        min_child_weight = [0.5,2,4,6,8]
        colsample_bytree = [0.3,0.4,0.6,0.7]

        random_grid = {
            'learning_rate': learning_rate,
            'min_split_loss': min_split_loss,
            'max_depth': max_depth,
            'min_child_weight': min_child_weight,
            'colsample_bytree': colsample_bytree
        }
    if modelType == "SVR":
        model = svm.SVR()
        kernel = ['poly','rbf','sigmoid']
        C = [0.5,1,1.5,2]
        epsilon = [0.1,0.3,0.5,0.7]
        tol = [1e-3, 1e-4, 0.5e-3]

        random_grid = {
            'kernel': kernel,
            'C': C,
            'epsilon': epsilon,
            'tol': tol
        }

    # Randomized search for best hyperparameters
    model_random = RandomizedSearchCV(estimator = model, param_distributions = random_grid, n_iter = 10, cv = kFold, verbose=2, random_state=42, n_jobs = -1)

    model_random.fit(X_train, y_train)
    print("RMSE with radnomsearch: " + str(evaluate_model(X_test,y_test, model_random.best_estimator_)))
    print(model_random.best_params_)

    return model_random.best_estimator_


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
    loaded_model = pickle.load(open('/home/emil_gunnbergquerat/MVK-GL/back-end/ml/trained_models/' + str(modelID), 'rb'))
    dataset = getData('forecast')

    # Convert col 1 (timestamps) to datetime then back to string in HH:MM format
    hours = dataset.iloc[:,0].apply(lambda x: dt.datetime.strptime(x, '%Y-%m-%dT%H:%M:%S').strftime('%H:%M')) 
    
    X = dataset.iloc[:,1:6]
    prediction = loaded_model.predict(X)

    # Zip hours with prediction
    return list(hours), list(map(str, list(prediction)))  

def createModel(configurations, modelID):
    
    dataset = getData('data')
    # Split data
    X = dataset.iloc[:,1:6]
    y = dataset.iloc[:,7]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=configurations['validation-split'], random_state=123)

    # Hyper-tuned model
    if configurations['hyper-tune'] == "True":
        trained_model = hyperTuneModel(configurations['model-type'], X_train,X_test, y_train, y_test)

    # Default model
    elif configurations['default'] == "True":
        if configurations['model-type'] == "XGBoost":
            default_model = xgb.XGBRegressor()
        if configurations['model-type'] == "LinearRegression":
            default_model = LinearRegression()
        if configurations['model-type'] == "RandomForest":
            default_model = RandomForestRegressor()
        if configurations['model-type'] == "SVR":
            default_model = svm.SVR()
        trained_model = fit_model(default_model, default_model, X_train, y_train)

    # Customized model
    else:
        if configurations['model-type'] == "XGBoost":
            model = xgb.XGBRegressor(learning_rate = configurations['learning-rate'], max_depth = configurations['max-depth'])
            default_model = xgb.XGBRegressor()
        if configurations['model-type'] == "LinearRegression":
            model = LinearRegression()
            default_model = LinearRegression()
        if configurations['model-type'] == "RandomForest":
            model = RandomForestRegressor(max_depth=configurations['max-depth'], n_estimators = configurations['n-estimators'])
            default_model = RandomForestRegressor()
        if configurations['model-type'] == "SVR":
            model = svm.SVR(kernel = configurations['kernel'], C = configurations['c'])
            default_model = svm.SVR()
        
        trained_model = fit_model(model, default_model, X_train, y_train)


    model_rmse = evaluate_model(X_test, y_test, trained_model)
    
    # Save model to local file
    try:
        pickle.dump(trained_model, open('/home/emil_gunnbergquerat/MVK-GL/back-end/ml/trained_models/' + str(modelID), 'wb'))
    except FileNotFoundError as error:
        raise FileNotFoundError(error)
        
    print(configurations['model-type'] + ' RMSE = %0.4f' % model_rmse)
    return model_rmse


    
