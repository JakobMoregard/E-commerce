"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""

from flask import Flask, request,render_template, make_response, redirect, url_for
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

    if status == 'None' or status == None:
        return "Not currently logged in"
    elif status == 'admin':
        sql = "SELECT AFName FROM D0018E.Administrator WHERE AID = {}".format(request.cookies.get('SID'))
        res = execute(sql)
        return "{} is logged in as admin".format(res[0]['AFName'])
    elif status == 'registered':
        sql = "SELECT RFName FROM D0018E.Registered WHERE RID = {}".format(request.cookies.get('SID'))
        res = execute(sql)
        return "{} is logged in as registered".format(res[0]['RFName'])

app = Flask(__name__)


@app.route("/", methods=['POST'])
def cart_route():

    data = ""

    print(request.args)
    if request.args:
        data = request.args['data'] 

    sql1 = "SELECT CID from D0018E.Customer"
    customers = execute(sql1)

    sql2 = "SELECT CuID, ReID FROM D0018E.Cart"
    IDs = execute(sql2)

    cookie_id = int(request.cookies.get('SID'))
    print(customers)
    print(request.cookies.get('SID'))

    flag = True
    for i in range(len(customers)):
        if customers[i]['CID'] == cookie_id:
            flag = False

    amount = request.form['Amount']
    print(amount)
    if request.cookies.get('login') == 'None' and flag:
        res = make_response(redirect(url_for(".customer", data = amount)))
        return res



    
    res = make_response(redirect(url_for('.cart', data = amount)))
    for i in range(len(IDs)):
        if cookie_id == IDs[i]['CuID']:
            return res
        elif cookie_id == IDs[i]['ReID']:
            return res
    CaID = valid_id()
    
    if request.cookies.get('login') == 'registered':
        sql_insert = "INSERT INTO D0018E.Cart (CaID, ReID) VALUES ({0}, (SELECT RID FROM D0018E.Registered WHERE RID = {1}))".format(CaID, cookie_id)
        execute(sql_insert, False)
    elif request.cookies.get('login') == 'None':
        sql_insert = "INSERT INTO D0018E.Cart (CaID, CuID) VALUES ({0}, (SELECT CID FROM D0018E.Customer WHERE CID = {1}))".format(CaID, cookie_id)
        execute(sql_insert, False)
        res = make_response(redirect(url_for('.cart', data = data)))
    
    return res

@app.route("/")
def hello():
    
    app.add_url_rule('/', 'index', hello)
    sql = "SELECT PID, PName, PPrice, PStock, PColor, PDescript FROM D0018E.Product;"
    data = execute(sql)

    res = make_response(render_template("test.html", prodTable = data, login = login_status(), loginstatus = request.cookies.get('login')))

    if not request.cookies.get('SID'):
        #sql = "SELECT AID FROM D0018E.Administrator"
        #admins = execute(sql)
        #sql2 = "SELECT CID FROM D0018E.Customer"
        #customers = execute(sql2)
        #sql3 = "SELECT RID FROM D0018E.Registered"
        #registered = execute(sql3)

        #session = valid_id(admins, customers, registered)
        session = valid_id()
        res.set_cookie('SID', str(session), max_age=60*60*24*365*2)
        res.set_cookie('login', 'None', max_age=60*60*24*365*2)
    else:
        print("Could find cookie")
        name = request.cookies.get('SID')
 
    return res 


@app.route("/customer")
def customer():
    data = request.args['data']
    print("data ", data)
    return render_template("customer.html", data = data)

@app.route("/customer", methods=['POST'])
def customerForm():

    #query1 = "SELECT * FROM D0018E.Customer"
    #registered = execute(query1)

    req = request.form
    keys = ['CID', 'CFName', 'CLName', 'CBAddress', 'CDAddress']

    Amount = req['Amount']
    print("amount ", Amount)
    try:
        ID = request.cookies.get('SID')
        form = parse_registered_data(ID, req, keys)
        keys = ", ".join(map(str, keys))
        query = ("INSERT INTO D0018E.Customer ({0}) VALUES {1}".format(keys, tuple(form)))
        execute(query, False)
    except pymysql.err.IntegrityError:
        errortext = "Customer is already registered"
        return render_template("customer.html", data = Amount, errortext = errortext)

    CaID = valid_id()
    #sql_insert = "INSERT INTO D0018E.Cart (CaID, CuID) VALUES ({0}, (SELECT CID FROM D0018E.Customer WHERE CID = {1}))".format(CaID, request.cookies.get('SID'))
    #execute(sql_insert, False)

    res = make_response(redirect(url_for("index", data = Amount), code=307))
    return res

@app.route("/cart")
def cart():
    data = request.args['data'] 
    
    return render_template("cart.html", CartID = data)


