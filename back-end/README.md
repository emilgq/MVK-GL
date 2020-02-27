# Back End Documentation

## Rest API

### Version 0

The initial version of the API provides placeholder data in the same format we intend on having in later versions with actual data. The data is hardcoded into python dictionaries and any update is lost upon server restart.

As of 27/2/2020, the API consists of the following endpoints:

#### /api/v0/project

This endpoint is the interface for resource management on the web application.

##### Resquest types

GET - Returns references to all placeholder machine learning models found in the dictionary TRAINED_MODELS together with their respective configurations.

POST - Provided the POST request arguments below, the server will add a new element to TRAINED_MODELS and return the new element as a response.

##### Argument details 
| Argument | Description | Allowed values |
| ---------------- | ------------------------------------------------------------------------------------ | ------------------------------------------------------------------ |
| modelID | Reference name of type string | Must be unique |
| model-type | Machine Model Technique | XGBoost, RandomForest or LinearRegression |
| learning-rate | Determines the step-size of each iteration of the model training | Floating point value between 0 and 1, inclusive |
| max-depth | Determines the longest path from root to leaf of the machine learning tree structure | Integer value bewteen 0 and 14, inclusive |
| train-split | Determines the size of the training data | Integer value\*, more info below |
| validation-split | Determines the size of the validation data | Integer value, sum of train-split and validation-split must be 100 |
| API-KEY | Authorization parameter | MVK123 |

##### Sample POST request. 

```
curl http://35.228.239.24/api/v0/project -d "modelID=RF002" -d "model-type=RandomForest" -d "learning-rate=0.5" -d "max-depth=10" -d "train-split=75" -d "validation-split=25" -d "API-KEY=MVK123" -X POST -v
```

#### /api/v0/project/<model_id>
This endpoint is the interface for specific resource details. The intention is to provide model configuration details and model results consisting of a energy consumption prediction in conjunction with a time series. 

##### Request types

GET - Given a model_id, the return value is the corresponding values linked to that key in TRAINED_MODELS as well as a fixed result for times 00:00 to 23:00. 

#### /api/v0/weather-forecast
This endpoint is the interface for weather forecasts. The intention is to provide an entry-point to the weather-forecast database and enable updates and retrievals. 

##### Request types

GET - Returns a fixed placeholder forecast including timestamp, wind speed, temperature and cloud coverage for times 00:00 to 23:00, found in the dictionary WEATHER_FORECAST. The forecast do not reflect any reliable weather forecast. It is manufactured by schwi. 

POST - Provided the POST request arguments below, the server will update the given timestamp with given weather metrics and return the updated element as a response.

##### Argument Details
| Argument | Description | Allowed values |
| ---------------- | ------------------------------------------------------------------------------------ | ------------------------------------------------------------------ |
| timestamp | Element to be updated | Must be of format 'XX:00' where XX ranges from 00-23 |
| wind | Wind speed in meters per second | Integer value |
| temperature | Temperature in Kelvin | Integer value |
| cloud-cover | Rate of cloud coverage in percentage | Integer value |
| API-KEY | Authorization parameter | MVK123 |

##### Sample POST request. 

```
curl http://35.228.239.24/api/v0/weather-forecast -d "timestamp=00:00" -d "wind=0" -d "temperature=0" -d "cloud-cover=0" -d "API-KEY=MVK123" -X POST -v 
```