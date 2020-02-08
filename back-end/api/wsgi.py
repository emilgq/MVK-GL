### This is the entry point for the application, run by gunicorn server.

from myproject import app

if __name__ == "__main__":
    app.run()