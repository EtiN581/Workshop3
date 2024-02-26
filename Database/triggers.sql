CREATE OR REPLACE FUNCTION orders_total_price()
RETURNS TRIGGER AS
$$
BEGIN
    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
        UPDATE orders 
        SET total_price = (
            SELECT SUM(p.price * o.quantity) 
            FROM orderdetails o 
            JOIN products p ON o.productid = p.productid 
            WHERE o.orderid = NEW.orderid
        )
        WHERE orderid = NEW.orderid;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE orders 
        SET total_price = (
            SELECT SUM(p.price * o.quantity) 
            FROM orderdetails o 
            JOIN products p ON o.productid = p.productid 
            WHERE o.orderid = OLD.orderid
        )
        WHERE orderid = OLD.orderid;
    END IF;
    RETURN NEW;
END;
$$
LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER orders_total_price
AFTER INSERT OR UPDATE OR DELETE
ON orderdetails
FOR EACH ROW
EXECUTE FUNCTION orders_total_price();

CREATE OR REPLACE FUNCTION cart_total_price()
RETURNS TRIGGER AS
$$
BEGIN
    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
        UPDATE cart 
        SET total_price = (
            SELECT SUM(p.price * c.quantity) 
            FROM cartdetails c 
            JOIN products p ON c.productid = p.productid 
            WHERE c.cartid = NEW.cartid
        )
        WHERE cartid = NEW.cartid;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE cart
        SET total_price = (
            SELECT SUM(p.price * c.quantity) 
            FROM cartdetails c 
            JOIN products p ON c.productid = p.productid 
            WHERE c.cartid = OLD.cartid
        )
        WHERE cartid = OLD.cartid;
    END IF;
    RETURN NEW;
END;
$$
LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER cart_total_price
AFTER INSERT OR UPDATE OR DELETE
ON cartdetails
FOR EACH ROW
EXECUTE FUNCTION cart_total_price();