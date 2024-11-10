SELECT idTable as 'Номер стола', idZone as 'Номер зоны', 
       normalSeatsN as 'Общее количество посадочных мест', kidsSeatsN as 'Количество детских мест'
FROM Tables
WHERE idTable = "$table_id";
