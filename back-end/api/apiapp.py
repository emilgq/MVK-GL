from flask import Flask
from flask_restful import Resource, Api, reqparse, abort
import json, random, re

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

# Arguments required to update forecast
updateForecastParser = reqparse.RequestParser()
updateForecastParser.add_argument('timestamp', type=str)
updateForecastParser.add_argument('wind', type=int)
updateForecastParser.add_argument('temperature', type=int)
updateForecastParser.add_argument('cloud-cover', type=int)
updateForecastParser.add_argument('API-KEY', type=str)

# Sample post request
# curl http://localhost:5000/api/v0/project -d "modelID=RF002" -d "model-type=RandomForest" -d "learning-rate=0.5" -d "max-depth=10" -d "train-split=75" -d "validation-split=25" -d "API-KEY=MVK123" -X POST -v
# curl http://localhost:5000/api/v0/weather-forecast -d "timestamp=00:00" -d "wind=0" -d "temperature=0" -d "cloud-cover=0" -d "API-KEY=MVK123" -X POST -v 

APIKEY = "MVK123"

testModelID = "XGB001"
testModelType = "XGBoost"
testRMSE = 15000
testLoadPrediction = [-300000,-290000,-280000,-270000,-290000,-310000,-300000,-310000,-320000,-330000,-340000,-310000,-320000,-290000,-280000,-300000,-310000,-330000,-300000,-280000,-290000,-280000,-270000,-320000]
testTimes = ['00:00','01:00','02:00','03:00','04:00','05:00','06:00','07:00','08:00','09:00','10:00','11:00','12:00','13:00','14:00','15:00','16:00','17:00','18:00','19:00', '20:00', '21:00', '22:00', '23:00']
testLearningRate = 0.5
testMaxDepth = 10

# Placeholder data
TRAINED_MODELS = {
  'XGB001': {"model-type": "XGBoost", "learning-rate": 0.6, "max-depth": 11, "train-split": 80, "validation-split": 20, "rmse": 15000},
  'RF001': {"model-type": "RandomForest", "learning-rate": 0.5, "max-depth": 8, "train-split": 75, "validation-split": 25, "rmse": 17500},
  'XGB002': {"model-type": "XGBoost", "learning-rate": 0.5, "max-depth": 8, "train-split": 70, "validation-split": 30, "rmse": 20000},
  'XGB003': {"model-type": "XGBoost", "learning-rate": 0.4, "max-depth": 5, "train-split": 80, "validation-split": 20, "rmse": 12500},
  'LRG001': {"model-type": "LinearRegression", "learning-rate": 0.5, "max-depth": 8, "train-split": 80, "validation-split": 20, "rmse": 10000}
}

# Placeholder data
WEATHER_FORECAST = {
  '00:00' : {"wind": 5, "temperature": 289, "cloud-cover": 13},
  '01:00' : {"wind": 6, "temperature": 283, "cloud-cover": 24},
  '02:00' : {"wind": 7, "temperature": 295, "cloud-cover": 51},
  '03:00' : {"wind": 5, "temperature": 293, "cloud-cover": 18},
  '04:00' : {"wind": 6, "temperature": 279, "cloud-cover": 1},
  '05:00' : {"wind": 5, "temperature": 301, "cloud-cover": 87},
  '06:00' : {"wind": 4, "temperature": 299, "cloud-cover": 35},
  '07:00' : {"wind": 3, "temperature": 286, "cloud-cover": 53},
  '08:00' : {"wind": 2, "temperature": 276, "cloud-cover": 2},
  '09:00' : {"wind": 0, "temperature": 285, "cloud-cover": 4},
  '10:00' : {"wind": 0, "temperature": 273, "cloud-cover": 74},
  '11:00' : {"wind": 8, "temperature": 300, "cloud-cover": 14},
  '12:00' : {"wind": 7, "temperature": 294, "cloud-cover": 26},
  '13:00' : {"wind": 6, "temperature": 299, "cloud-cover": 53},
  '14:00' : {"wind": 4, "temperature": 284, "cloud-cover": 42},
  '15:00' : {"wind": 3, "temperature": 284, "cloud-cover": 12},
  '16:00' : {"wind": 2, "temperature": 293, "cloud-cover": 1},
  '17:00' : {"wind": 1, "temperature": 300, "cloud-cover": 9},
  '18:00' : {"wind": 1, "temperature": 302, "cloud-cover": 26},
  '19:00' : {"wind": 1, "temperature": 295, "cloud-cover": 85},
  '20:00' : {"wind": 0, "temperature": 279, "cloud-cover": 42},
  '21:00' : {"wind": 8, "temperature": 288, "cloud-cover": 35},
  '22:00' : {"wind": 3, "temperature": 286, "cloud-cover": 24},
  '23:00' : {"wind": 5, "temperature": 294, "cloud-cover": 1},
}
class ModelResult(Resource):
  def get(self, model_id):
    # Given the model_id, fetch reference info from Database
    # Pass weather forecast through trained model (.score())
    if model_id not in TRAINED_MODELS:
      abort(404, message='model not found')

    response = TRAINED_MODELS[model_id]
    respone['result'] = dict(zip(testTimes, testLoadPrediction))

    return response, 200

class Project(Resource):
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

    # sql = """
    # insert into ml_models (model_name, configurations, owner) 
    # values (
    #   %s, \{ model-type: %s\}
    # """, args['model_name'], args['model-type']

    return TRAINED_MODELS[args['modelID']]

class WeatherForecast(Resource):
  def get(self):
    return WEATHER_FORECAST

  def post(self):
    args = updateForecastParser.parse_args(strict=True)
    if not re.match(r"([0-1]?[0-9]|2[0-3]):00", args['timestamp']): 
      abort(404,message='Timestamp not right format')
    if args['API-KEY'] != APIKEY:
      abort(404, message='unauthorized')
    WEATHER_FORECAST[args['timestamp']] = {
      "wind": args["wind"], 
      "temperature": args["temperature"], 
      "cloud-cover": args["cloud-cover"]
    }
    return WEATHER_FORECAST[args['timestamp']]

api.add_resource(ModelResult, '/api/v0/project/<model_id>')
api.add_resource(Project, '/api/v0/project')
api.add_resource(WeatherForecast, '/api/v0/weather-forecast')

if __name__ == "__main__":
    app.run(debug=True)