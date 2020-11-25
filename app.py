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


def parse_product_data(data, keys):

    data_content = []

    for i in range(0, len(keys)):
        print(data[keys[i]])
        if data[keys[i]] != '':
            data_content.append(data[keys[i]])
        else:
            keys.remove(keys[i])
            continue

    #new_data = [tuple(keys), tuple(data_content)]
    return data_content

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
    keys = ['PID', 'PName', 'PPrice', 'PStock', 'PColor', 'PDescript', 'PRating']
    
    if req['form_id'] == '1':
        
        data = parse_product_data(req, keys)
        print(data)
        print(data[0])
        #sql = ("INSERT INTO D0018E.Product (" + (', '.join(map(str, data[0]))) + ") VALUES " + str(data[1]))
        keys = ", ".join(map(str, keys))
        sql = ("INSERT INTO D0018E.Product ({0}) VALUES {1}".format(keys, tuple(data))) 
        print(sql)
        res = execute(sql, False)
            
    elif req['form_id'] == '2':
        
        data = parse_product_data(req, keys)
        print(data)
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