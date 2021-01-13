import app
import valid


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

def parse_reviews(review_data, keys):

    new_data = []

    for i in range(len(review_data)):
        temp_data = {}
        for j in range(len(review_data[i])):
            if keys[j] == 'CuID' and review_data[i][keys[j]] != None:

                sql = "SELECT CFName FROM D0018E.Customer WHERE CID = {}".format(review_data[i][keys[j]])
                temp_data['ID'] = execute(sql)[0]['CFName']
            elif keys[j] == 'ReID' and review_data[i][keys[j]] != None:
                sql = "SELECT RFName FROM D0018E.Registered WHERE RID = {}".format(review_data[i][keys[j]])
                temp_data['ID'] = execute(sql)[0]['RFName']
            elif review_data[i][keys[j]] != None:
                temp_data[keys[j]] = review_data[i][keys[j]]
        new_data.append(temp_data)

    return new_data


def parse_price_data(ID, data, keys):

    print(data)
    print(keys)
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

def parse_pid(ID):

    sql = "SELECT PID FROM D0018E.Product"
    product = execute(sql)
    for i in range(len(product)):
        if product[i]['PID'] == ID:
            return product[i]['PID']

    return ''
