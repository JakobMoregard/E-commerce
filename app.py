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


def parse_product_data(ID, data, keys):

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


def parse_price_data(ID, data, keys):

    data_content = []
    used_keys = []

    data_content.append(ID)
    print(ID)

    for i in range(1, len(keys)-1):
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
    sql4 = "SELECT PID FROM D0018E.Product"
    product_IDs = execute(sql4)
    sql5 = "SELECT AvID FROM D0018E.Available"
    available_IDs = execute(sql5)
    sql6 = "SELECT RaID FROM D0018E.Rating"
    rating_IDs = execute(sql6)
    sql7 = "SELECT CaID FROM D0018E.Cart"
    cart_IDs = execute(sql7)
    sql8 = "SELECT IID FROM D0018E.Item"
    Item_IDs = execute(sql8)

    if id not in admin_IDs or customer_IDs or registered_IDs or product_IDs or available_IDs or rating_IDs  or cart_IDs or item_IDs:
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

    
    data1 = ""
    flag2 = False
    if request.args:
        data1 = request.args['data']
        flag2 = True

    data2 = ""
    if not flag2:
        data2 = "{0}, {1}".format(request.form['form_id'], request.form['Amount'])

    if request.cookies.get('login') == 'admin':
        return make_response(redirect("/"))
    elif flag2:
        temp = data1.split(",")
        print("temp: ", temp)
        if temp == ['']: 
            return make_response(redirect("/"))
        elif int(temp[1]) <= 0:
            return make_response(redirect("/"))
    elif not flag2:
        temp = data2.split(",")
        print("temp: ", temp)
        if temp[1] == ' ': 
            return make_response(redirect("/"))
        elif int(temp[1]) <= 0:
            return make_response(redirect("/"))


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

    
    if request.cookies.get('login') == 'None' and flag:
        res = make_response(redirect(url_for(".customer", data = data2)))
        return res

    res = make_response(redirect(url_for('.cart', data = data2)))
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
        if flag2:
            res = make_response(redirect(url_for('.cart', data = data1)))
    
    return res

@app.route("/")
def hello():
    
    app.add_url_rule('/', 'index', hello)
    sql1 = "SELECT PID, PName, PColor, PDescript FROM D0018E.Product;"
    product = execute(sql1)
    sql2 = "SELECT AvID, APrice, AStock, PrID FROM D0018E.Available;"
    price = execute(sql2)

    res = make_response(render_template("test.html", product = product, price = price, login = login_status(), loginstatus = request.cookies.get('login')))

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
        name = request.cookies.get('SID')
 
    return res 


@app.route("/customer")
def customer():

    data = request.args['data']
    print("data ", data)
    return render_template("customer.html", data = data, login = login_status(), loginstatus = request.cookies.get('login'))

@app.route("/customer", methods=['POST'])
def customerForm():

    #query1 = "SELECT * FROM D0018E.Customer"
    #registered = execute(query1)

    req = request.form
    keys = ['CID', 'CFName', 'CLName', 'CBAddress', 'CDAddress']

    data = req['data']
    print("data ", data)
    try:
        ID = request.cookies.get('SID')
        form = parse_registered_data(ID, req, keys)
        keys = ", ".join(map(str, keys))
        query = ("INSERT INTO D0018E.Customer ({0}) VALUES {1}".format(keys, tuple(form)))
        execute(query, False)
    except pymysql.err.IntegrityError:
        errortext = "Customer is already registered"
        return render_template("customer.html", data = data, errortext = errortext, login = login_status(), loginstatus = request.cookies.get('login'))

    CaID = valid_id()
    #sql_insert = "INSERT INTO D0018E.Cart (CaID, CuID) VALUES ({0}, (SELECT CID FROM D0018E.Customer WHERE CID = {1}))".format(CaID, request.cookies.get('SID'))
    #execute(sql_insert, False)

    res = make_response(redirect(url_for("index", data = data), code=307))
    return res




@app.route("/cart")
def cart():



    CaID = ""
    try:
        if request.cookies.get('login') == 'registered':
            sql1 = "SELECT CaID FROM D0018E.Cart WHERE ReID = {}".format(request.cookies.get('SID'))
            res = execute(sql1)
            print(res)
            CaID = res[0]['CaID']
        elif request.cookies.get('login') == 'None':
            sql1 = "SELECT CaID FROM D0018E.Cart WHERE CuID = {}".format(request.cookies.get('SID'))
            res = execute(sql1)
            print(res)
            CaID = res[0]['CaID']
    except IndexError:
        return render_template("cart.html", NoCartID = "No cart, please add something so I can eat tonight", login = login_status(), loginstatus = request.cookies.get('login'))
    print(CaID)
    
    #data[0] = PID, data[1] = Amount 
    if request.args:
        
        keys = ["IID", "CaID", "PrID", "IAmount"]
        keys = ", ".join(map(str, keys))

        data = request.args['data'].split(",")
        IID = valid_id()

        sql_check_if_exists = "SELECT PrID, IAmount, IID FROM D0018E.Item WHERE CaID = {}".format(CaID)
        PrIDs = execute(sql_check_if_exists)
        print(PrIDs)
        if PrIDs:
            temp = int(data[1]) + int(PrIDs[0]['IAmount'])
            print(temp)
            update = "UPDATE D0018E.Item SET IAmount = {0} WHERE IID = {1}".format(temp, int(PrIDs[0]['IID']))
            execute(update, False)
        else:
            sql_insert = "INSERT INTO D0018E.Item ({0}) VALUES ({1}, (SELECT CaID FROM D0018E.Cart WHERE CaID = {2}), (SELECT PID FROM D0018E.Product WHERE PID = {3}), {4})".format(keys, str(IID), CaID, data[0], data[1])
            execute(sql_insert, False)

    sql_items = "SELECT IID, IAmount FROM D0018E.Item WHERE CaID = {}".format(CaID)
    table = execute(sql_items)
    return render_template("cart.html", table = table , loginstatus = request.cookies.get('login'))


@app.route("/cart", methods=['POST'])
def change_cart():
    
    data = request.form
    print(data)
    return redirect("/cart")


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

    query2 = "Select PID, PName from D0018E.Product"
    table = execute(query2)

    return render_template("admin.html", table = table, admin = admin, login = login_status(), loginstatus = request.cookies.get('login'))

   
@app.route("/admin", methods=['POST'])
def adminForm():

    req = request.form
    print(req)
    
    product_keys = ['PID', 'PName', 'PColor', 'PDescript']
    price_keys = ['AvID', 'APrice', 'AStock', 'PrID']

    if req['form_id'] == '1':
        try:
            product_ID = valid_id()
            price_ID = valid_id()

            form1 = parse_product_data(product_ID, req, product_keys)
            form2 = parse_price_data(price_ID, req, price_keys)

            product_keys = ", ".join(map(str, product_keys))
            price_keys = ", ".join(map(str, price_keys))

            sql1 = "INSERT INTO D0018E.Product ({0}) VALUES {1}".format(product_keys, tuple(form1))
            res = execute(sql1, False)
            sql2 = "INSERT INTO D0018E.Available ({0}) VALUES ({1}, (SELECT PID FROM D0018E.Product WHERE PID = {2}));".format(price_keys, form2, str(product_ID)) 
            res = execute(sql2, False)
        except pymysql.err.ProgrammingError:
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
    query2 = "Select PID, PName from D0018E.Product"
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
