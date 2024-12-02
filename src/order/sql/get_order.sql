SELECT MAX(idOrder) as idOrder
FROM Orders
WHERE idWaiter = $e_waiter_id AND ordersDatetime = '$e_order_date';