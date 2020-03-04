from flask_restful import reqparse

def addDataParser():
  adparser = reqparse.RequestParser()
  adparser.add_argument('timestamp', type=str)
  adparser.add_argument('day', type=int)
  adparser.add_argument('hour', type=int)
  adparser.add_argument('month', type=int)
  adparser.add_argument('temperature', type=int)
  adparser.add_argument('cloud-cover', type=int)
  adparser.add_argument('wind', type=int)
  adparser.add_argument('consumption', type=str)
  adparser.add_argument('API-KEY', type=str)
  return adparser
