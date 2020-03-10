import random, re
from flask import Flask, json
from flask_restful import Resource, Api, reqparse, abort
import psycopg2

# To enable Cross Origin Requests (such as JS .fetch())
from flask_cors import CORS

# Import application-specific argument parsers
from reqparsers.createmodel import createmodelparser
from reqparsers.updateforecast import updateforecastparser
from reqparsers.adddata import addDataParser

# Import database conf and parser
from config import config

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
# curl http://localhost:5000/api/v0/project -d "model-name=RF002" -d "model-type=RandomForest" -d "learning-rate=0.5" -d "max-depth=10" -d "train-split=75" -d "validation-split=25" -d "API-KEY=MVK123" -X POST -v
# curl http://localhost:5000/api/v0/weather-forecast -d "timestamp=00:00" -d "wind=0" -d "temperature=0" -d "cloud-cover=0" -d "API-KEY=MVK123" -X POST -v
# curl http://localhost:5000/api/v0/weather-data -d "timestamp=1999-02-02 11:11" -d "day=1" -d "hour=1" -d "month=2" -d "temperature=280" -d "cloud-cover=99" -d "wind=14" -d "consumption=10" -d "API-KEY=MVK123" -X POST -v

# Sample data
APIKEY = "MVK123"
testLoadPrediction = [-300000,-290000,-280000,-270000,-290000,-310000,-300000,-310000,-320000,-330000,-340000,-310000,-320000,-290000,-280000,-300000,-310000,-330000,-300000,-280000,-290000,-280000,-270000,-320000]
testTimes = ['00:00','01:00','02:00','03:00','04:00','05:00','06:00','07:00','08:00','09:00','10:00','11:00','12:00','13:00','14:00','15:00','16:00','17:00','18:00','19:00', '20:00', '21:00', '22:00', '23:00']

# Query must be a parametrized SQL Statement - (select * from ml_models where model_name = %s)
# Paramteres must be a tuple with number of element equal to number of parameters in query. (XGB001)
def runDBQuery(query, parameters):
  conn = None
  query_result = None
  try:
    params = config()
    conn = psycopg2.connect(**params)
    cur = conn.cursor()
    cur.execute(query,parameters)
    try:
      query_result = cur.fetchall()
      query_columns = [desc[0] for desc in cur.description]
    except:
      pass
    finally:
      conn.commit()
      cur.close()

  except (Exception, psycopg2.DatabaseError) as error:
    print(error)

  finally:
    if conn is not None:
      conn.close()
      if query_result is None: 
        return
      else: 
        return query_result, query_columns


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
    query = "select model_id, model_name, time_creation::varchar, configurations, owner, status, rmse from ml_models"
    parameters = None
    result, columns = runDBQuery(query, parameters)
    response = {}

    # Convert list of list to dict of dict with columns as keys
    for i in range(0, len(result)):
      response[result[i][0]] = {}
      for j in range (1, len(result[i])):
        response[result[i][0]][columns[j]] = result[i][j]

    return response, 200

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
    if (args['train-split']+args['validation-split'] != 100):
      abort(404,message='Split must total to 100')

    # Run machine learning module

    # Fetch reference from database
    query = "insert into ml_models (model_name, configurations, owner) values (%s,%s,%s)"
    configurations = {
      "model-type": args['model-type'],
      "learning-rate": args['learning-rate'],
      "max-depth": args['max-depth'],
      "train-split": args['train-split'],
      "validation-split": args['validation-split'] 
    }
    parameters = (args['model-name'], json.dumps(configurations), 1337,)
    # Embed in try/except
    runDBQuery(query, parameters)
    message = 'successful model creation'
    return message, 200

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
    query = "select ts, day, hour, month, temperature, cloud_cover, wind, consumption from weather_data"
    parameters = None
    result, _ = runDBQuery(query, parameters)
    response = []
    # Convert list of list to dict of dict with columns as keys
    for i in range(0, len(result)):
      response.append([])
      for j in range (0, len(result[i])):
        if j == 0:
          response[i].append(result[i][j].isoformat())
        else:
          response[i].append(result[i][j])

    return response, 200

  def post(self):
    args = addDataParser.parse_args(strict=True)
    #if ()  #timestamp not right format
     # abort(404,message='Timestamp not right format')
    # Check timestamp format
    # Extract timestamp dow, hod, moy
    # Run insert query to weahter_data
    WEATHER_DATA[args['timestamp']] = {
      "day": args["day"],
      "hour": args["hour"],
      "month": args["month"],
      "temperature": args["temperature"],
      "cloud-cover": args["cloud-cover"],
      "wind": args["wind"],
      "consumption": args["consumption"]
    }
    # queryParameter = 
    # runDBQuery("insert into....%s", (args["day"],))
    return WEATHER_DATA[args['timestamp']]


api.add_resource(ModelResult, '/api/v0/project/<model_id>')
api.add_resource(Project, '/api/v0/project')
api.add_resource(WeatherForecast, '/api/v0/weather-forecast')
api.add_resource(WeatherData, '/api/v0/weather-data')

if __name__ == "__main__":
    app.run(debug=True)

""" 
In order to integrate the app with the database we'll use the psycopg2 library. 

It provides a cursor class which serves as an interface to the database. 

We'll need a function which takes a parametrized SQL statement, e.g. "SELECT * FROM weather_forecast WHERE timestamp < %s"
together with the parameters for the desired query and executes the combined statement.

The following procedure should take place(see egq/lms-dbas/ui for reference):
1. Setup a connection element

Within a try except clause, 
2. Load configuration parameters of database
3. Connect and create psycopg2 cursor.
4. Construct and execute query
5. Fetch and store result
6. Commit any potential changes of the transaction
7. Close cursor

If exception
8. Throw database error

Finally
9. Close connection

The return value should either be the resulting table of the query or none, depending on 
the nature of the query (SELECT/INSERT/DELETE). The cursor returns a list of tuples.

The intended usage of the function is that an endpoint request should trigger a database query. 
The endpoint function has the query structure stored as a local variable. The query parameters are given either by 
request header, data or url-parameters (e.g. model_id). 
"""
