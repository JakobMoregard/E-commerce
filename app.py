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
            else:
                cursor.execute(sql)
                result = conn.insert_id()
                conn.commit()
    finally:
        conn.close()
    return result


def parse_data(data):
    print("yep")
    data_fields = [] 
    data_content = []

    data_fields.append("PID")
    print(data_fields)
    data_content.append(data['Insert'])
    print(data_content)

    for i in range(1, len(data)-1):
        if data[i][1] != "":
            data_fields.append(data[i][0])
            data_content.append(data[i][1])
        else:
            continue

    print("hm")
    new_data = (data_fields, data_content)
    print(new_data)
    return new_data

app = Flask(__name__)

@app.route("/")
def hello():
    sql = "Select PName, PPrice from D0018E.Product"
    data = execute(sql)
    return render_template("test.html", data = data)

@app.route('/', methods=['POST'])
def my_form_post():

    req = request.form
    print(req)
    data = parse_data(req)
    print(data)
    if 'Insert' in req:

        data = parse_data(req)
        print(insert)
        sql = ("INSERT INTO D0018E.Product(PID, PName, PPrice, PStock, PColor, PDescript, PRating) VALUES ({})".format(insert))
        res = execute(sql, False)
    
    elif 'Update' in req:
        
        update = request.form['Update']
        update = tuple(update.split(", "))
        sql = ("UPDATE D0018E.Product SET PPrice = " + update[1] + " WHERE PID = " + update[0]) 
        res = execute(sql, False)
        
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
