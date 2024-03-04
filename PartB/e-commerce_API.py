from flask import Flask, request, render_template
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
def connection():
    return psycopg2.connect(database='e-commerce', host='localhost', user='db_user', password='root', port=5432)

def SQLquery(query:str, *args):
    with connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, args)
                data = cursor.fetchall()
                conn.commit()
    return data

@app.route('/shop')
def shop(): #shopping page
    return render_template("shop.html")

@app.route('/')
def login(): #login page
    return render_template("login.html")

@app.route('/getServer')
def getServer():
    return {"code":200, "server":"localhost:3001"}


################       /PRODUCTS/        ##################
@app.route('/products', methods=['GET', 'POST'])
def routeProducts():
    if request.method == 'GET':
        s=""
        for key,value in request.args.to_dict().items():  
            s+=f"{key}={value} and " if isinstance(value, int) or isinstance(value, float) else f"{key}='{value}' and "
        if len(s)>0:
            data = SQLquery("SELECT * FROM products WHERE "+s[:-5]+";")
        else:
            data = SQLquery("SELECT * FROM products;")
        return data
    elif request.method == 'POST':
        product = request.get_json()
        with connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("INSERT INTO products(name,description,category,stock_status,price) VALUES(%(name)s,%(description)s,%(category)s,%(stock_status)s,%(price)s) RETURNING *;", product)
                product = cursor.fetchone()
                conn.commit()        
        return product
    else:
        return 'error wrong request method'


@app.route('/products/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def routeProductsId(id):
    if request.method == 'GET':
        data = SQLquery("SELECT * FROM products WHERE productid=%s;", id)
        if len(data)!=0:
            return data[0]
        else:
            return {'code':404, 'error':'Product not found'}
    elif request.method == 'PUT':
        s=""
        for key,value in request.get_json().items():
            s+=f"{key}={value}," if isinstance(value, int) or isinstance(value, float) else f"{key}='{value}',"
        try:
            with connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(f"UPDATE products SET {s[:-1]} WHERE productid=%s;", (id,))
                    cursor.execute("SELECT * FROM products WHERE productid=%s;", (id,))
                    product = cursor.fetchone()
                    conn.commit()        
            return product
        except Exception as e:
            print(e)
            return {'code':400, 'error':'Bad request'}
    elif request.method == 'DELETE':
        try:
            with connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("DELETE FROM orderdetails WHERE productid=%s;", (id,))
                    cursor.execute("DELETE FROM cartdetails WHERE productid=%s;", (id,))
                    cursor.execute("DELETE FROM products WHERE productid=%s;", (id,))
                    conn.commit()
            return {'code':200, 'success':'Product removed and all dependencies'}
        except Exception as e:
            print(e)
            return {'code':404, 'error':'Product not found'}
    else:
        return {'code':405, 'error':'Method Not Allowed'}


#################         /ORDERS/        ###########
@app.post('/orders')
def PostOrders():
    data=request.get_json()
    try:
        with connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("INSERT INTO orders(userid, order_status) VALUES(%(userid)s, %(order_status)s) RETURNING orderid;", data)
                orderid = cursor.fetchone()['orderid']
                assert(len(data['products'])==len(data['quantities']))
                for i in range(len(data['products'])):
                    cursor.execute("INSERT INTO orderdetails VALUES(%s, %s, %s);", (orderid, data['products'][i], data['quantities'][i],))
                ##instead of listing with productid, list with product.name##
                cursor.execute("SELECT o.orderid, array_agg(od.productid) AS productids, array_agg(p.name) AS productnames, array_agg(od.quantity) AS quantities, o.total_price, o.order_status FROM orders o JOIN orderdetails od ON o.orderid=od.orderid JOIN products p ON p.productid=od.productid WHERE o.orderid=%s GROUP BY o.orderid;", (orderid,))
                data = cursor.fetchone()
                conn.commit()
        return data
    except Exception as e:
        print(e)
        return {'code':400, 'error':'Bad request'}

@app.get('/orders/<int:userid>')
def getOrdersId(userid):
    try:
        data = SQLquery("SELECT o.orderid, array_agg(od.productid) AS productids, array_agg(p.name) AS productnames, array_agg(od.quantity) AS quantities, o.total_price, o.order_status FROM orders o JOIN orderdetails od ON o.orderid=od.orderid JOIN products p ON p.productid=od.productid WHERE userid=%s GROUP BY o.orderid;", userid)
        return data
    except Exception as e:
        print(e)
        return {'code':404, 'error':'ID user not found'}


####################      /CART/       #########################
@app.route('/cart/<int:userid>', methods=['GET', 'POST'])
def routeCartUserId(userid):
    if request.method == 'GET':
        try:
            data = SQLquery("SELECT c.userid, array_agg(cd.productid) AS products, array_agg(cd.quantity) AS quantities, c.total_price FROM cart c JOIN cartdetails cd ON c.userid=cd.userid WHERE c.userid=%s GROUP BY c.userid;", (userid,))
            return data[0]
        except Exception as e:
            print(e)
            return {'code':404, 'error':'Not Found'}
    elif request.method == 'POST':
        data=request.get_json()
        try:
            with connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("SELECT 1 FROM cart WHERE userid=%s;", (userid,))
                    if not cursor.fetchone():
                        cursor.execute("INSERT INTO cart(userid) VALUES(%s);", (userid,))
                    cursor.execute("INSERT INTO cartdetails VALUES(%s, %s, %s);", (userid, data['productid'], data['quantity'],))
                    cursor.execute("SELECT c.userid, array_agg(cd.productid) AS products, array_agg(cd.quantity) AS quantities, c.total_price FROM cart c JOIN cartdetails cd ON c.userid=cd.userid WHERE c.userid=%s GROUP BY c.userid;", (userid,))
                    data = cursor.fetchone()
                    conn.commit()
            return data
        except Exception as e:
            print(e)
            return {'code':400, 'error':'Bad request'}
    else:
        return {'code':405, 'error':'Method Not Allowed'}


@app.delete('/cart/<int:userid>/item/<int:productid>')
def deleteCartProduct(userid, productid):
    try:
        with connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("DELETE FROM cartdetails cd WHERE cd.productid=%s AND cd.userid IN (SELECT userid FROM cart WHERE userid=%s);", (productid, userid,))
                cursor.execute("SELECT c.userid, array_agg(cd.productid) AS products, array_agg(cd.quantity) AS quantities, c.total_price FROM cart c JOIN cartdetails cd ON c.userid=cd.userid WHERE c.userid=%s GROUP BY c.userid;", (userid,))
                data = cursor.fetchone()
                conn.commit()
        if data:
            return data
        else:
            return {'code':204, 'success':'No Content'}
    except Exception as e:
        print(e)
        return {'code':400, 'error':'Bad request'}

######################   Users   ######################
@app.post('/users')
def users(): #post method to get the userid and add a new user, more secured than get method for login
    data = request.get_json()
    if data['action']=='login':
        with connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("SELECT userid FROM users WHERE username=%(username)s and password=%(password)s;", data)
                    res = cursor.fetchone()
        if res:
            return res
        else:
            return {'code':400, 'error':'Username or password incorrect'}
    elif data['action']=='create':
        with connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("SELECT 1 FROM users WHERE username=%(username)s;", data)
                    res = cursor.fetchone()
                    if res:
                        res = {'code':400, 'error':'Username already taken'}
                    else:
                        cursor.execute("INSERT INTO users(username, password) VALUES(%(username)s, %(password)s) RETURNING *;", data)
                        res = {'code':200, 'success':'Account created'}
                    conn.commit()
        return res

app.run(host="0.0.0.0", port=3001)