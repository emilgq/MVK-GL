from flask import Flask
from flask_restful import Resource, Api, reqparse, abort
import json, random

app = Flask(__name__)
api = Api(app)

# Arguments required to train a new model.
createModelParser = reqparse.RequestParser()
createModelParser.add_argument('modelID', type=str)
createModelParser.add_argument('model-type', type=str, help='Choose a model type from XGBoost, RandomForest or LinearRegression')
createModelParser.add_argument('learning-rate', type=float, help='Learning rate between 0 and 1')
createModelParser.add_argument('max-depth', type=int, help='Max Depth')
createModelParser.add_argument('train-split', type=int, help='Training Split')
createModelParser.add_argument('validation-split', type=int, help='Validation Split')
createModelParser.add_argument('API-KEY', type=str, help='Authentication')

# Sample post request
# curl http://localhost:5000/api/v0/project -d "modelID=RF004" -d "model-type=RandomForest" -d "learning-rate=0.5" -d "max-depth=10" -d "train-split=75" -d "validation-split=25" -d "API-KEY=MVK123" -X POST -v

APIKEY = "MVK123"

testModelID = "XGB001"
testModelType = "XGBoost"
testRMSE = 15000
testLoadPrediction = [-300000,-290000,-280000,-270000,-290000,-310000,-300000,-310000,-320000,-330000,-340000,-310000,-320000,-290000,-280000,-300000,-310000,-330000,-300000,-280000,-290000,-280000,-270000,-320000]
testLearningRate = 0.5
testMaxDepth = 10

MODEL_RESULT = {
    "modelID": "XGB001",
    "model-type": "XGBoost",
    "hyperparameters": {
        "learning-rate": 0.5,
        "max-depth": 10,
        "train_split": 80,
        "validation_split": 20
    },
    "rmse": 15000,
    "prediction": [
        -300000, -290000, -280000, -270000, -290000, -310000, -300000, -310000, -320000, -330000, -340000, -310000, -320000, -290000, -280000, -300000, -310000, -330000, -300000, -280000, -290000, -280000, -270000, -320000
    ]
}

# Sample
TRAINED_MODELS = {
  'XGB001': {"model-type": "XGBoost", "learning-rate": 0.6, "max-depth": 11, "train-split": 80, "validation-split": 20, "rmse": 15000},
  'RF001': {"model-type": "RandomForest", "learning-rate": 0.5, "max-depth": 8, "train-split": 75, "validation-split": 25, "rmse": 17500},
  'XGB002': {"model-type": "XGBoost", "learning-rate": 0.5, "max-depth": 8, "train-split": 70, "validation-split": 30, "rmse": 20000},
  'XGB003': {"model-type": "XGBoost", "learning-rate": 0.4, "max-depth": 5, "train-split": 80, "validation-split": 20, "rmse": 12500},
  'LRG001': {"model-type": "LinearRegression", "learning-rate": 0.5, "max-depth": 8, "train-split": 80, "validation-split": 20, "rmse": 10000},
}

class ModelResult(Resource):
  def get(self, model_id):
    # Given the model_id, fetch reference info from Database
    # Pass weather forecast through trained model (.score())
    if model_id not in TRAINED_MODELS:
      abort(404, message='model not found')

    response = TRAINED_MODELS[model_id]

    return response, 200

class Project(Resource):
  # List all trained models
  def get(self):
    return TRAINED_MODELS

  # Create new Machine Learning Model
  def post(self):
    args = createModelParser.parse_args(strict=True)
    if args['API-KEY'] != APIKEY:
      abort(404, message='unauthorized')
    if args['model-type'] not in ['XGBoost', 'RandomForest', 'LinearRegression']:
      abort(404,message='Model type \"{}\" is not provided in this application. Select \"XGBoost\", \"RandomForest\" or \"LinearRegression\"'.format(args['model-type']))
    if ((args['learning-rate'] <= 0) or (args['learning-rate'] >= 1)): 
      abort(404,message='Learning rate must be between 0 and 1')
    if args['max-depth'] > 15:
      abort(404,message='Max depth is capped at 15')
    if args['modelID'] in TRAINED_MODELS:
      abort(404,message='Model ID already taken')
    if (args['train-split']+args['validation-split'] != 100):
      abort(404,message='Split must total to 100')
    # Run machine learning module
    # Fetch reference from database
    TRAINED_MODELS[args['modelID']] = {
      "model-type": args['model-type'], 
      "learning-rate": args['learning-rate'], 
      "max-depth": args['max-depth'], 
      "train-split": args['train-split'],
      "validation-split": args['validation-split'],
      "rmse": random.randint(10000,30000)
      }
    return TRAINED_MODELS[args['modelID']]

api.add_resource(ModelResult, '/api/v0/model-result/<model_id>')
api.add_resource(Project, '/api/v0/project')

if __name__ == "__main__":
    app.run(debug=True)