from flask_restful import reqparse

def updateforecastparser():
  ufparser = reqparse.RequestParser()
  ufparser.add_argument('timestamp', type=str)
  ufparser.add_argument('wind', type=int)
  ufparser.add_argument('temperature', type=int)
  ufparser.add_argument('cloud-cover', type=int)
  ufparser.add_argument('API-KEY', type=str)
  return ufparser
