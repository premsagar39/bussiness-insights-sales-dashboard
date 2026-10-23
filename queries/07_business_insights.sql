-- name: subcategory_diagnostics
WITH grouped AS (SELECT ProductSubCategory,SUM(Sales) AS Sales,SUM(Profit) AS Profit,
SUM(Profit)/NULLIF(SUM(Sales),0) AS ProfitMargin,
SUM(CASE WHEN Profit<0 THEN -Profit ELSE 0 END) AS LossAmount,
AVG(Discount) AS AverageDiscount,COUNT(DISTINCT OrderID) AS Orders
FROM fact_sales GROUP BY ProductSubCategory)
SELECT *,DENSE_RANK() OVER(ORDER BY Sales DESC) AS SalesRank FROM grouped ORDER BY SalesRank;
-- name: discount_band_performance
SELECT `Discount Band` AS DiscountBand,COUNT(*) AS OrderLines,SUM(Sales) AS Sales,SUM(Profit) AS Profit
FROM fact_sales GROUP BY `Discount Band` ORDER BY Sales DESC;
