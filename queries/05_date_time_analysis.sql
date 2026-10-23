-- name: monthly_performance
SELECT DATE_FORMAT(OrderDate,'%Y-%m') AS YearMonth,SUM(Sales) AS Sales,SUM(Profit) AS Profit,
SUM(Profit)/NULLIF(SUM(Sales),0) AS ProfitMargin,COUNT(DISTINCT OrderID) AS Orders
FROM fact_sales GROUP BY DATE_FORMAT(OrderDate,'%Y-%m') ORDER BY YearMonth;
