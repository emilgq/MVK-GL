# Back End Documentation

## API Service

### Version 0 (27/2/2020)

The initial version of the API provides placeholder data in the same format we intend on having in later versions with actual data. The data is hardcoded into python dictionaries and any update is lost upon server restart.

### Version 1 (18/5/2020)
The second and current version of the API provides data stored in the Postgres Database and is integrated with the machine learning module. Please see the db/README.md for further database documentation. Any GET request fetches data from the database and any POST request alters it. Changes are permanent.

#### /api/v1/project

This endpoint is the interface for resource management on the web application.

##### Resquest types

GET - Returns references to all machine learning references models found in the ml_models relation together with their respective configurations.

POST - Provided the POST request body contents described below, the server will add a new machine learning reference in ml_models and begin model training in accordance to the settings. Please see the machine learning module documentation for further description of creating new models.

##### Argument details
For all POST requests, the following keys must be specified.
| Body content key | Description                               | Allowed values               |
| ---------------- | ----------------------------------------- | ---------------------------- |
| model-name       | Reference name of type string             | Any string                   |
| API-KEY          | Authorization parameter                   | MVK123                       |
| configurations | Model configurations object | Keys described in table below. |

The table below shows the keys required in the configurations object. All models must specify the train-split, validation-split, default and hyper-tune values of the configuration object. If both hyper-tune and default are False, additional parameters must be passed in the request body, specific for each model.

| Configurations key | Model type                                                                           | Description                                                        | Allowed values |
| ---------------- | ------------------------------------------------------------------------------------ | ------------------------------------------------------------------ | -------------- |
| model-type       | All | Machine Model Technique                   | XGBoost, RandomForest or SVR |
| hyper-tune       | All |Enable hyper-tuned machine learning model | True/False                   |
| default          | All |Train model with library default settings | True/False                   |
| train-split      | All | Determines the size of the training data                                             | Floating point value\*, more info below                                   |
| validation-split | All | Determines the size of the validation data                                           | Floating point value, sum of train-split and validation-split must be 1 |
| learning-rate    | XGBoost | Determines the step-size of each iteration of the model training                     | Floating point value between 0 and 1, inclusive                    |
| max-depth        | XGBoost |  Determines the longest path from root to leaf of the machine learning tree structure | Non-negative integer                       |
| n-estimators    | RandomForest | The number of trees in the forest.                     | Non-negative integer
| max-depth        | RandomForest |  The maximum depth of the tree.  | Non-negative integer                        |
| kernel    | SVR | Specifies the kernel type to be used in the algorithm. | linear, poly, rbf or sigmoid  |
| c       | SVR |  Margin size of decision function | Non-negative integer                         |


##### Sample POST request.

```
curl http://localhost:5000/api/v1/project -d '{"model-name": "XXXXX", "configurations": {"model-type": "XGBoost", "default": "False", "hyper-tune": "False", "learning-rate": 0.01, "max-depth":7, "train-split": 0.75, "validation-split": 0.25}, "API-KEY": "MVK123"}' -X POST -H "Content-Type: application/json"
```

#### /api/v1/project/<model_id>
This endpoint is the interface for specific resource details. The intention is to provide model configuration details and model results consisting of a energy consumption prediction in conjunction with a time series.

##### Request types

GET - Given a model_id, the return value is the corresponding energy consumption prediction made by the specified model, made on the current weather forecast. In addition, model configurations are also provided. Please read the machine learning module documentation for further description on making predictions.

DELETE - Deletes the specified model from the file system and in the database.

#### /api/v1/weather-forecast
This endpoint is the interface for weather forecasts. The intention is to provide an entry-point to the weather-forecast database and enable updates and retrievals.

##### Request types

GET - Returns a forecast data including timestamp, wind speed, temperature and cloud coverage found in the weather_forecast relation. This data is updated hourly, for further description please read the data retrieval documentation.

POST - Provided the POST request arguments below, the server will update the given timestamp with given weather metrics and return the updated element as a response.

