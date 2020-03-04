import json, random, re
from flask import Flask
from flask_restful import Resource, Api, reqparse, abort
# To enable Cross Origin Requests (such as JS .fetch())
from flask_cors import CORS

# Import application-specific argument parsers
from reqparsers.createmodel import createmodelparser
from reqparsers.updateforecast import updateforecastparser
from reqparsers.adddata import addDataParser

# Data samples for v0
from samples import WEATHER_FORECAST, TRAINED_MODELS, WEATHER_DATA



app = Flask(__name__)

# Enable RESTful framework
api = Api(app)

# Enable JavaScript Fetch
cors = CORS(app, resources={r"/api/v0/*": {"origins": "*"}})

# Arguments parser for training new model.
createModelParser = createmodelparser()

# Arguments parser for updating weather forecast.
updateForecastParser = updateforecastparser()

# Arguments parser for adding data
addDataParser = addDataParser()

# Sample post request
# curl http://localhost:5000/api/v0/project -d "modelID=RF002" -d "model-type=RandomForest" -d "learning-rate=0.5" -d "max-depth=10" -d "train-split=75" -d "validation-split=25" -d "API-KEY=MVK123" -X POST -v
# curl http://localhost:5000/api/v0/weather-forecast -d "timestamp=00:00" -d "wind=0" -d "temperature=0" -d "cloud-cover=0" -d "API-KEY=MVK123" -X POST -v
# curl http://localhost:5000/api/v0/weather-data -d "timestamp=1999-02-02 11:11" -d "day=1" -d "hour=1" -d "month=2" -d "temperature=280" -d "cloud-cover=99" -d "wind=14" -d "consumption=10" -d "API-KEY=MVK123" -X POST -v

# Sample data
APIKEY = "MVK123"
testLoadPrediction = [-300000,-290000,-280000,-270000,-290000,-310000,-300000,-310000,-320000,-330000,-340000,-310000,-320000,-290000,-280000,-300000,-310000,-330000,-300000,-280000,-290000,-280000,-270000,-320000]
testTimes = ['00:00','01:00','02:00','03:00','04:00','05:00','06:00','07:00','08:00','09:00','10:00','11:00','12:00','13:00','14:00','15:00','16:00','17:00','18:00','19:00', '20:00', '21:00', '22:00', '23:00']

# API Resource for fetching model specific results
class ModelResult(Resource):
  def get(self, model_id):
    # Given the model_id, fetch reference info from Database
    # Pass weather forecast through trained model (.score())
    if model_id not in TRAINED_MODELS:
      abort(404, message='model not found')

    response = TRAINED_MODELS[model_id].copy()
    response['result'] = dict(zip(testTimes, testLoadPrediction))

    return response, 200

# API Resource for fetching information about trained models and creating new instances
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

# API Resource for fetching the weather forecast and updating it with new data
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

# API Resource for fetching the weather data and adding it to the database
class WeatherData(Resource):
  def get(self):
    return WEATHER_DATA

  def post(self):
    args = addDataParser.parse_args(strict=True)
    #if ()  #timestamp not right format
     # abort(404,message='Timestamp not right format')
    WEATHER_DATA[args['timestamp']] = {
      "day": args["day"],
      "hour": args["hour"],
      "month": args["month"],
      "temperature": args["temperature"],
      "cloud-cover": args["cloud-cover"],
      "wind": args["wind"],
      "consumption": args["consumption"]
    }
    return WEATHER_DATA[args['timestamp']]


api.add_resource(ModelResult, '/api/v0/project/<model_id>')
api.add_resource(Project, '/api/v0/project')
api.add_resource(WeatherForecast, '/api/v0/weather-forecast')
api.add_resource(WeatherData, '/api/v0/weather-data')

if __name__ == "__main__":
    app.run(debug=True)
