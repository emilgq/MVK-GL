from flask import Flask, abort, request, Response, render_template, url_for, redirect, session, flash
from functools import wraps
import requests, json

app = Flask(__name__)

app.secret_key = 'MVK123'
# session['logged_in'] = False

# Authorized wrapper function
def is_logged_in(f):
  @wraps(f)
  def wrap(*args, **kwargs):
      try:
          if session['logged_in']:
              return f(*args, **kwargs)
          else:
              flash("Unauthorized. Please enter you credentials to access this feature.", "danger")
              return redirect(url_for("login"))
      except KeyError:
          # flash("hello")
          return redirect(url_for("login"))
  return wrap

# Sample code for rendering and serving html templates
# https://flask.palletsprojects.com/en/1.1.x/quickstart/#rendering-templates
@app.route('/login', methods=['GET', 'POST'])
def login():
  # if session['logged_in'] == False:
  #     return redirect(url_for("login"))
  if request.method == 'GET':
    return render_template('login.html')
  if request.method == 'POST':
    password = request.form['password']
    if password == app.secret_key:
      session['logged_in'] = True
      flash("Access authorized, welcome :)", "success")
      return redirect(url_for("project"))
    else:
      error = "Wrong Authorization key. Please contact the MVK-team"
      return render_template('login.html', error=error)

@app.route('/logout')
# @is_logged_in
def logout():
    if session['logged_in']:
      session['logged_in'] = False
      flash("You have been logged out.", "success")
      return redirect(url_for("login"))
    else:
      # session['logged_in'] = False
      error = "Quit messing around with the URL, use the buttons like normal people"
      return render_template('login.html', error=error)
      return redirect(url_for("login"))


@app.route('/project', methods =['POST'])
@is_logged_in
def project():
  return render_template('project.html')

@app.route('/project/<model_id>')
@is_logged_in
def display(model_id=None):
  return render_template('index.html', model_id=model_id)

@app.route('/project/train', methods=['GET', 'POST'])
# @is_logged_in
def train():
  if request.method == 'GET':
    return render_template('train.html')

  if request.method == 'POST':
    endpoint_url = "http://35.228.239.24/api/v1/project"
    headers = {"Content-Type" : "application/json"}

    default = False
    hyperTune = False
    custom = False

    modelsetting = request.form['modelsetting']
    if(modelsetting == 'Default'):
        default = True
        hyperTune = False
        custom = False
    if(modelsetting == 'Hypertune'):
        default = False
        hyperTune = True
        custom = False
    if(modelsetting == 'Custom'):
        default = False
        hyperTune = False
        custom = True
    # default = bool(request.form['default'])
    # hyperTune = bool(request.form['hypertune'])

    print("hello this is default status " + str(default))
    print("hello this is hyperTune status " + str(hyperTune))
    print("hello this is custom status " + str(custom))
    print("hello " + modelsetting)
    # Default model
    hardCodedTrainSplit = 0.8
    hardCodedValSplit = 0.2

    # print(str(custom))
    if(default and not hyperTune):
        params = {
        "model-name": request.form['modelname'],
        "configurations":{
        "model-type": request.form['modeltype'],
        "default": str(default), #ska vara true för o va default
        "hyper-tune": str(hyperTune), #ska vara false för o va default
        "train-split": hardCodedTrainSplit,
        "validation-split": hardCodedValSplit},
        "API-KEY": "MVK123"
        }
        print("the default and not Hypertune happened")
    # HyperTune model
    if(not default and hyperTune):
        params = {
        "model-name": request.form['modelname'],
        "configurations":{
        "model-type": request.form['modeltype'],
        "default": str(default), #ska vara false för hypertune
        "hyper-tune": str(hyperTune), #ska var true för hypertune
        "train-split": hardCodedTrainSplit,
        "validation-split": hardCodedValSplit},
        "API-KEY": "MVK123"
        }
        print("the hyperTune and not default happened ")


    # Custom models since not hypertune and not default:
    if (not default and not hyperTune):
        modeltype = request.form['modeltype']
        print("the model type is " + modeltype)
        print (modeltype)
        if modeltype == "XGBoost":
            params = {
            "model-name": request.form['modelname'],
            "configurations":{
            "model-type": request.form['modeltype'],
            "default": str(default),
            "hyper-tune": str(hyperTune),
            "learning-rate": float(request.form['learningrateXG'])/10, # divided by 10 för den gör inte divisionen "i tid" i fetchstadie.
            "max-depth": int(request.form['maxdepthXG']),
            "train-split": int(request.form['trainsplitXG'])/100,
            "validation-split": (100-int(request.form['trainsplitXG']))/100,},
            "API-KEY": "MVK123"
            }
            # print(params)
            print("The If case: XGBoost happened")

        # elif modeltype == "LinearRegression":
        #     params = {
        #     "model-name": request.form['modelname'],
        #     "configurations":{
        #     "model-type": request.form['modeltype'],
        #     "default": request.form['default'],
        #     "hyper-tune": request.form['hypertune'],
        #     "learning-rate": float(request.form['learningrateLR']),
        #     "train-split": int(request.form['trainsplitLR']),
        #     "validation-split": int(request.form['valsplitLR']),
        #     "max-depth": int(request.form['maxdepthLR'])},
        #     "API-KEY": "MVK123"
        #     }
        #     # print(params)
        #     print("The If case: Linear Regression happened")

        elif modeltype == "RandomForest":
            params = {
            "model-name": request.form['modelname'],
            "configurations":{
            "model-type": request.form['modeltype'],
            "default": str(default),
            "hyper-tune": str(hyperTune),
            "n-estimators": float(request.form['n-estimatorRF']),
            "max-depth": int(request.form['maxdepthRF']),
            "train-split": int(request.form['trainsplitRF'])/100,
            "validation-split": (100-int(request.form['trainsplitRF']))/100,},
            "API-KEY": "MVK123"
            }
            # print("watafak")
            print(params)
            print("The If case: Random Forest happened")

        elif modeltype == "SVR":
            params = {
            "model-name": request.form['modelname'],
            "configurations":{
            "model-type": request.form['modeltype'],
            "default": str(default),
            "hyper-tune": str(hyperTune),
            "kernel": request.form['SVR KERNEL'],
            "c": int(request.form['CSVR']),
            "train-split": int(request.form['trainsplitSVR'])/100,
            "validation-split": (100-int(request.form['trainsplitSVR']))/100,},
            "API-KEY": "MVK123"
            }
            print("The If case: SVR happened")

        else:
            print("The else case happened")
            flash("Error, something went wrong")
            return redirect(url_for("train"))
    print(params)
    print("Hello this should get a response")
    response = requests.post(endpoint_url, headers=headers, data=json.dumps(params))
    return response.text


if __name__ == "__main__":
    app.run(debug=True)
