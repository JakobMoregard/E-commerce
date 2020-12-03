"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""

from flask import Flask, request,render_template, make_response, redirect
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

def parse_registered_data(ID, data, keys):

    data_content = []
    used_keys = []

    data_content.append(ID)
    print(ID)

    for i in range(1, len(keys)):
        print(data[keys[i]])
        if data[keys[i]] != '':
            data_content.append(data[keys[i]])
        else:
            used_keys.append(keys[i])
            continue
    
    for j in range(0, len(used_keys)):    
        keys.remove(used_keys[j])
    print("parse ",  keys)
    return data_content



#def valid_id(admin_IDs, customer_IDs, registered_IDs):
def valid_id():
    id = random.randint(1, 99999999)

    sql = "SELECT AID FROM D0018E.Administrator"
    admin_IDs = execute(sql)
    sql2 = "SELECT CID FROM D0018E.Customer"
    customer_IDs = execute(sql2)
    sql3 = "SELECT RID FROM D0018E.Registered"
    registered_IDs = execute(sql3)

    if id not in admin_IDs or customer_IDs or registered_IDs:
        return id
    else:
        #return valid_id(admin_IDs, customer_IDs, registered_IDs)
        return valid_id()

def login_status():
    status = request.cookies.get('login')

    if status == None:
        return "Not currently logged in"
    elif status == 'admin':
        sql = "SELECT AFName FROM D0018E.Administrator WHERE AID = {}".format(request.cookies.get('SID'))
        res = execute(sql)
        return "{} is logged in as admin".format(res[0]['AFName'])
    elif status == 'registered':
        sql = "SELECT RFName FROM D0018E.Registered WHERE RID = {}".format(request.cookies.get('SID'))
        res = execute(sql)
        return "{} is logged in as admin".format(res[0]['RFName'])

app = Flask(__name__)

@app.route("/")
def hello():
    sql = "SELECT PName, PPrice, PStock, PColor, PDescript FROM D0018E.Product;"
    data = execute(sql)
    login = login_status()

    if not request.cookies.get('SID'):
        #sql = "SELECT AID FROM D0018E.Administrator"
        #admins = execute(sql)
        #sql2 = "SELECT CID FROM D0018E.Customer"
        #customers = execute(sql2)
        #sql3 = "SELECT RID FROM D0018E.Registered"
        #registered = execute(sql3)

        #session = valid_id(admins, customers, registered)
        session = valid_id()
        res = make_response(render_template("test.html", prodTable = data, login = login))
        res.set_cookie('SID', str(session), max_age=60*60*24*365*2)
    else:
        print("Could find cookie")
        name = request.cookies.get('SID')
        res = make_response(render_template("test.html", prodTable = data, login = login))
 
    return res


@app.route("/Kenobi")
def kenobi():
    return render_template("bold_one.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/login", methods=['POST'])
def loginForm():

    req = request.form
    admins_query = "SELECT AID, APassword FROM D0018E.Administrator;"
    admins = execute(admins_query)
    registered_query = "SELECT RID, RPassword FROM D0018E.Registered"
    registered = execute(registered_query)

    
    for i in range(len(admins)):

        if int(req['ID']) == admins[i]['AID'] and req['Password'] == admins[i]['APassword']:
            res = make_response(redirect("/admin"))
            res.set_cookie('login', 'admin', max_age=60*60*24*365*2)
            res.set_cookie('SID', str(admins[i]['AID']), max_age=60*60*24*365*2)
            return res
    for j in range(len(registered)):
        if int(req['ID']) == registered[j]['RID'] and req['Password'] == registered[j]['RPassword']:    
            res = make_response(redirect("/"))
            res.set_cookie('login', 'registered', max_age=60*60*24*365*2)
            res.set_cookie('SID', str(registered[j]['RID']), max_age=60*60*24*365*2)
            return res

    return render_template("login.html")


@app.route("/signup")
def signup():
    query = "SELECT * FROM D0018E.Registered;"
    registered = execute(query)
    return render_template("signup.html", registered = registered)


@app.route("/signup", methods=['POST'])
def signupForm():

    query1 = "SELECT * FROM D0018E.Registered;"
    registered = execute(query1)

    req = request.form
    new_ID = valid_id()
    keys = ['RID', 'RFName', 'RLName', 'RBAddress', 'RDAddress', 'RMail', 'RPassword']

    try:
        form = parse_registered_data(new_ID, req, keys)
        keys = ", ".join(map(str, keys))
        query = ("INSERT INTO D0018E.Registered ({0}) VALUES {1}".format(keys, tuple(form))) 
        execute(query, False)
    except pymysql.err.IntegrityError:
        errortext = "Mail is already registered"
        return render_template("signup.html", registered = registered, errortext = errortext)

    return render_template("signup.html", registered = registered)
   


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
        try:
            form = parse_product_data(req, keys)
            keys = ", ".join(map(str, keys))
            query1 = ("INSERT INTO D0018E.Product ({0}) VALUES {1}".format(keys, tuple(form))) 
            res = execute(query1, False)
        except pymysql.err.IntegrityError:
            print("something went wrong")

    elif req['form_id'] == '2':
        try:
            data = parse_product_data(req, keys)
            parse_string = parse_update_string(data, keys)
            sql = ("UPDATE D0018E.Product SET {} WHERE PID = ".format(parse_string) + data[0]) 
            res = execute(sql, False)
        except:
            print("something went wrong")

    elif req['form_id'] == '3':

        sql = "DELETE FROM D0018E.Product WHERE PID = '{}'".format(req['PID'])
        res = execute(sql, False)

    query3 = "SELECT AID, AFName, ALName, AMail FROM D0018E.Administrator;"
    adminTable = execute(query3)
    query2 = "Select PID, PName, PStock, PRating from D0018E.Product"
    table = execute(query2)
    return render_template("admin.html", table = table, adminTable = adminTable)



if __name__ == "__main__":
    app.run(host='0.0.0.0')