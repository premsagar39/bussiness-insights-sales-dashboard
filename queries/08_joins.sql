-- name: region_customer_segment
SELECT s.Region,s.CustomerSegment,COUNT(DISTINCT s.CustomerID) AS Customers,
COUNT(DISTINCT s.OrderID) AS Orders,SUM(s.Sales) AS Sales,SUM(s.Profit) AS Profit,
AVG(s.`Days to Ship`) AS AverageDaysToShip
FROM fact_sales s JOIN dim_products p ON s.ProductKey=p.ProductKey JOIN dim_dates d ON s.OrderDate=d.Date
GROUP BY s.Region,s.CustomerSegment ORDER BY s.Region,s.CustomerSegment;
-- name: join_reconciliation
SELECT (SELECT COUNT(*) FROM stg_sales) AS SourceLines,COUNT(*) AS JoinedLines,SUM(s.Sales) AS Sales,SUM(s.Profit) AS Profit
FROM fact_sales s JOIN dim_products p ON s.ProductKey=p.ProductKey JOIN dim_dates d ON s.OrderDate=d.Date;
