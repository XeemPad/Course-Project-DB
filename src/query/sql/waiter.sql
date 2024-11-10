SELECT idWaiter as 'id Официанта', Name as 'Имя', 
    Birthday as 'День рождения', PassportData as 'Паспортные данные', 
    EmploymentDate as 'Дата устройства на работу', ResignDate as 'Дата увольнения'
FROM Waiters
WHERE Name LIKE "%${waiter_name}%";
