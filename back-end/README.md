# Back End Documentation

## Rest API

### Version 0 (27/2/2020)

The initial version of the API provides placeholder data in the same format we intend on having in later versions with actual data. The data is hardcoded into python dictionaries and any update is lost upon server restart. 

### Version 1 (10/3/2020)
The second version of the API provides data stored in the Postgres Database. Please see the db/README.md for further database documentation. Any GET request fetches data from the database and any POST request alters it. Changes are permanent. 

#### /api/v0/project

This endpoint is the interface for resource management on the web application.

##### Resquest types

GET - Returns references to all machine learning references models found in the ml_models relation together with their respective configurations.

POST - Provided the POST request arguments below, the server will add a new machine learning reference in ml_models and return the new element as a response.

##### Argument details 
| Argument | Description | Allowed values |
| ---------------- | ------------------------------------------------------------------------------------ | ------------------------------------------------------------------ |
| model-name | Reference name of type string | Any string |
| model-type | Machine Model Technique | XGBoost, RandomForest or LinearRegression |
| learning-rate | Determines the step-size of each iteration of the model training | Floating point value between 0 and 1, inclusive |
| max-depth | Determines the longest path from root to leaf of the machine learning tree structure | Integer value bewteen 0 and 14, inclusive |
| train-split | Determines the size of the training data | Integer value\*, more info below |
| validation-split | Determines the size of the validation data | Integer value, sum of train-split and validation-split must be 100 |
| API-KEY | Authorization parameter | MVK123 |

##### Sample POST request. 

```
curl http://localhost:5000/api/v0/project -d '{"model-name": "XXXXX", "model-type": "RandomForest", "learning-rate": 0.5, "max-depth":10, "train-split": 75, "validation-split": 25, "API-KEY": "MVK123"}' -X POST -v -H "Content-Type: application/json"
```

#### /api/v0/project/<model_id>
This endpoint is the interface for specific resource details. The intention is to provide model configuration details and model results consisting of a energy consumption prediction in conjunction with a time series. 

##### Request types

GET - Given a model_id, the return value is the corresponding values linked to that key in ml_models as well as a placeholder results for times 00:00 to 23:00. 

#### /api/v0/weather-forecast
This endpoint is the interface for weather forecasts. The intention is to provide an entry-point to the weather-forecast database and enable updates and retrievals. 

##### Request types

GET - Returns a forecast data including timestamp, wind speed, temperature and cloud coverage found in the weather_forecast relation. The forecast do not reflect any reliable weather forecast as of 10/3/2020. 

POST - Provided the POST request arguments below, the server will update the given timestamp with given weather metrics and return the updated element as a response.

##### Argument Details
| Argument | Description | Allowed values |
| ---------------- | ------------------------------------------------------------------------------------ | ------------------------------------------------------------------ |
| timestamp | Element to be updated | Must be of format 'YYYY-MM-DD HH:00'|
| wind | Wind speed in meters per second | Decimal value |
| temperature | Temperature in Kelvin | Decimal value |
| cloud-cover | Rate of cloud coverage in percentage | Decimal value |
| API-KEY | Authorization parameter | MVK123 |

##### Sample POST request. 

```
curl http://localhost:5000/api/v0/weather-forecast -d '{"timestamp":"2021-02-02 11:00", "wind": 0, "temperature": 0, "cloud-cover": 0, "API-KEY":"MVK123"}' -X POST -v -H "Content-Type: application/json"
```