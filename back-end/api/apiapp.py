from flask import Flask
from flask_restful import Resource, Api, reqparse, abort
import json, random

app = Flask(__name__)
api = Api(app)

# Arguments required to train a new model.
createModelParser = reqparse.RequestParser()
createModelParser.add_argument('modelID', type=str)
createModelParser.add_argument('model-type', type=str, help='Choose a model type from XGBoost, CatBoost or LightGBM')
createModelParser.add_argument('learning-rate', type=float, help='Learning rate between 0 and 1')
createModelParser.add_argument('max-depth', type=int, help='Max Depth')

# Sample post request
# curl http://localhost:5000/v0/trained-models -d "modelID=CB002" -d "model-type=CatBoost" -d "learning-rate=0.5" -d "max-depth=10" -X POST -v


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
        "max-depth": 10
    },
    "rmse": 15000,
    "prediction": [
        -300000, -290000, -280000, -270000, -290000, -310000, -300000, -310000, -320000, -330000, -340000, -310000, -320000, -290000, -280000, -300000, -310000, -330000, -300000, -280000, -290000, -280000, -270000, -320000
    ]
}

# Sample
TRAINED_MODELS = {
  'XGB001': {"model-type": "XGBoost", "learning-rate": 0.6, "max-depth": 11, "rmse": 15000},
  'CB001': {"model-type": "CatBoost", "learning-rate": 0.5, "max-depth": 8, "rmse": 17500},
  'XGB002': {"model-type": "XGBoost", "learning-rate": 0.5, "max-depth": 8, "rmse": 20000},
  'XGB003': {"model-type": "XGBoost", "learning-rate": 0.4, "max-depth": 5, "rmse": 12500},
  'LGBM001': {"model-type": "LightGBM", "learning-rate": 0.5, "max-depth": 8, "rmse": 10000},
}

class ModelResult(Resource):
  def get(self, model_id):
    # Given the model_id, fetch reference info from Database
    # Pass weather forecast through trained model (.score())
    response = {
      "modelID": MODEL_RESULT["modelID"],
      "model-type": MODEL_RESULT["model-type"],
      "hyperparameters": MODEL_RESULT["hyperparameters"],
      "rmse": MODEL_RESULT["rmse"],
      "prediction": MODEL_RESULT["prediction"]
      }
    return response, 200

class TrainedModels(Resource):
  # List all trained models
  def get(self):
    return TRAINED_MODELS

  # Create new Machine Learning Model
  def post(self):
    args = createModelParser.parse_args(strict=True)
    if args['model-type'] not in ['XGBoost', 'CatBoost', 'LightGBM']:
      abort(404,message='Model type \"{}\" is not provided in this application. Select \"XGBoost\", \"CatBoost\" or \"LightGBM\"'.format(args['model-type']))
    if ((args['learning-rate'] <= 0) or (args['learning-rate'] >= 1)): 
      abort(404,message='Learning rate must be between 0 and 1')
    if args['max-depth'] > 15:
      abort(404,message='Max depth is capped at 15')
    if args['modelID'] in TRAINED_MODELS:
      abort(404,message='Model ID already taken')
    # Run machine learning module
    # Fetch reference from database
    TRAINED_MODELS[args['modelID']] = {
      "model-type": args['model-type'], 
      "learning-rate": args['learning-rate'], 
      "max-depth": args['max-depth'], 
      "rmse": random.randint(10000,30000)}
    return TRAINED_MODELS[args['modelID']]

api.add_resource(ModelResult, '/v0/model-result/<model_id>')
api.add_resource(TrainedModels, '/v0/trained-models')

if __name__ == "__main__":
    app.run(debug=True)