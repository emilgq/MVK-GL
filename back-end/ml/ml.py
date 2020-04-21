import pandas as pd
import xgboost as xgb
import numpy as np
import datetime as dt
import pickle
from numpy import loadtxt
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn import svm
import urllib, json
from urllib.request import urlopen



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

    # Convert col 1 (timestamps) to datetime then back to string in HH:MM format
    hours = dataset.iloc[:,0].apply(lambda x: dt.datetime.strptime(x, '%Y-%m-%dT%H:%M:%S').strftime('%H:%M')) 
    
    X = dataset.iloc[:,1:6]
    prediction = loaded_model.predict(X)

    # Zip hours with prediction
    response = dict(zip(list(hours), list(prediction)))
    return response

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
    createModel(configurations, "2")
    