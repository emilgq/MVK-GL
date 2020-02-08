from flask import Flask
app = Flask(__name__)

@app.route("/placeholder/random-json")
def hello():
    return """{ "users": [ { "userId": 1, "firstName": "Krish", "lastName": "Lee", "phoneNumber": "123456", "emailAddress": "krish.lee@learningcontainer.com" }, { "userId": 2, "firstName": "racks", "lastName": "jacson", "phoneNumber": "123456", "emailAddress": "racks.jacson@learningcontainer.com" }, { "userId": 3, "firstName": "denial", "lastName": "roast", "phoneNumber": "33333333", "emailAddress": "denial.roast@learningcontainer.com" }, { "userId": 4, "firstName": "devid", "lastName": "neo", "phoneNumber": "222222222", "emailAddress": "devid.neo@learningcontainer.com" }, { "userId": 5, "firstName": "jone", "lastName": "mac", "phoneNumber": "111111111", "emailAddress": "jone.mac@learningcontainer.com" } ] }"""

@app.route("/placeholder/model-result")
def snd():
    return """{
  "modelID": "XGB001",
  "model-type": "XGBosst",
  "parameters": {
    "learning_rate": "0.5",
    "max_depth": "10"
  },
  "results": {
    "00:00": "1.2",
    "01:00": "1.4",
    "02:00": "1.5",
    "03:00": "1.7",
    "04:00": "2.0",
    "05:00": "2.3",
    "06:00": "2.3",
    "07:00": "2.4",
    "08:00": "2.9",
    "09:00": "3.0",
    "10:00": "3.5",
    "11:00": "3.5",
    "12:00": "3.8",
    "13:00": "3.9",
    "14:00": "4.0",
    "15:00": "4.0",
    "16:00": "4.2",
    "17:00": "4.4",
    "18:00": "4.6",
    "19:00": "4.7",
    "20:00": "4.9",
    "21:00": "5.0",
    "22:00": "5.1",
    "23:00": "5.5"
  }
}"""

if __name__ == "__main__":
    app.run(host='0.0.0.0')