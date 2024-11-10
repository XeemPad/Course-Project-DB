SELECT idDish as 'id Блюда', dishName as 'Название блюда', 
       priceInRubles as 'Цена в рублях', weightInGramms as 'Вес, г'
FROM Menu
WHERE dishName LIKE "%${dish_name}%";
