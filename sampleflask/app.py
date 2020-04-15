from flask import Flask, abort, request, Response, render_template, url_for, redirect, session, flash
from functools import wraps
import requests, json

app = Flask(__name__)

app.secret_key = 'MVK123'

# Authorized wrapper function
def is_logged_in(f):
  @wraps(f)
  def wrap(*args, **kwargs):
    if session['logged_in']:
      return f(*args, **kwargs)
    else:
      flash("Please enter your credentials in order to access this feature.", "danger")
      return redirect(url_for("login"))
  return wrap

# Sample code for rendering and serving html templates
# https://flask.palletsprojects.com/en/1.1.x/quickstart/#rendering-templates
@app.route('/login', methods=['GET', 'POST'])
def login():
  if session['logged_in']:
    return redirect(url_for("project"))
  if request.method == 'GET':
    return render_template('login.html')
  if request.method == 'POST':
    password = request.form['password']
    if password == app.secret_key:
      session['logged_in'] = True
      flash("Access authorized, welcome :)", "success")
      return redirect(url_for("project"))
    else:
      error = "Unauthorized"
      return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    if session['logged_in']:
      session['logged_in'] = False
      flash("You have been logged out.", "success")
      return redirect(url_for("login"))
    else:
      session['logged_in'] = False
      error = "You can't log out if you have yet to log in, silly"
      return render_template('login.html', error=error)


@app.route('/project')
@is_logged_in
def project():
  return render_template('project.html')

@app.route('/project/<model_id>')
@is_logged_in
def display(model_id=None):
  return render_template('index.html', model_id=model_id)

@app.route('/project/train', methods=['GET', 'POST'])
@is_logged_in
def train():
  if request.method == 'GET':
    return render_template('train.html')

  if request.method == 'POST':
    endpoint_url = "http://35.228.239.24/api/v1/project"
    headers = {"Content-Type" : "application/json"}

    params = {
      "model-name": request.form['modelname'],
      "model-type": request.form['modeltype'],
      "learning-rate": float(request.form['learningrate']),
      "max-depth": int(request.form['maxdepth']),
      "train-split": int(request.form['trainsplit']),
      "validation-split": int(request.form['valsplit']),
      "API-KEY": "MVK123"
    }
    print(params)
    response = requests.post(endpoint_url, headers=headers, data=json.dumps(params))
    return response.text

if __name__ == "__main__":
    app.run(debug=True)
