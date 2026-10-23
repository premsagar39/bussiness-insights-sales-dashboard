-- name: shipping_mode_review
SELECT ShipMode,COUNT(*) AS OrderLines,COUNT(DISTINCT OrderID) AS Orders,AVG(`Days to Ship`) AS AverageDaysToShip,
SUM(ShippingCost) AS ShippingCost,SUM(Profit) AS Profit FROM fact_sales GROUP BY ShipMode ORDER BY OrderLines DESC;
-- name: product_review
SELECT p.ProductKey,p.ProductName,p.ProductCategory,p.ProductSubCategory,
SUM(s.Sales) AS Sales,SUM(s.Profit) AS Profit,COUNT(DISTINCT s.OrderID) AS Orders
FROM fact_sales s JOIN dim_products p ON s.ProductKey=p.ProductKey
GROUP BY p.ProductKey,p.ProductName,p.ProductCategory,p.ProductSubCategory ORDER BY Sales DESC,p.ProductKey LIMIT 25;
