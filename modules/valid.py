import app
import parse

# Pre PrID string of existing product, Amount int of how many products to be in cart
def valid_amount(PrID, Amount):

    id = request.cookies.get('SID')
    print("args valid_amount", PrID, " ", Amount)

    sql1 = "SELECT AStock FROM D0018E.Available WHERE PrID = {}".format(PrID)
    stock = execute(sql1)[0]['AStock']
    print(stock)


    CaID = ""
    try:
        if request.cookies.get('login') == 'registered':
            sql2 = "SELECT CaID FROM D0018E.Cart WHERE ReID = {} and CBought = 0".format(id)
            CaID  = execute(sql2)[0]['CaID']
        elif request.cookies.get('login') == 'None':
            sql2 = "SELECT CaID FROM D0018E.Cart WHERE CuID = {} and CBought = 0".format(id)
            CaID  = execute(sql2)[0]['CaID']

        sql3 = "SELECT IAmount FROM D0018E.Item WHERE PrID = {0} and CaID = {1}".format(PrID, CaID)
        res = execute(sql3)

        cur_amount = res[0]['IAmount']
        if len(res) > 1:
            for i in range(1, len(res)):
                cur_amount += res[i]['IAmount']

        if Amount + cur_amount > stock:
            return False
        else:
            return True
    except IndexError: #if no cart
        if Amount > stock:
            return False
        else:
            return True
    

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
