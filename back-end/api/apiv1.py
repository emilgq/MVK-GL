import random, re, datetime, time, sys, os, errno
from flask import Flask, json, abort, request, Response
import psycopg2

# Importing celery to be able to run tasks in the backround
from celery import Celery

# To enable Cross Origin Requests (such as JS .fetch())
from flask_cors import CORS

# Import database conf and parser
from config import config

# Import home made Machine Learning module
sys.path.append('../ml/')
from ml import createModel, predictModel

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
testLoadBenchmark = [-500,-100,-900,-270,-400,-310,-300,-310,-320,-330,-340,-310,-320,-290,-280,-300,-310,-330,-300,-280,-290,-280,-270,-320]

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

# Create model in background process
@celery.task(time_limit=600)
def create_new_model(model_id, configurations):
  try:  
    print('Creating new model with conf: ' + str(configurations))
    rmse = createModel(configurations, model_id)
    updatequery = "update ml_models set status = 'True', rmse = (%s) where model_id = (%s)"
    updateParameters = (rmse, model_id,)
    runDBQuery(updatequery, updateParameters)
  except Exception as error:
    updatequery = "update ml_models set status = 'True' where model_id = (%s)"
    runDBQuery(updatequery, (model_id,))
    print('Model training failed with error message: {}'.format(error))
  finally:
    return True

# Delete model as background process
def delete_model(model_id):
  # Wait for model to complete training before deletion
  # Evaluate if model is ready to be deleted
  query = "select status, rmse from ml_models where model_id = %s"

  try:
    (training_completed, rmse) = runDBQuery(query, (model_id,))[0][0]
  except Exception as error:
    raise Exception(error)

  # Query yields no result
  if training_completed is None: 
    print('Model ID not found')
    return 'Model ID not found'

  # If status is true, model has finished training.
  if (training_completed):
    # Succeeded training assigns value to rmse
    if rmse is not None:
      print('Model {} ready for deletion'.format(model_id))
      
      # Delete model from ml/trained_models
      if os.path.exists("../ml/trained_models/" + model_id):
        os.remove("../ml/trained_models/" + model_id)
        print('ML Object deleted')
        query = "delete from ml_models where model_id = %s"
        try: 
          runDBQuery(query, (model_id,))  
        except Exception as error:
          raise Exception(error)
        print('Model reference deleted from DB')
        # End while loop
        return 'ML Object deleted from file system and model reference deleted from DB'

      # model not found in file system  
      else:
        print('ML Object not found') 
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), os.path.abspath("../ml/trained_models/" + model_id)) 
    
    # rmse has no assigned value, implying error while training.
    # Remove only db reference without cleaning file system
    else:
      print('Model had error while training and failed. Deleting DB reference.')
      query = "delete from ml_models where model_id = %s"
      try: 
        runDBQuery(query, (model_id,))  
      except Exception as error:
        raise Exception(error)

      print('Model reference deleted from DB')
      return 'Model reference deleted from DB'

  # If model has not finished training, do nothing. 
  else:
    print('Model is still training and cannot yet be deleted')
    return 'Model is still training and cannot yet be deleted'


  
  # Add function which removes save model from filesystem if model is trained or abort training in case still training


# Model load prediction
def predict_model(model_id):
  print('Predicting load for model with id: ' + model_id)
  hours, load = predictModel(model_id)
  return hours, load

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

    # Compile response object with headers and tuple content
    response = dict(zip(cols, result[0]))
    # Add result column
    response['hours'], response['load'] = predict_model(model_id)
    return json.dumps(response), 200

  # Remove model
  if request.method == 'DELETE':
    print("received DEL req for model id: {}".format(model_id))
    args = request.get_json()
    try:
      if args['API-KEY'] != APIKEY:
        abort(Response('Unauthorized', 400))
      # Run celery process of deleting model
      delete_response = delete_model(model_id)
      return Response(json.dumps({"message": delete_response, "model_id": model_id}), 200)
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
    args = request.get_json()
    if args['API-KEY'] != APIKEY:
      abort(Response('unauthorized',400))
    configurations = args['configurations']
    if configurations['model-type'] not in ['XGBoost', 'RandomForest', 'SVR', 'LinearRegression']:
      abort(Response('Model type \"{}\" is not provided in this application. Select \"XGBoost\", \"RandomForest\", \"SVR\", or \"LinearRegression\"'.format(configurations['model-type']),400))
    
    # Validate learning rate and max depth for XGBoost models
    if (configurations['model-type'] == 'XGBoost'):
        if (configurations['learning-rate'] < 0 or configurations['learning-rate'] > 1):
            abort(Response('Lerning rate must be a number from 0 to 1',400))
        if (configurations['max-depth'] <= 0):
            abort(Response('Max depth must be a positive number larger than 0',400))
            
    # Validate n-estimators and max depth for RandomForest models        
    if (configurations['model-type'] == 'RandomForest'):
        if (configurations['n-estimators'] <= 0):
            abort(Response('n-estimator must be a positive number larger than 0',400))
        if (configurations['max-depth'] <= 0):
            abort(Response('Max depth must be a positive number larger than 0',400))
     
    # Validate kernel and c for SVR models
    if (configurations['model-type'] == 'SVR'):
        if configurations['kernel'] not in ['linear', 'poly', 'rbf', 'sigmoid']:
             abort(Response('Kernel type \"{}\" is not provided in this application. Select \"linear\", \"poly\", \"rbf\", or \"sigmoid\"'.format(configurations['kernel']),400))
        if (configurations['c'] <= 0):
            abort(Response('C must be a positive number larger than 0',400)) #Vet inte om denna parameter heter C!!
            
    if (configurations['train-split']+configurations['validation-split'] != 1):
      abort(Response('Split must total to 1',400))
    if configurations['hyper-tune'] not in ("True", "False") or configurations['default'] not in ("True", "False"):
      abort(Response('Default and Hyper-tune must be True or False'))
    if configurations['hyper-tune'] == "True" and configurations['default'] == "True":
      abort(Response('Default and Hyper-tune cannot both be True'))

    # Create reference in database
    query = "insert into ml_models (model_name, configurations, owner) values (%s,%s,%s)"
    parameters = (args['model-name'], json.dumps(configurations), 1337,)
    try:
      runDBQuery(query, parameters)
      # Get model_id of new model
      model_id, _ = runDBQuery("select model_id from ml_models order by time_creation desc limit 1", None)
      # Start training as background process
      create_new_model.delay(model_id[0][0], configurations)
      message = {"msg": 'Model training started', "model-id": model_id}
      return json.dumps(message), 200
    except Exception as e:
      abort(Response('Invalid argument. Error: {}'.format(e), 400))


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

# API resource for fetching the predicted load for the the upcoming 24h
@app.route('/api/v1/benchmark', methods=['GET'])
def benchmark():
  if request.method == 'GET':
    response = {}
    try: 
      response['hours'], response['load'] = predict_model('0')
      response['model-name'] = 'Benchmark'
      response['model-type'] = 'LinearRegression'
      return json.dumps(response), 200
    except Exception as e:
      abort(Response('Error: {}'.format(e), 400))

if __name__ == "__main__":
    app.run(debug=True)
