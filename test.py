from flask import Flask, request,render_template
import pymysql.cursor

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
                #print(f"result = {result}")
            else:
                cursor.execute(sql)
                result = conn.insert_id()
                conn.commit()
    finally:
        conn.close()
    return result

app = Flask(__name__)

@app.route("/")
def hello():
    return render_template("test.html")

@app.route("/Kenobi")
def kenobi():
    return render_template("bold_one.html")

@app.route("/data")
def data():
    sql = "Select * from D0018E.test"
    data = execute(sql)
    print(data)
    return str(data)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
