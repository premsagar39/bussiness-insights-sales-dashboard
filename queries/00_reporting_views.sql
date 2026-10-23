-- Transform staged rows into the reporting model.
INSERT INTO dim_products
SELECT ROW_NUMBER() OVER(ORDER BY MIN(LineKey)),ProductName,ProductCategory,ProductSubCategory
FROM stg_sales GROUP BY ProductName,ProductCategory,ProductSubCategory;
INSERT INTO dim_dates
WITH RECURSIVE calendar AS (
SELECT MIN(OrderDate) AS d FROM stg_sales
UNION ALL SELECT DATE_ADD(d,INTERVAL 1 DAY) FROM calendar
WHERE d < (SELECT MAX(OrderDate) FROM stg_sales))
SELECT d,DATE_FORMAT(d,'%b'),MONTH(d),DATE_FORMAT(d,'%Y-%m'),YEAR(d) FROM calendar;
INSERT INTO fact_sales
SELECT s.*,p.ProductKey,DATEDIFF(s.ShipDate,s.OrderDate),
CASE WHEN s.Discount=0 THEN 'No discount' WHEN s.Discount<=0.05 THEN '01–05%'
WHEN s.Discount<=0.10 THEN '06–10%' ELSE 'Above 10%' END
FROM stg_sales s JOIN dim_products p ON s.ProductName=p.ProductName
AND s.ProductCategory=p.ProductCategory AND s.ProductSubCategory=p.ProductSubCategory;
CREATE OR REPLACE VIEW vw_powerbi_sales AS SELECT * FROM fact_sales;
CREATE OR REPLACE VIEW vw_powerbi_products AS SELECT * FROM dim_products;
CREATE OR REPLACE VIEW vw_powerbi_dates AS SELECT * FROM dim_dates;
