import pandas as pd
import xgboost as xgb
import numpy as np
import pickle
from numpy import loadtxt
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn import svm
import urllib, json
from urllib.request import urlopen

# Fetch the data, just placeholder data for the moment.

# Just some testdata


# url = "http://35.228.239.24/api/v1/weather-data"

# json_url = urlopen(url)

# data = json.loads(json_url.read())


# dataset = pd.DataFrame(data)
# dataset = dataset.dropna()
# Seperate the target variable and the rest of the variables using .iloc to subset the data
# X = dataset.iloc[:,1:6]
# y = dataset.iloc[:,7]

# Just to test the format
#print(X)
#print(y)

configurations = {
    "learning-rate": 0.1,
    "max-depth": 6,
    "model-type": 'SVM',
    "train-split": 0.80,
    "validation-split": 0.20   
}


def getData():
    url = "http://35.228.239.24/api/v1/weather-data"
    json_url = urlopen(url)
    data = json.loads(json_url.read())
    dataset = pd.DataFrame(data)
    dataset = dataset.dropna()
    return dataset

print(configurations['model-type'])
# Convert the dataset into an optimized data structure called Dmatrix
# that XGBoost supports and gives it acclaimed performance and efficiency gains.
#data_dmatrix = xgb.DMatrix(data = X, label = y)


#def split_data(validation_split):
 #   X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=123)

# Fit the regressor to the training set and make predictions on the test set using the familiar .fit()
# and .predict() methods.
def fit_model(model, X_train, y_train):
    # Train model
    model.fit(X_train, y_train)
    return model


# Compute the rmse by invoking the mean_squared_error function from sklearn's metrics module.
def evaluate_model(X_test, y_true, model):
    y_pred = model.predict(X_test)
    return np.sqrt(mean_squared_error(y_true, y_pred))



def predictModel(forecast, modelID):
    loaded_model = pickle.load(open('trained_models/' + modelID, 'rb'))
    # May have to change this dependent on the format of the forecast
    dataset = pd.DataFrame(forecast)
    X = dataset.iloc[:,1:6]
    result = loaded_model.predict(X)
    #print(result)
    return result

def createModel(configurations, modelID):
    default_maxdepth = 6
    default_learning_rate = 0.3
    # Pretty ugly right now ¯\_(ツ)_/¯
    if configurations['max-depth'] != None:
         maxDepth =  configurations['max-depth']
    elif configurations['max-depth'] == None:
         if configurations['model-type'] == "XGBoost":
            maxDepth = default_maxdepth
         if configurations['model-type'] == "RandomForest":
            maxDepth = None
    if configurations['learning-rate'] != None:
        learningRate =  configurations['learning-rate']
    else:
         learningRate = default_learning_rate
    if configurations['model-type'] == "XGBoost":
        model = xgb.XGBRegressor(learning_rate = learningRate, max_depth = maxDepth)
    if configurations['model-type'] == "LinearRegression":
         model = LinearRegression()
    if configurations['model-type'] == "RandomForest":
         model = RandomForestRegressor(max_depth=maxDepth)
    if configurations['model-type'] == "SVM":
        model = svm.SVR()

    # Get and format the data
    dataset = getData()
    X = dataset.iloc[:,1:6]
    y = dataset.iloc[:,7]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=configurations['validation-split'], random_state=123)
    trained_model = fit_model(model, X_train, y_train)
    model_rmse = evaluate_model(X_test, y_test, trained_model)

    #print(maxDepth)
    #print(learningRate)
    
    pickle.dump(trained_model, open('trained_models/' + modelID, 'wb'))
    print(configurations['model-type'] + ' RMSE = %0.4f' % model_rmse)
    return model_rmse


# Only for testing
if __name__== '__main__':

    createModel(configurations, "2")
    #predictModel([["Sat, 02 Feb 2999 11:00:00 GMT", 5, 11, 2, 280.0, 99.0, 14.0, 10.0], ["Sat, 02 Feb 2999 12:00:00 GMT", 5, 12, 2, 280.0, 99.0, 14.0, 10.0]], "1")
    