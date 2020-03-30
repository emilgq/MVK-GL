import random, re, datetime, time
from flask import Flask, json, abort, request, Response
import psycopg2

# Importing celery to be able to run tasks in the backround
from celery import Celery

# To enable Cross Origin Requests (such as JS .fetch())
from flask_cors import CORS

# Import database conf and parser
from config import config

app = Flask(__name__)

# Passing the application name and the connection URL for the message broker
# The URL tells Celery where the broker service is running
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379'
# Getting and storing result from Task
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
# Passing any additional configuration options for Celery from Flask
celery.conf.update(app.config)

# Enable JavaScript Fetch
cors = CORS(app, resources={r"/api/v1/*": {"origins": "*"}})

# Sample post request
# curl http://localhost:5000/api/v1/project -d '{"model-name": "XXXXX", "configurations": {"model-type": "RandomForest", "learning-rate": 0.5, "max-depth":10, "train-split": 75, "validation-split": 25}, "API-KEY": "MVK123"}' -X POST -v -H "Content-Type: application/json"
# curl http://localhost:5000/api/v1/weather-forecast -d '{"timestamp":"2021-02-02 11:00", "wind": 0, "temperature": 0, "cloud-cover": 0, "API-KEY":"MVK123"}' -X POST -v -H "Content-Type: application/json"
# curl http://localhost:5000/api/v1/weather-data -d '{"timestamp":"2999-02-02 11:00", "temperature":280, "cloud-cover":99, "wind":14, "consumption":10, "API-KEY":"MVK123"}' -X POST -v -H "Content-Type: application/json"

# Sample delete request, replace X with desired model_id to delete
# curl http://localhost:5000/api/v1/project/X -d '{"API-KEY":"MVK123"}' -X DELETE -v -H "Content-Type: application/json"

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
    except Exception as error:
      raise Exception(error)
    finally:
      conn.commit()
      cur.close()
      if query_result is None:
        return
      else:
        return query_result, query_columns

  except (Exception, psycopg2.DatabaseError) as error:
    print(error)
    if conn is not None:
      conn.close()
    raise Exception(error)

# Background task
@celery.task
def background_task(model_id, configurations):
  for i in range(10):
    time.sleep(1)
    print(i)
  print('finished')
  # rmse = createModel(configurations, model_id)
  rmse = 20
  updatequery = "update ml_models set status = 'True', rmse = (%s) where model_id = (%s)"
  updateParameters = (rmse, model_id,)
  runDBQuery(updatequery, updateParameters)
  return

# API Resource for fetching model specific results
@app.route('/api/v1/project/<model_id>', methods=['GET', 'DELETE'])
def modelresult(model_id):
  if request.method == 'GET':
    # Given the model_id, fetch reference info from Database
    query = "select * from ml_models where model_id = %s"
    try:
      result, cols = runDBQuery(query, (model_id,))
    except Exception as e:
      abort(Response('Error: {}'.format(e), 400))

    if len(result) == 0:
      abort(Response('Model not found', 404))

    # Pass weather forecast through trained model (.score())
    response = dict(zip(cols, result[0]))
    # Add result column
    response['result'] = dict(zip(testTimes, testLoadPrediction))
    return json.dumps(response), 200

  # Remove model
  if request.method == 'DELETE':
    args = request.get_json()
    try:
      if args['API-KEY'] != APIKEY:
        abort(Response('Unauthorized', 400))
      query = "delete from ml_models where model_id = %s"
      runDBQuery(query, (model_id,))
      # Add function which removes save model from filesystem if model is trained or abort training in case still training
      return Response(json.dumps({"message": "Succesfully deleted model with id: {}".format(model_id)}), 200)
    except Exception as e:
      abort(Response('Error: {}'.format(e), 400))



# API Resource for fetching information about trained models and creating new instances
@app.route('/api/v1/project', methods=['GET', 'POST'])
def project():
  if request.method == 'GET':
    query = "select * from ml_models"
    parameters = None
    result, columns = runDBQuery(query, parameters)
    response = {}

    # Convert list of list to dict of dict with columns as keys
    for i in range(0, len(result)):
      response[result[i][0]] = {}
      for j in range (1, len(result[i])):
        response[result[i][0]][columns[j]] = result[i][j]
    return json.dumps(response), 200

  if request.method == 'POST':
  # Create new Machine Learning Model
    args = request.get_json()
    if args['API-KEY'] != APIKEY:
      abort(Response('unauthorized',400))
    configurations = args['configurations']
    if configurations['model-type'] not in ['XGBoost', 'RandomForest', 'SVR', 'LinearRegression']:
      abort(Response('Model type \"{}\" is not provided in this application. Select \"XGBoost\", \"RandomForest\", \"SVR\", or \"LinearRegression\"'.format(configurations['model-type']),400))
    if (configurations['train-split']+configurations['validation-split'] != 100):
      abort(Response('Split must total to 100',400))

    # Run machine learning module

    # Fetch reference from database
    query = "insert into ml_models (model_name, configurations, owner) values (%s,%s,%s)"
    parameters = (args['model-name'], json.dumps(configurations), 1337,)
    # Embed in try/except
    try:
      runDBQuery(query, parameters)
      model_id, _ = runDBQuery("select model_id from ml_models order by time_creation desc limit 1", None)
      background_task(model_id[0], configurations)
      message = 'successful model creation'
      return message, 200
    except Exception as e:
      abort(Response('Invalid argument. Error: {}'.format(e), 400))

    # Kolla hur man returnerar model_id


