SELECT Name AS 'Имя', OrdersCount AS 'Принято заказов', RevenueGenerated AS 'Созданная выручка', 
    EmploymentDate AS 'Дата начала работы', ResignDate AS 'Дата увольнения', PassportData AS 'Паспортные данные', 
    Birthday AS 'Дата рождения'

FROM WaiterWorkReport
WHERE year='$year' AND month='$month';