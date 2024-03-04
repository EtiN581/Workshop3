CREATE TABLE products(
	productid SERIAL PRIMARY KEY,
	name VARCHAR(20),
	description VARCHAR(200),
	category VARCHAR(50),
	stock_status VARCHAR(15),
	price DECIMAL(10,2)
);

CREATE TABLE users(
	userid SERIAL PRIMARY KEY,
	username VARCHAR(15),
	password VARCHAR(15)
);

CREATE TABLE orders(
	orderid SERIAL PRIMARY KEY,
	userid INT,
	total_price DECIMAL(10,2) DEFAULT 0,
	order_status VARCHAR(10)
);

CREATE TABLE orderdetails(
	orderid INT,
	productid INT,
	quantity INT,
	PRIMARY KEY(orderid, productid)
);

CREATE TABLE cart(
	userid INT PRIMARY KEY,
	total_price DECIMAL(10,2) DEFAULT 0
);

CREATE TABLE cartdetails(
	userid INT,
	productid INT,
	quantity INT,
	PRIMARY KEY (userid, productid)
);

ALTER TABLE orders ADD CONSTRAINT fk_userid FOREIGN KEY(userid) REFERENCES users(userid);
ALTER TABLE orderdetails ADD CONSTRAINT fk_orderid FOREIGN KEY(orderid) REFERENCES orders(orderid);
ALTER TABLE orderdetails ADD CONSTRAINT fk_productid FOREIGN KEY(productid) REFERENCES products(productid);
ALTER TABLE cartdetails ADD CONSTRAINT fk_productid FOREIGN KEY(productid) REFERENCES products(productid);
ALTER TABLE cartdetails ADD CONSTRAINT fk_cartid FOREIGN KEY(userid) REFERENCES cart(userid);

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO db_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO db_user;