"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""

from flask import Flask, request,render_template
import pymysql.cursors

def execute(sql, isSelect = True, t = None):
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
                cursor.execute(sql, t)
                result = conn.insert_id()
                conn.commit()
    finally:
        conn.close()
    return result

app = Flask(__name__)

@app.route("/")
def hello():
    sql = "Select PName, PPrice from D0018E.Product"
    data = execute(sql)
    print(data)
    return render_template("test.html", data = data)

@app.route('/', methods=['POST'])
def my_form_post():
    text = request.form['text']
    print(text)
    processed_text = text.upper()
    sql = ("INSERT INTO D0018E.Product (PID, PName, PPrice, PStock, PColor, PDescript, PRating) VALUES")
    insert = execute(sql, False, text)
    print(insert)
    sql = "Select PName, PPrice from D0018E.Product"
    data = execute(sql)
    return render_template("test.html", data = data)

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

@app.route("/admin")
def admin():
    sql = "SELECT AID, AFName, ALName, AMail FROM D0018E.Administrator;"
    adminTable = execute(sql)
    print(adminTable)
    return render_template("Admin.html", adminTable = adminTable)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
