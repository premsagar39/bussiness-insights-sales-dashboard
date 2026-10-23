-- name: loss_lines
SELECT LineKey,OrderID,ProductName,ProductSubCategory,Region,Sales,Profit,Discount,`Discount Band`
FROM fact_sales WHERE Profit<0 ORDER BY Profit,LineKey;
