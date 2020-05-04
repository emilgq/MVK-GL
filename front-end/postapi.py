import requests, json

endpoint_url = "http://35.228.239.24/api/v1/project"
headers = {"Content-Type" : "application/json"}
params = {
"model-name": "WORKSHOPTEST",
"model-type": "XGBoost",
"learning-rate": 0.5,
"max-depth":10,
"train-split": 75, 
"validation-split": 25,
"API-KEY": "MVK123"
}
response = requests.post(endpoint_url, headers=headers, data=json.dumps(params))
print(response.text)

# curl http://localhost:5000/api/v1/project -d '{, "API-KEY": "MVK123"}' -X POST -v -H "Content-Type: application/json"
