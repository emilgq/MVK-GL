import requests

endpoint_url = "http://35.228.239.24/api/v1/project"
response = requests.get(endpoint_url)
print(response.text)