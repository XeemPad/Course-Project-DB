UPDATE Orders
SET totalCostRubles = $total_cost
WHERE idOrder = $e_order_id;