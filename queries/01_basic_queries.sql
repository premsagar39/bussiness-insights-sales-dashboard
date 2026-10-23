-- name: portfolio_kpis
SELECT COUNT(*) AS OrderLines,COUNT(DISTINCT OrderID) AS Orders,
COUNT(DISTINCT CustomerID) AS Customers,SUM(Sales) AS Sales,SUM(Profit) AS Profit,
SUM(Profit)/NULLIF(SUM(Sales),0) AS ProfitMargin,
SUM(Sales)/NULLIF(COUNT(DISTINCT OrderID),0) AS SalesPerOrder,
SUM(Profit<0) AS LossLines,SUM(CASE WHEN Profit<0 THEN -Profit ELSE 0 END) AS LossAmount,
AVG(`Days to Ship`) AS AverageDaysToShip FROM fact_sales;
