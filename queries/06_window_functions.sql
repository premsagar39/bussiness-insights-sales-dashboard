-- name: cumulative_monthly_sales
WITH monthly AS (SELECT DATE_FORMAT(OrderDate,'%Y-%m') AS YearMonth,SUM(Sales) AS Sales
FROM fact_sales GROUP BY DATE_FORMAT(OrderDate,'%Y-%m'))
SELECT YearMonth,Sales,SUM(Sales) OVER(ORDER BY YearMonth ROWS UNBOUNDED PRECEDING) AS CumulativeSales
FROM monthly ORDER BY YearMonth;