# API Resource for fetching the weather forecast and updating it with new data
@app.route('/api/v1/weather-forecast', methods=['GET', 'POST'])
def weatherForecast():
  if request.method == 'GET':
    query = "select * from weather_forecast"
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
    return json.dumps(response), 200

  if request.method == 'POST':
    args = request.get_json()
    # Validate given arguments
    # Check timestamp format YYYY-MM-DD HH:00
    if not re.match(r"\d\d\d\d-(0?[1-9]|1[0-2])-(0?[1-9]|[12][0-9]|3[01]) (0[0-9]|1[0-9]|2[0-3]):00", args['timestamp']):
      abort('Timestamp not right format', 400)
    # Check decimal values
    try:
      temp = float(args['temperature'])
      wind = float(args['wind'])
      cc = float(args['cloud-cover'])
    except:
      abort(Response(json.dumps({"message": "Type Error of weather metrics or load"}), 400))

    ts = datetime.datetime.strptime(args['timestamp'], '%Y-%m-%d %H:%M')

    # Extract datetime specifics
    dow = datetime.datetime.weekday(ts)
    hod = ts.hour
    moy = ts.month

    # Attempt to delete current tuple with given hour of day
    query = "delete from weather_forecast where hour = (%s)"
    try:
      runDBQuery(query,(hod,))
    except:
      pass

    # Run insert query to weather_forecast
    query = "insert into weather_forecast (ts, day, hour, month, temperature, cloud_cover, wind) values (%s,%s,%s,%s,%s,%s,%s)"
    parameters = (ts, dow, hod, moy, temp, cc, wind,)
    try:
      runDBQuery(query, parameters)
      return Response(json.dumps({"message": "Data point successfully added", "Data point": parameters}), 200)
    except Exception as e:
      abort(Response('Error: {}'.format(e), 400))

# API Resource for fetching the weather data and adding it to the database
@app.route('/api/v1/weather-data', methods=['GET', 'POST'])
def weatherData():
  if request.method == 'GET':
    query = "select * from weather_data"
    parameters = None
    result, _ = runDBQuery(query, parameters)
    response = []
    # Create matrix of weather & load data
    for i in range(0, len(result)):
      response.append([])
      for j in range (0, len(result[i])):
          response[i].append(result[i][j])
    return Response(json.dumps(response), 200)

  if request.method == 'POST':
    args = request.get_json()
    # Validate given arguments
    # Check timestamp format YYYY-MM-DD HH:00
    if not re.match(r"\d\d\d\d-(0?[1-9]|1[0-2])-(0?[1-9]|[12][0-9]|3[01]) (0[0-9]|1[0-9]|2[0-3]):00", args['timestamp']):
      abort('Timestamp not right format', 400)
    # Check decimal values
    try:
      temp = float(args['temperature'])
      wind = float(args['wind'])
      cc = float(args['cloud-cover'])
      load = float(args['consumption'])
    except:
      abort(Response(json.dumps({"message": "Type Error of weather metrics or load"}), 400))

    # Convert string to datetime object
    ts = datetime.datetime.strptime(args['timestamp'], '%Y-%m-%d %H:%M')

    # Extract datetime specifics
    dow = datetime.datetime.weekday(ts)
    hod = ts.hour
    moy = ts.month
    query = "insert into weather_data (ts, day, hour, month, temperature, cloud_cover, wind, consumption) values (%s,%s,%s,%s,%s,%s,%s,%s)"
    parameters = (ts, dow, hod, moy, temp, cc, wind, load,)

    # Run insert query to weather_data
    try:
      runDBQuery(query, parameters)
      return Response(json.dumps({"message": "Data point successfully added", "Data point": parameters}), 200)
    except Exception as e:
      abort(Response('Error: {}'.format(e), 400))



if __name__ == "__main__":
    app.run(debug=True)
