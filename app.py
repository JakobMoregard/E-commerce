"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""

from flask import Flask, request,render_template
import psycopg2
from sshtunnel import SSHTunnelForwarder
def query(q):
     with SSHTunnelForwarder(
          ("130.240.200.30", 22),
          ssh_username="bersim-8",
          ssh_private_key ='C:/users/Simon/id_rsa',
          remote_bind_address=("127.0.0.1", 3306)
     ) as server:
          conn = psycopg2.connect(database="D0018E", 
                                  user="bersim-8",
                                  host="localhost",
                                  port=server.local_bind_port, 
                                  password="Norrviken123")
          return "yup"
test = query('select * from test')
app = Flask(__name__)

@app.route("/")
def hello():
    return render_template("test.html")

@app.route("/Kenobi")
def kenobi():
    return render_template("bold_one.html")

if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)
