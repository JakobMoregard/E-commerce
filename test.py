from flask import Flask, render_template
app = Flask(__name__)

@app.route("/")
def hello():
    return render_template("test.html")

@app.route("/Kenobi")
def kenobi():
    return "General Kenobi"

if __name__ == "__main__":
    app.run(host='0.0.0.0')
