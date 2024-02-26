--select * from products where name='name';
--delete from products where name='name'
INSERT INTO products(name,description,category,stock_status,price) VALUES('test1','desc','cat1','yay',10) RETURNING productid;
INSERT INTO products(name,description,category,stock_status,price) VALUES('test2','desc','cat2','yay',12.5) RETURNING productid;
INSERT INTO users(firstname,lastname) VALUES('Etienne', 'Goury') RETURNING userid;
INSERT INTO orders(userid,order_status) VALUES(1,'yay');
INSERT INTO orderdetails VALUES(1,1,2);
INSERT INTO orderdetails VALUES(1,2,4);
--SELECT * FROM orders o JOIN orderdetails od ON o.orderid=od.orderid WHERE o.userid=1 GROUP BY o.orderid;
--order ID, list of products ordered with quantities, total price, and order status.
INSERT INTO cart(userid) VALUES(1);
INSERT INTO cartdetails VALUES(1,1,10);
insert into users(firstname, lastname) values('e','g');