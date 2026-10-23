-- name: repeat_customers
SELECT CustomerID,COUNT(DISTINCT OrderID) AS Orders,SUM(Sales) AS Sales
FROM fact_sales GROUP BY CustomerID HAVING COUNT(DISTINCT OrderID)>1 ORDER BY Sales DESC,CustomerID;
-- name: customer_summary
SELECT COUNT(*) AS Customers,SUM(Orders>1) AS RepeatCustomers,SUM(Orders>1)/COUNT(*) AS RepeatCustomerShare
FROM (SELECT CustomerID,COUNT(DISTINCT OrderID) AS Orders FROM fact_sales GROUP BY CustomerID) c;
