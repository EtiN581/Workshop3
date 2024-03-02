from flask import Flask, request, jsonify
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

@app.route('/')
def hello_world():
    return 'hey'

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
        product = {'name':'name', 'description':'desc', 'price':12, 'category':'test', 'stock status':'yay'}
        with connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("INSERT INTO products(name,description,category,stock_status,price) VALUES(%(name)s,%(description)s,%(category)s,%(stock status)s,%(price)s)", product)
                cursor.execute("SELECT * FROM products WHERE name=%(name)s", product)
                product = cursor.fetchall()
                conn.commit()        
        return product
    else:
        return 'error wrong request method'


@app.route('/products/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def routeProductsId(id):
    if request.method == 'GET':
        data = SQLquery("SELECT * FROM products WHERE productid=%s", id)
        if len(data)!=0:
            return data[0]
        else:
            return {'code':404, 'error':'Product not found'}
    elif request.method == 'PUT':
        s=""
        for key,value in request.args.to_dict().items():
            s+=f"{key}={value}," if isinstance(value, int) or isinstance(value, float) else f"{key}='{value}',"
        try:
            with connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("UPDATE products SET "+s[:-1]+" WHERE productid=%s", id)
                    cursor.execute("SELECT * FROM products WHERE productid=%s", id)
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
                    cursor.execute("DELETE FROM orderdetails WHERE productid=%s", id)
                    cursor.execute("DELETE FROM cartdetails WHERE productid=%s", id)
                    cursor.execute("DELETE FROM products WHERE productid=%s", id)
                    product = cursor.fetchone()
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
    data=request.args.to_dict()
    try:
        with connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("INSERT INTO orders(userid, order_status) VALUES(%(userid)s, %(order status)s) RETURNING orderid;", data)
                orderid = cursor.fetchone()['orderid']
                for i in len(data['products']):
                    cursor.execute("INSERT INTO orderdetails VALUES(%s, %s, %s);", orderid, data['product'][i], data['quantity'][i],)
                ##instead of listing with productid, list with product.name##
                cursor.execute("SELECT o.orderid, string_agg(p.name::varchar ||':'|| od.quantity::varchar, ', ') AS list_products, o.total_price, o.order_status FROM orders o JOIN orderdetails od ON o.orderid=od.orderid JOIN products p ON p.productid=od.productid WHERE  o.orderid=%s;", orderid)
                data = cursor.fetchone()
                conn.commit()
        return data
    except Exception as e:
        print(e)
        return {'code':400, 'error':'Bad request'}


@app.get('/orders/<int:userid>')
def getOrdersId(userid):
    try:
        data = SQLquery("SELECT o.orderid, string_agg(p.name::varchar ||':'|| od.quantity::varchar, ', ') AS list_products, o.total_price, o.order_status FROM orders o JOIN orderdetails od ON o.orderid=od.orderid JOIN products p ON p.productid=od.productid WHERE userid=%s GROUP BY o.orderid;", userid)
        return data
    except:
        return {'code':404, 'error':'ID user not found'}


####################      /CART/       #########################
@app.route('/cart/<int:userid>', methods=['GET', 'POST'])
def routeCartUserId(userid):
    if request.method == 'GET':
        try:
            data = SQLquery("SELECT c.cartid, string_agg(cd.productid::varchar ||':'|| cd.quantity::varchar, ', ') AS list_products, c.total_price FROM cart c JOIN cartdetails cd ON c.cartid=cd.cartid WHERE userid=%s GROUP BY c.cartid;", userid)
            return data
        except Exception as e:
            print(e)
            return {'code':404, 'error':'Not Found'}
    elif request.method == 'POST':
        data=request.args.to_dict()
        try:#todo
            with connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("INSERT INTO cart(userid) VALUES(%(userid)s) RETURNING cartid;", data)
                    cartid = cursor.fetchone()['cartid']
                    for i in len(data['products']):
                        cursor.execute("INSERT INTO cartdetails VALUES(%s, %s, %s);", cartid, data['product'][i], data['quantity'][i],)
                    ##instead of listing with productid, list with product.name##
                    cursor.execute("SELECT c.cartid, string_agg(p.name::varchar ||':'|| cd.quantity::varchar, ', ') AS list_products, c.total_price FROM cart c JOIN cartdetails cd ON c.cartid=cd.cartid JOIN products p ON p.productid=cd.productid WHERE c.cartid=%s;", cartid)
                    data = cursor.fetchone()
                    conn.commit()
            return data
        except Exception as e:
            print(e)
            return {'code':400, 'error':'Bad request'}
    else:
        return {'code':405, 'error':'Method Not Allowed'}


@app.route('/cart/<int:userid>/item/<int:productid>')
def deleteCartProduct(userid, productid):
    try:
        with connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("DELETE FROM cartdetails cd WHERE cd.productid=%s AND cd.cartid IN (SELECT cartid FROM cart WHERE userid=%s);", productid, userid)
                cursor.execute("SELECT c.cartid, string_agg(cd.productid::varchar ||':'|| cd.quantity::varchar, ', ') AS list_products, c.total_price FROM cart c JOIN cartdetails cd ON c.cartid=cd.cartid WHERE userid=%s GROUP BY c.cartid;", userid)
                data = cursor.fetchall()
                conn.commit()
        return data
    except Exception as e:
        print(e)
        return {'code':400, 'error':'Bad request'}

@app.route('/test/<int:id>', methods=['GET'])
def test(id=None):

    pass
    
app.run(host="0.0.0.0", port=3001)