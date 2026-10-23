-- name: category_performance
SELECT p.ProductCategory,SUM(s.Sales) AS Sales,SUM(s.Profit) AS Profit,
SUM(s.Profit)/NULLIF(SUM(s.Sales),0) AS ProfitMargin,
COUNT(DISTINCT s.OrderID) AS Orders,SUM(s.Profit<0) AS LossLines
FROM fact_sales s JOIN dim_products p ON s.ProductKey=p.ProductKey
GROUP BY p.ProductCategory ORDER BY Sales DESC;
