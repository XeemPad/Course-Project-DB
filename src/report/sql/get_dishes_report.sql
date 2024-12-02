SELECT dishName AS 'Название блюда', monthlyOrders AS 'Количество заказов',
    monthlyRevenue AS 'Выручка от блюда'

FROM DishPopularityReport
WHERE year='$year' AND month='$month';