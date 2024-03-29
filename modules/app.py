"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""

from flask import Flask, request,render_template, make_response, redirect, url_for
import pymysql.cursors
import random
import parse
import valid

def execute(sql, isSelect = True):
    conn = pymysql.connect(host='127.0.0.1',
                           port=3306,
                           user='jakmor-8',
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


app = Flask(__name__)


@app.route("/", methods=['POST'])
def cart_route():

    if request.cookies.get('login') == 'admin':
        return make_response(redirect("/"))
    data1 = ""
    flag2 = False
    print(request.args)
    if request.args:
        data1 = request.args['data']
        flag2 = True
    print("data1 ", data1)
    data2 = ""
    if not flag2:
        data2 = "{0}, {1}, {2}".format(request.form['form_id'], request.form['Amount'], request.form['price'])
        if not valid_amount(request.form['form_id'], int(request.form['Amount'])):
            return make_response(redirect("/"))
    else:
        temp = data1.split(",")
        if not valid_amount(temp[0], int(temp[1])):
            return make_response(redirect("/"))

    
    if flag2:
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

    flag = True
    for i in range(len(customers)):
        if customers[i]['CID'] == cookie_id:
            flag = False
    print("ye that worked")
    
    if request.cookies.get('login') == 'None' and flag:
        res = make_response(redirect(url_for(".customer", data = data2)))
        return res
    print("ok")

    res = make_response(redirect(url_for('.cart', data = data2)))
    CaID = valid_id()
    
    print("weird")
    if request.cookies.get('login') == 'registered':
        sql_insert = "INSERT INTO D0018E.Cart (CaID, CBought, ReID) SELECT {0}, 0, (SELECT RID FROM D0018E.Registered WHERE RID = {1}) FROM DUAL WHERE NOT EXISTS (SELECT CBought FROM D0018E.Cart WHERE CBought = 0 AND CaID = {0})".format(CaID, cookie_id)
        execute(sql_insert, False)
    elif request.cookies.get('login') == 'None':
        sql_insert = "INSERT INTO D0018E.Cart (CaID, CBought, CuID) SELECT {0}, 0, (SELECT CID FROM D0018E.Customer WHERE CID = {1}) FROM DUAL WHERE NOT EXISTS (SELECT CBought FROM D0018E.Cart WHERE CBought = 0 AND CaID = {0})".format(CaID, cookie_id)
        execute(sql_insert, False)
        if flag2:
            res = make_response(redirect(url_for('.cart', data = data1)))
    
    return res

@app.route("/")
def hello():
    
    app.add_url_rule('/', 'index', hello)

    sql1 = "SELECT Product.PID, Product.PName, Product.PColor, Product.PDescript, Available.APrice, Available.AStock FROM (D0018E.Product INNER JOIN D0018E.Available ON D0018E.Product.PID = D0018E.Available.PrID)"
    product = execute(sql1)

    res = make_response(render_template("home.html", product = product, login = login_status(), loginstatus = request.cookies.get('login')))

    if not request.cookies.get('SID'):
   
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

    req = request.form
    print(req)
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
    except pymysql.err.OperationalError:
        errortext = "Please enter all required fields"
        return render_template("customer.html", data = data, errortext = errortext, login = login_status(), loginstatus = request.cookies.get('login'))
    except pymysql.err.DataError:
        errortext = "Field too long"
        return render_template("customer.html", data = data, errortext = errortext, login = login_status(), loginstatus = request.cookies.get('login'))

    CaID = valid_id()

    res = make_response(redirect(url_for("index", data = data), code=307))
    return res


@app.route("/cart")
def cart():

    CaID = ""
    try:
        if request.cookies.get('login') == 'registered':
            sql1 = "SELECT CaID FROM D0018E.Cart WHERE ReID = {} and CBought = 0".format(request.cookies.get('SID'))
            res = execute(sql1)
            CaID = res[0]['CaID']
        elif request.cookies.get('login') == 'None':
            sql1 = "SELECT CaID FROM D0018E.Cart WHERE CuID = {} and CBought = 0".format(request.cookies.get('SID'))
            res = execute(sql1)
            CaID = res[0]['CaID']
    except IndexError:
        return render_template("cart.html", empty_flag = True, login = login_status(), loginstatus = request.cookies.get('login'))
    print(CaID)

    if request.args:
        
        keys = ["IID", "CaID", "PrID", "IAmount", "IPrice"]
        keys = ", ".join(map(str, keys))

        data = request.args['data'].split(",")
        print("cart data ", data)
        IID = valid_id()

        sql_check_if_exists = "SELECT PrID, IAmount, IID FROM D0018E.Item WHERE CaID = {0} and PrID = {1}".format(CaID, data[0])
        PrIDs = execute(sql_check_if_exists)

        if PrIDs and str(PrIDs[0]['PrID']) in data:
            temp = int(data[1]) + int(PrIDs[0]['IAmount'])
            update = "UPDATE D0018E.Item SET IAmount = {0} WHERE IID = {1}".format(temp, int(PrIDs[0]['IID']))
            execute(update, False)
        else:
            sql_insert = "INSERT INTO D0018E.Item ({0}) VALUES ({1}, (SELECT CaID FROM D0018E.Cart WHERE CaID = {2} and CBought = 0), (SELECT PID FROM D0018E.Product WHERE PID = {3}), {4}, {5})".format(keys, str(IID), CaID, data[0], data[1], int(data[1])* int(data[2]))
            execute(sql_insert, False)

    sql_items = "SELECT Product.PName, Item.IPrice, Item.IAmount, Item.IID FROM (D0018E.Product INNER JOIN D0018E.Item ON D0018E.Product.PID = D0018E.Item.PrID) WHERE D0018E.Item.CaID = {}".format(CaID)
    table = execute(sql_items)
    return render_template("cart.html", table = table, login = login_status(), loginstatus = request.cookies.get('login'))


@app.route("/cart", methods=['POST'])
def change_cart():
    
    data = request.form
    print(data)
    if data['form_id'] == '-1':
        SID = request.cookies.get('SID')
        check_cart = "SELECT IID FROM D0018E.Item WHERE EXISTS (SELECT CaID FROM D0018E.Cart WHERE D0018E.Item.CaID = D0018E.Cart.CaID AND ( ReID = {0} OR CuID = {1}) AND CBought = 0)".format(SID, SID)
        print(check_cart)
        cart = execute(check_cart)

        if cart:
            for i in range(len(cart)):
                sql = "SELECT IAmount, PrID FROM D0018E.Item WHERE IID = {}".format(cart[i]['IID'])
                amount = execute(sql)

                if not valid_amount(amount[0]['PrID'], 0):
                    return redirect("/cart")
            return redirect("/check_out")
        else: 
            return redirect("/cart")
    try:
        amount = int(data["Amount"])
        sql = "SELECT IAmount, PrID, IPrice FROM D0018E.Item WHERE IID = " + data['form_id']
        print(sql)
        cur_amount = execute(sql)
        new_amount = amount + int(cur_amount[0]['IAmount'])
    except ValueError:
        return redirect("/cart")
    

    if new_amount <= 0:
        sql1 = "SELECT CaID FROM D0018E.Item WHERE IID = {}".format(data['form_id'])
        CaID = execute(sql1)[0]['CaID']

        sql2 = "DELETE FROM D0018E.Item WHERE IID = {}".format(data['form_id'])
        execute(sql2, False)

        sql3 = "SELECT IID, IAmount, IPrice FROM D0018E.Item WHERE CaID = {}".format(CaID)
        table = execute(sql3)
        print("Table ", table)
        if table!= ():
            return render_template("cart.html", table = table, login = login_status(), loginstatus = request.cookies.get('login'))
        else:
            return render_template("cart.html", empty_flag = True, login = login_status(), loginstatus = request.cookies.get('login'))
    elif valid_amount(str(cur_amount[0]['PrID']) , amount):

        sql1 = "SELECT APrice FROM D0018E.Available WHERE PrID = {}".format(cur_amount[0]['PrID'])
        old_price = execute(sql1)[0]['APrice']

        new_price = (int(old_price) * amount) + int(cur_amount[0]['IPrice'])
        print("new things ", new_amount, " ", new_price)

        sql2 = "UPDATE D0018E.Item SET IAmount = {0}, IPrice = {1} WHERE IID = {2}".format(new_amount, new_price ,data['form_id'])
        execute(sql2, False)

    
    return redirect("/cart")


@app.route("/check_out")
def check_out():

    loginstatus = request.cookies.get('login')
    CaID = ""
    old_tableS = []
    Old_CaIDs = []
    print("status ", loginstatus)
    if loginstatus == 'None':
        sql1 = "SELECT CaID FROM D0018E.Cart WHERE CuID = {} and CBought = 0".format(request.cookies.get('SID'))
        CaID = execute(sql1)[0]['CaID']
        sql2 = "SELECT CaID FROM D0018E.Cart WHERE CuID = {} and CBought = 1".format(request.cookies.get('SID'))
        Old_CaIDs = execute(sql2)

    elif loginstatus == 'registered':
        sql1 = "SELECT CaID FROM D0018E.Cart WHERE ReID = {} and CBought = 0".format(request.cookies.get('SID'))
        CaID = execute(sql1)[0]['CaID']
        sql2 = "SELECT CaID FROM D0018E.Cart WHERE ReID = {} and CBought = 1".format(request.cookies.get('SID'))
        Old_CaIDs = execute(sql2)

    for j in range(len(Old_CaIDs)):
        sql3 = "SELECT Product.PName, Product.PColor, Product.PDescript, Item.IPrice, Item.IAmount FROM (D0018E.Product INNER JOIN D0018E.Item ON D0018E.Product.PID = D0018E.Item.PrID) WHERE EXISTS (SELECT CBought FROM D0018E.Cart WHERE Item.CaID = {} and CBought = 1)".format(Old_CaIDs[j]['CaID'])
        old_table = execute(sql3)
        old_tableS.append(old_table)

    sql4 = "SELECT Product.PName, Product.PColor, Product.PDescript, Item.IPrice, Item.IAmount FROM (D0018E.Product INNER JOIN D0018E.Item ON D0018E.Product.PID = D0018E.Item.PrID) WHERE EXISTS (SELECT CBought FROM D0018E.Cart WHERE Item.CaID = {} and CBought = 0)".format(CaID)
    table = execute(sql4)

    sql5 = "UPDATE D0018E.Cart SET CBought = 1 WHERE CaID = {}".format(CaID)
    execute(sql5, False)

    
    for i in range(len(table)):
        sql6 = "SELECT AStock FROM D0018E.Available WHERE PrID = (SELECT PID FROM D0018E.Product WHERE PName = '{}' )".format(table[i]['PName'])
        available = execute(sql6)
        print("aval ", available)
        new_amount = int(available[0]['AStock']) - int(table[i]['IAmount'])
        sql7 = "UPDATE D0018E.Available SET AStock = {0} WHERE PrID = (SELECT PID FROM D0018E.Product WHERE PName = '{1}' )".format(new_amount ,table[i]['PName'])
        print("sql ", sql7)
        execute(sql7, False)

    return render_template("checkout.html", table = table , old_tables = old_tableS, login = login_status(), loginstatus = loginstatus)

@app.route("/Kenobi")
def kenobi():

    login = login_status()
    return render_template("easter_egg.html", login = login, loginstatus = request.cookies.get('login'))

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
        res.set_cookie('SID', str(valid_id()), max_age=60*60*24*365*2)

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
        return render_template("signup.html", registered = registered, errortext = errortext, login = login_status(), loginstatus = request.cookies.get('login'))
    except pymysql.err.OperationalError:
        errortext = "Please enter all required fields"
        return render_template("signup.html", registered = registered, errortext = errortext, login = login_status(), loginstatus = request.cookies.get('login'))
    except pymysql.err.DataError:
        errortext = "Field too long"
        return render_template("signup.html", registered = registered, errortext = errortext, login = login_status(), loginstatus = request.cookies.get('login'))

    res = make_response(redirect("/user"))
    res.set_cookie('SID', str(new_ID), max_age=60*60*24*365*2)
    res.set_cookie('login', 'registered', max_age=60*60*24*365*2)
    return res
    


@app.route("/admin")
def admin():
    sql = "SELECT AID, AFName, ALName, AMail, APassword FROM D0018E.Administrator WHERE AID = {}".format(request.cookies.get('SID'));
    admin = execute(sql)

    try:
        sql2 = "SELECT D0018E.Product.*, D0018E.Available.* FROM D0018E.Product INNER JOIN D0018E.Available ON D0018E.Product.PID = D0018E.Available.PrID;"
        table = execute(sql2)
    except pymysql.err.Error:
        print("bad inner join")

    try:
        sql3 = "SELECT * FROM D0018E.Product LEFT JOIN D0018E.Available ON D0018E.Product.PID = D0018E.Available.PrID UNION ALL SELECT * FROM D0018E.Product RIGHT JOIN D0018E.Available ON D0018E.Product.PID = D0018E.Available.PrID WHERE D0018E.Product.PID IS NULL;"
        table2 = execute(sql3)
    except pymysql.err.Error:
        print("bad outer join")

    return render_template("admin.html", table = table, table2 = table2, admin = admin, login = login_status(), loginstatus = request.cookies.get('login'))

   
@app.route("/admin", methods=['POST'])
def adminForm():

    errortext = ''
    req = request.form
    print(req)
    
    product_keys = ['PID', 'PName', 'PColor', 'PDescript']
    price_keys = ['AvID', 'APrice', 'AStock', 'PrID']

    if req['form_id'] == '1':
        try:
            product_ID = valid_id()
            price_ID = valid_id()

            form1 = parse_product_data(product_ID, req, product_keys)
            form2 = parse_price_data(price_ID, req, price_keys[:3])

            product_keys = ", ".join(map(str, product_keys))
            price_keys = ", ".join(map(str, price_keys))

            sql1 = "INSERT INTO D0018E.Product ({0}) VALUES {1}".format(product_keys, tuple(form1))
            res = execute(sql1, False)
            sql2 = "INSERT INTO D0018E.Available ({0}) VALUES ({1}, {2}, {3}, (SELECT PID FROM D0018E.Product WHERE PID = {4}));".format(price_keys, form2[0], form2[1], form2[2],  product_ID)
            res = execute(sql2, False)
        except pymysql.err.ProgrammingError:
            print("bad sql query")

    elif req['form_id'] == '2':
        try:
            product_ID = req['PID']
            try:
                sql = "SELECT AvID FROM D0018E.Available WHERE PrID = {0};".format(product_ID)
                res = execute(sql)
                price_ID = res[0]['AvID']
            except pymysql.err.ProgrammingError:
                print("this sytax sucks ass")

            price_keys = ['AvID', 'APrice', 'AStock']

            form1 = parse_product_data(product_ID, req, product_keys)
            form2 = parse_price_data(price_ID, req, price_keys)

            parse_string1 = parse_update_string(form1, product_keys)
            parse_string2 = parse_update_string(form2, price_keys)

            if parse_string1 != '':
                sql2 = "UPDATE D0018E.Product SET {0} WHERE PID = {1}".format(parse_string1, form1[0])
                res1 = execute(sql2, False)
            
            elif parse_string2 != '':
                sql3 = "UPDATE D0018E.Available SET {0} WHERE AvID = {1}".format(parse_string2, form2[0])
                res2 = execute(sql3, False)

        except pymysql.err.ProgrammingError:
            print("bad sql query")

    elif req['form_id'] == '3':
        
        sql = "DELETE FROM D0018E.Product WHERE PID = {};".format(req['PID'])
        print(sql)
        res = execute(sql, False)


    query3 = "SELECT AID, AFName, ALName, AMail, APassword FROM D0018E.Administrator WHERE AID = {}".format(request.cookies.get('SID'));
    admin = execute(query3)
    try:
        sql4 = "SELECT D0018E.Product.*, D0018E.Available.* FROM D0018E.Product INNER JOIN D0018E.Available ON D0018E.Product.PID = D0018E.Available.PrID;"
        table = execute(sql4)
    except pymysql.err.Error:
        print("bad inner join")

    return render_template("admin.html", errortext = errortext, table = table, admin = admin, login = login_status(), loginstatus = request.cookies.get('login'))

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
            sql = "UPDATE D0018E.Registered SET {0} WHERE RID ={1};".format(parse_string, data[0])
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

@app.route("/product")
def product(): #you just had to smh...

    product_id = request.args['data']
    sql1 = "SELECT * FROM (D0018E.Product INNER JOIN D0018E.Available ON D0018E.Product.PID = D0018E.Available.PrID) WHERE PID = " + '"{}"'.format(request.args['data'])
    product = execute(sql1)
    sql2 = "SELECT RaID, RRating, RReview, CuID, ReID FROM D0018E.Rating WHERE PrID = {0}".format(product_id)
    keys = ['RaID', 'RRating', 'RReview', 'CuID', 'ReID']
    reviews = parse_reviews(execute(sql2), keys)
    print(reviews)


    return render_template("product.html", review = reviews, product = product, login = login_status(), loginstatus = request.cookies.get('login'))

@app.route("/product", methods=['POST'])
def cart_route_product():
    if request.cookies.get('login') == 'admin':
        return make_response(redirect("/"))

    data1 = ""
    flag2 = False
    data1 = request.args['data'].split(",")
    del data1[0]
    if data1:
        flag2 = True
    print("data1 ", data1)
    data2 = ""
    if not flag2:
        data2 = "{0}, {1}, {2}".format(request.form['form_id'], request.form['Amount'], request.form['price'])
        if not valid_amount(request.form['form_id'], int(request.form['Amount'])):
            return make_response(redirect("#top"))

    else:
        temp = data1.split(",")
        if not valid_amount(temp[0], int(temp[1])):
            return make_response(redirect("#top"))

    if flag2:
        temp = data1.split(",")
        print("temp: ", temp)
        if temp == ['']: 
            return make_response(redirect("#top"))

        elif int(temp[1]) <= 0:
            return make_response(redirect("#top"))

    elif not flag2:
        temp = data2.split(",")
        print("temp: ", temp)
        if temp[1] == ' ': 
            return make_response(redirect("#top"))

        elif int(temp[1]) <= 0:
            return make_response(redirect("#top"))

    sql1 = "SELECT CID from D0018E.Customer"
    customers = execute(sql1)
    sql2 = "SELECT CuID, ReID FROM D0018E.Cart"
    IDs = execute(sql2)

    cookie_id = int(request.cookies.get('SID'))

    flag = True
    for i in range(len(customers)):
        if customers[i]['CID'] == cookie_id:
            flag = False
    
    if request.cookies.get('login') == 'None' and flag:
        res = make_response(redirect(url_for(".customer", data = data2)))
        return res
    print("ok")

    res = make_response(redirect(url_for('.cart', data = data2)))
    CaID = valid_id()
    
    if request.cookies.get('login') == 'registered':
        sql_insert = "INSERT INTO D0018E.Cart (CaID, CBought, ReID) SELECT {0}, 0, (SELECT RID FROM D0018E.Registered WHERE RID = {1}) FROM DUAL WHERE NOT EXISTS (SELECT CBought FROM D0018E.Cart WHERE CBought = 0 AND CaID = {0})".format(CaID, cookie_id)
        execute(sql_insert, False)
    elif request.cookies.get('login') == 'None':
        sql_insert = "INSERT INTO D0018E.Cart (CaID, CBought, CuID) SELECT {0}, 0, (SELECT CID FROM D0018E.Customer WHERE CID = {1}) FROM DUAL WHERE NOT EXISTS (SELECT CBought FROM D0018E.Cart WHERE CBought = 0 AND CaID = {0})".format(CaID, cookie_id)
        execute(sql_insert, False)
        if flag2:
            res = make_response(redirect(url_for('.cart', data = data1)))
    
    return res

@app.route("/Review")
def review():

    product_id = request.args['data']

    return render_template("review.html", product_id = product_id, login = login_status(), loginstatus = request.cookies.get('login'))


@app.route("/Review", methods=['POST'])
def write_review():
    print(request.form)

    data1 = request.args['data'].split(",")
    data1 = data1[0]
    print(data1)
    if request.cookies.get('login') == 'admin':
        return make_response(redirect(url_for('.product', data = data1)))

    sql1 = "SELECT CID FROM D0018E.Customer"
    customers = execute(sql1)

    sql2 = "SELECT CuID, ReID FROM D0018E.Rating"
    IDs = execute(sql2)

    cookie_id = int(request.cookies.get('SID'))

    flag = True
    for i in range(len(customers)):
        if customers[i]['CID'] == cookie_id:
            flag = False
    
    if request.cookies.get('login') == 'None' and flag:
        res = make_response(redirect(url_for(".customer", data = data1)))
        return res

    res = make_response(redirect(url_for('.product', data = data1)))
    RaID = valid_id()
    
    if request.cookies.get('login') == 'registered':
        sql_insert = "INSERT INTO D0018E.Rating (RaID, RRating, RReview, PrID, ReID) VALUES({0}, {1}, '{2}', (SELECT PID FROM D0018E.Product WHERE PID = {3}), (SELECT RID FROM D0018E.Registered WHERE RID = {4}));".format(RaID, request.form['RRating'], request.form['RReview'], data1, cookie_id)
        print(sql_insert)
        execute(sql_insert, False)
    elif request.cookies.get('login') == 'None':
        sql_insert = "INSERT INTO D0018E.Rating (RaID, RRating, RReview, PrID, CuID) VALUES({0}, {1}, '{2}', (SELECT PID FROM D0018E.Product WHERE PID = {3}), (SELECT CID FROM D0018E.Customer WHERE CID = {4}));".format(RaID, request.form['RRating'], request.form['RReview'], data1, cookie_id)
        print(sql_insert)
        execute(sql_insert, False)
       
    return res

if __name__ == "__main__":
    app.run(host='0.0.0.0')
