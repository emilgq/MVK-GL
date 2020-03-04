from flask_restful import reqparse

def createmodelparser():
  cmparser = reqparse.RequestParser()
  cmparser.add_argument('model-name', type=str)
  cmparser.add_argument('model-type', type=str, help='Choose a model type from XGBoost, RandomForest or LinearRegression')
  cmparser.add_argument('learning-rate', type=float, help='Learning rate between 0 and 1')
  cmparser.add_argument('max-depth', type=int, help='Max Depth')
  cmparser.add_argument('train-split', type=int, help='Training Split')
  cmparser.add_argument('validation-split', type=int, help='Validation Split')
  cmparser.add_argument('API-KEY', type=str, help='Authentication')
  return cmparser