##### Argument Details
| Argument    | Description                          | Allowed values                       |
| ----------- | ------------------------------------ | ------------------------------------ |
| timestamp   | Element to be updated                | Must be of format 'YYYY-MM-DD HH:00' |
| wind        | Wind speed in meters per second      | Decimal value                        |
| temperature | Temperature in Kelvin                | Decimal value                        |
| cloud-cover | Rate of cloud coverage in percentage | Decimal value                        |
| API-KEY     | Authorization parameter              | MVK123                               |

##### Sample POST request.

```
curl http://localhost:5000/api/v0/weather-forecast -d '{"timestamp":"2021-02-02 11:00", "wind": 0, "temperature": 0, "cloud-cover": 0, "API-KEY":"MVK123"}' -X POST -H "Content-Type: application/json"
```


#### /api/v1/weather-data
This endpoint is the interface for the training data. The intention is to provide an entry-point to the weather-data database and enable updates and retrievals.

##### Request types

GET - Returns the full training data set including energy consumption, timestamp, wind speed, temperature and cloud coverage found in the weather_forecast relation. This data is updated daily, for further description please read the data retrieval documentation.

POST - Provided the POST request arguments below, the server will add a new data point to the data set, provided the timestamp is valid and unique.

##### Argument Details
| Argument    | Description                          | Allowed values                       |
| ----------- | ------------------------------------ | ------------------------------------ |
| timestamp   | Element to be updated                | Must be of format 'YYYY-MM-DD HH:00' |
| wind        | Wind speed in meters per second      | Decimal value                        |
| temperature | Temperature in Kelvin                | Decimal value                        |
| cloud-cover | Rate of cloud coverage in percentage | Decimal value                        |
| consumption | MWh consumption rate | Decimal value      |
| API-KEY     | Authorization parameter              | MVK123                               |

##### Sample POST request.

```
curl http://localhost:5000/api/v1/weather-data -d '{"timestamp":"2019-02-02 11:00", "temperature":280, "cloud-cover":99, "wind":14, "consumption":300, "API-KEY":"MVK123"}' -X POST -H "Content-Type: application/json"

```

## Data retrieval
All data is for Stockholm region

### greenMegaFiller

This script is used for initial filling of weather-data database. Retrieves timestamp, wind, Temperature, cloud-cover from greenlytics endpoint DWD_ICON-EU and consumption from Svenska kraftnäts to weather-data  endpoint.
All data is sent to the weather-data endpoint.
Dates have to manually be changed to correct ones. Can't use dates older than 2019-03-05 09:00 UTC or newer than today's date.
Dates that need to be updates is start_date, end_date for GL and date_start and date-end for SVK.


### green
Sends data to weather-data endpoint with Loads, timestamp, wind, Temperature and cloud-cover. Script checks for latest date in database. Gets data from that date until yesterday.
Script should run as cronjob once a day. Cronjob should be done after 12 pm otherwise error with date will occur.

### forecast
Sends forecast for wind temperature and cloud-cover for the comming 24 hours. The forecast from NCEP_GFS is update once a day. Get the forecsat for the comming 93 hours from NCEP_CPS. The script calculate the difference in hour from when the forcast was made. Should run as cronjob every hour to get the correct forecast. Sends the forecast to weather-forecast endpoint.


## Machine learning module
The different models are XGBoost, Random Forest and Support vector regression. The benchmark is Linear regression.

The main methods are __createModel, predictModel and hyperTuneModel__

### createModel
`createModel(configurations, modelID)` train and evaluate a model with the stated configurations and saves the model locally using pickle with the modelID as the name. It returns the RMSE of the trained model.

### predictModel
`predictModel(modelID)` takes a model name as the argument, then it loads the model with the specific modelID and use the model to predict the weather-load on the upcomming 24 hours. It returns all the predicted values with its corresponding timestamps.

### hyperTuneModel
hyperTuneModel are used when the hypertune is set to true in configurations. This method is used to find a really good model by testing multiple sets of hyperparameters in order to find the best ones. This is done using randomGridSearchVC, which basically is a way to test random hyperparameters from a specific set in order to find the best configuration. It returns the best model of the ones tested.