@app.route("/Kenobi")
def kenobi():

    login = login_status()
    return render_template("bold_one.html", login = login, loginstatus = request.cookies.get('login'))

@app.route("/login")
def login():
    return render_template("login.html", login = login_status(), loginstatus = request.cookies.get('login'))

@app.route("/login", methods=['POST'])
def loginForm():

    req = request.form
    admins_query = "SELECT AID, AMail, APassword FROM D0018E.Administrator;"
    admins = execute(admins_query)
    registered_query = "SELECT RID, RMail, RPassword FROM D0018E.Registered;"
    registered = execute(registered_query)

    
    for i in range(len(admins)):
        if req['Mail'] == admins[i]['AMail'] and req['Password'] == admins[i]['APassword']:
            res = make_response(redirect("/admin"))
            res.set_cookie('login', 'admin', max_age=60*60*24*365*2)
            res.set_cookie('SID', str(admins[i]['AID']), max_age=60*60*24*365*2)
            return res

    for j in range(len(registered)):
        if req['Mail'] == registered[j]['RMail'] and req['Password'] == registered[j]['RPassword']: 
            res = make_response(redirect("/user"))
            res.set_cookie('login', 'registered', max_age=60*60*24*365*2)
            res.set_cookie('SID', str(registered[j]['RID']), max_age=60*60*24*365*2)
            return res

    return render_template("login.html", login = login_status(), loginstatus = request.cookies.get('login'))

@app.route("/logout")
def logutForm():

    res = make_response(redirect("/"))
    if request.cookies.get('login') != None:
        res.set_cookie('login', 'None', max_age=60*60*24*365*2)

    return res


@app.route("/signup")
def signup():
    query = "SELECT * FROM D0018E.Registered;"
    registered = execute(query)
    return render_template("signup.html", registered = registered, login = login_status(), loginstatus = request.cookies.get('login'))


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

    res = make_response(redirect("/user"))
    res.set_cookie('SID', str(new_ID), max_age=60*60*24*365*2)
    res.set_cookie('login', 'registered', max_age=60*60*24*365*2)
    return res
    


@app.route("/admin")
def admin():
    query = "SELECT AID, AFName, ALName, AMail FROM D0018E.Administrator WHERE AID = {}".format(request.cookies.get('SID'));
    admin = execute(query)

    query2 = "Select PID, PName, PStock, PRating from D0018E.Product"
    table = execute(query2)

    return render_template("admin.html", table = table, admin = admin, login = login_status(), loginstatus = request.cookies.get('login'))

   
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

    query3 = "SELECT AID, AFName, ALName, AMail FROM D0018E.Administrator WHERE AID = {}".format(request.cookies.get('SID'));
    admin = execute(query3)
    query2 = "Select PID, PName, PStock, PRating from D0018E.Product"
    table = execute(query2)
    return render_template("admin.html", table = table, admin = admin, login = login_status(), loginstatus = request.cookies.get('login'))

@app.route("/user")
def user():

    status = request.cookies.get('login')

    if status == 'registered':
        sql = "SELECT RFName, RLName, RBAddress, RDAddress, RMail, RPassword FROM D0018E.Registered WHERE RID = {}".format(request.cookies.get('SID'))
        user = execute(sql)
        return render_template("user.html", user = user, login = login_status(), loginstatus = request.cookies.get('login'))
        
    else:
        res = make_response(redirect("/"))
        return res

@app.route("/user", methods = ['POST'])
def userForm():

    status = request.cookies.get('login')

    if status == 'registered':
        req = request.form
        print(req)
        ID = request.cookies.get('SID')
        keys = ['RID', 'RFName', 'RLName', 'RBAddress', 'RDAddress', 'RMail', 'RPassword']

        try:
            data = parse_registered_data(ID, req, keys)
            parse_string = parse_update_string(data, keys)
            sql = ("UPDATE D0018E.Registered SET {} WHERE RID = ".format(parse_string) + data[0])
            print(sql)
            res = execute(sql, False)
        except:
            errortext = "something went wrong"
            sql = "SELECT RFName, RLName, RBAddress, RDAddress, RMail, RPassword FROM D0018E.Registered WHERE RID = {}".format(request.cookies.get('SID'))
            user = execute(sql)
            return render_template("user.html", user = user, errortext = errortext)

        sql = "SELECT RFName, RLName, RBAddress, RDAddress, RMail, RPassword FROM D0018E.Registered WHERE RID = {}".format(request.cookies.get('SID'))
        user = execute(sql)
        return render_template("user.html", user = user, login = login_status(), loginstatus = request.cookies.get('login'))


    else:
        res = make_response(redirect("/"))
        return res



if __name__ == "__main__":
    app.run(host='0.0.0.0')