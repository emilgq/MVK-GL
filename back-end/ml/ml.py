import pandas as pd
import xgboost as xgb
import numpy as np
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor

# Fetch the data, just placeholder data for the moment.
# data_placeholder = 

data = pd.DataFrame(data_placeholder.data)

# Seperate the target variable and the rest of the variables using .iloc to subset the data
#X, y = data.iloc[:,:], data.iloc[:,:] 


# Convert the dataset into an optimized data structure called Dmatrix
# that XGBoost supports and gives it acclaimed performance and efficiency gains.
data_dmatrix = xgb.DMatrix(data = X, label = y)

## The train set
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=123)


# Fit the regressor to the training set and make predictions on the test set using the familiar .fit()
# and .predict() methods.
def fit_and_evaluate(model):
    # Train model
    model.fit(X_train, y_train)

    # Test model
    model_preds = xg_reg.predict(X_test)
    model_mae = mea(y_test, model_preds)


# Compute the rmse by invoking the mean_squared_error function from sklearn's metrics module.
def mea(y_true, y_pred):
    return np.sqrt(mean_squared_error(y_true, y_pred))

# Instantiate an XGBoost regressor object
xgB_reg = xgb.XGBRegressor(learning_rate = 0.1, max_depth = 5)
xgB_reg_mae = fit_and_evaluate(xgB_reg)


# Print RMSE
print("xgboost MAE = %f" % (rmse))