"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""

from flask import Flask, request,render_template
import pymysql.cursors
import random

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


def parse_product_data(data, keys):

    data_content = []
    used_keys = []

    for i in range(0, len(keys)):
        print(data[keys[i]])
        if data[keys[i]] != '':
            data_content.append(data[keys[i]])
        else:
            used_keys.append(keys[i])
            continue

    #new_data = [tuple(keys), tuple(data_content)]
    for j in range(0, len(used_keys)):    
        keys.remove(used_keys[j])
    print("parse ",  keys)
    return data_content


def parse_update_string(data, keys):

    parse_string = ""

    print(keys)

    for i in range(1, len(keys)):
        if i > 1:
            parse_string += ","
        print("key = " + keys[i] + " data = " + data[i])
        parse_string += keys[i] + " = '" + data[i] + "'"
        
    
    print(parse_string)
    return parse_string

app = Flask(__name__)

@app.route("/")
def hello():

    session = randint(0, 10000)
    res = make_response("Setting a cookie")
    res.set_cookie('SID', session)

    name = request.cookies.get('userID')
    print(name)

    sql = "SELECT PName, PPrice, PStock, PColor, PDescript FROM D0018E.Product;"
    data = execute(sql)
    return render_template("test.html", prodTable = data)


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
    sql = "SELECT CID, CFName FROM D0018E.Customer;"
    table = execute(sql)
    return render_template("readTable.html", table = table)

@app.route("/admin")
def admin():
    query = "SELECT AID, AFName, ALName, AMail FROM D0018E.Administrator;"
    adminTable = execute(query)

    query2 = "Select PID, PName, PStock, PRating from D0018E.Product"
    table = execute(query2)

    return render_template("admin.html", table = table, adminTable = adminTable)

   
@app.route("/admin", methods=['POST'])
def adminForm():

    req = request.form
    print(req)
    keys = ['PID', 'PName', 'PPrice', 'PStock', 'PColor', 'PDescript', 'PRating']

    if req['form_id'] == '1':
        
        form = parse_product_data(req, keys)
        print(form)
        print(form[0])
        keys = ", ".join(map(str, keys))
        query1 = ("INSERT INTO D0018E.Product ({0}) VALUES {1}".format(keys, tuple(form))) 
        res = execute(query1, False)

    elif req['form_id'] == '2':
        
        data = parse_product_data(req, keys)
        print(data)
        print(keys)
        parse_string = parse_update_string(data, keys)
        sql = ("UPDATE D0018E.Product SET {} WHERE PID = ".format(parse_string) + data[0]) 
        print(sql)
        res = execute(sql, False)
        
    elif req['form_id'] == '3':

        sql = "DELETE FROM D0018E.Product WHERE PID = '{}'".format(req['PID'])
        print(sql)
        res = execute(sql, False)

    query2 = "Select PID, PName, PStock, PRating from D0018E.Product"
    table = execute(query2)
    return render_template("admin.html", table = table)


@app.route("/products")
def product():
    query = "SELECT PName, PPrice, PStock, PColor, PDescript FROM D0018E.Product;"
    prodTable = execute(query)
    return render_template("products.html", prodTable = prodTable)

if __name__ == "__main__":
    app.run(host='0.0.0.0')