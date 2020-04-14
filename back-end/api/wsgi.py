### This is the entry point for the application, run by gunicorn server.

from apiapp import app

if __name__ == "__main__":
    app.run()