"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""

from flask import Flask, request,render_template
import pymysql.cursors

def execute(sql, isSelect = True):
    conn = pymysql.connect(host='127.0.0.1',
                           port=3306,
                           user='bersim-8',
                           password='SecretPassword',
                           db ='D0018E',
                           charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)
    result = None
    try:
        with conn.cursor() as cursor:
            if isSelect:
                cursor.execute(sql)
                result = cursor.fetchall()
                #print(f"result = {result}")
            else:
                cursor.execute(sql)
                result = conn.insert_id()
                conn.commit()
    finally:
        conn.close()
    return result

app = Flask(__name__)

@app.route("/")
def hello():
    return render_template("test.html")

@app.route("/Kenobi")
def kenobi():
    return render_template("bold_one.html")

@app.route("/data")
def data():
    sql = "Select * from D0018E.test"
    data = execute(sql)
    print(data)
    return render_template("table.html", data = data)

@app.route("/readTable")
def readTable():
    sql = "SELECT CID, CFName FROM D0018E.Customer WHERE CID = '11223344';"
    table = execute(sql)
    print(table)
    return render_template("readTable.html", table = table)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
