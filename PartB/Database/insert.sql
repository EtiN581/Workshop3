INSERT INTO users(username, password) VALUES('test', 'root');
INSERT INTO users(username, password) VALUES('test2', 'root');

INSERT INTO products(name, description, category, stock_status, price) VALUES('prod1', 'desc1', 'cat1', 'in_stock', 10.5);
INSERT INTO products(name, description, category, stock_status, price) VALUES('prod2', 'desc2', 'cat2', 'in_stock', 7.5);
INSERT INTO products(name, description, category, stock_status, price) VALUES('prod3', 'desc3', 'cat3', 'not_in_stock', 7.5);

INSERT INTO orders(userid, order_status) VALUES(1, 'to do');
INSERT INTO orderdetails VALUES(1,1,2);
INSERT INTO orderdetails VALUES(1,2,3);