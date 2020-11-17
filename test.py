from flask import Flask, request,render_template
import psycopg2
try: 
    conn = psycopg2.connect(database="D0018E", user="bersim-8",  
    password="Norrviken123", host="localhost")
    print("connected")
except:
    print ("I am unable to connect to the database")
mycursor = conn.cursor()
app = Flask(__name__)

@app.route("/")
def hello():
    return render_template("test.html")

@app.route("/Kenobi")
def kenobi():
    return render_template("bold_one.html")


if __name__ == "__main__":
    app.run(host='0.0.0.0')
