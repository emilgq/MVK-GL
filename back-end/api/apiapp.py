from flask import Flask
app = Flask(__name__)

@app.route("/json-placeholder")
def hello():
    return """{ "users": [ { "userId": 1, "firstName": "Krish", "lastName": "Lee", "phoneNumber": "123456", "emailAddress": "krish.lee@learningcontainer.com" }, { "userId": 2, "firstName": "racks", "lastName": "jacson", "phoneNumber": "123456", "emailAddress": "racks.jacson@learningcontainer.com" }, { "userId": 3, "firstName": "denial", "lastName": "roast", "phoneNumber": "33333333", "emailAddress": "denial.roast@learningcontainer.com" }, { "userId": 4, "firstName": "devid", "lastName": "neo", "phoneNumber": "222222222", "emailAddress": "devid.neo@learningcontainer.com" }, { "userId": 5, "firstName": "jone", "lastName": "mac", "phoneNumber": "111111111", "emailAddress": "jone.mac@learningcontainer.com" } ] }"""

@app.route("/second-test")
def hello():
    return "This change works too!"

if __name__ == "__main__":
    app.run(host='0.0.0.0')