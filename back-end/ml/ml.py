import pandas as pd
import xgboost as xgb
import numpy as np
import pickle
from numpy import loadtxt
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor

# Fetch the data, just placeholder data for the moment.
# data_placeholder = 

#data = pd.DataFrame(data)
dataset = loadtxt('phTestData.csv', delimiter=",")

# Seperate the target variable and the rest of the variables using .iloc to subset the data
# X, y = dataset.iloc[:,:], dataset.iloc[:,:] 
X = dataset[:,0]
y = dataset[:,1]

# Because data is only one 1d array
X = np.array(X).reshape(-1,1)


# Convert the dataset into an optimized data structure called Dmatrix
# that XGBoost supports and gives it acclaimed performance and efficiency gains.
#data_dmatrix = xgb.DMatrix(data = X, label = y)

## The train set
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=123)


# Fit the regressor to the training set and make predictions on the test set using the familiar .fit()
# and .predict() methods.
def fit_model(model):
    # Train model
    model.fit(X_train, y_train)

    # Test model
    #model_preds = model.predict(X_test)
    #model_mae = mea(y_test, model_preds)
    return model


# Compute the rmse by invoking the mean_squared_error function from sklearn's metrics module.
def evaluate_model(y_true, y_pred, model):
    model_preds = model.predict(X_test)
    return np.sqrt(mean_squared_error(y_true, y_pred))

# Instantiate an XGBoost regressor object
xgB_reg = xgb.XGBRegressor(objective ='reg:linear', colsample_bytree = 0.3, learning_rate = 0.3,
                max_depth = 5, alpha = 10, n_estimators = 10)
#xgB_reg = xgb.XGBRegressor(learning_rate = 0.1, max_depth = 5)
xgB_reg_model = fit_model(xgB_reg)
xgB_reg_mae = evaluate_model(y_test, xgB_reg_model)


# Instantiate and fit linear regression 
linReg = LinearRegression()
linReg_model = fit_model(linReg)
linReg_mae = evaluate_model(y_test, linReg_model)

# Instantiate and fit Randomforest regressor.
randomForest = RandomForestRegressor(max_depth = 5)
randomForest_model = fit_model(randomForest)
randomForest_mae = evaluate_model(y_test, randomForest_model)

# Print LinReg MAE
print('LinReg MAE = %0.4f' % linReg_mae)

# Print XGBoost MAE
print('XGBoost MAE = %0.4f' % xgB_reg_mae)

# Print RandomForest MAE
print('RandomForest MAE = %0.4f' % randomForest_mae)

def predict_model(model, test_data):
    return model.predict(test_data)

def save_model(model)
