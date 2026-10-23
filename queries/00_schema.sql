CREATE TABLE stg_sales (
LineKey INT PRIMARY KEY,RowID INT NOT NULL,OrderPriority VARCHAR(80),
Discount DECIMAL(12,8),UnitPrice DECIMAL(20,8),ShippingCost DECIMAL(20,8),
CustomerID INT,CustomerName VARCHAR(200),ShipMode VARCHAR(80),CustomerSegment VARCHAR(80),
ProductCategory VARCHAR(100),ProductSubCategory VARCHAR(200),ProductContainer VARCHAR(100),
ProductName VARCHAR(500),ProductBaseMargin DECIMAL(12,8) NULL,Country VARCHAR(100),Region VARCHAR(100),
StateorProvince VARCHAR(150),City VARCHAR(150),PostalCode VARCHAR(30),OrderDate DATE,ShipDate DATE,
Profit DECIMAL(24,10),Quantityorderednew INT,Sales DECIMAL(24,8),OrderID INT,
INDEX ix_order(OrderID),INDEX ix_date(OrderDate),INDEX ix_customer(CustomerID)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;
CREATE TABLE dim_products(ProductKey INT PRIMARY KEY,ProductName VARCHAR(500),
ProductCategory VARCHAR(100),ProductSubCategory VARCHAR(200)) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;
CREATE TABLE dim_dates(Date DATE PRIMARY KEY,Month VARCHAR(3),`Month Number` INT,`Year Month` VARCHAR(7),Year INT);
CREATE TABLE fact_sales LIKE stg_sales;
ALTER TABLE fact_sales ADD ProductKey INT NOT NULL,ADD `Days to Ship` INT,ADD `Discount Band` VARCHAR(30),
ADD CONSTRAINT fk_sales_product FOREIGN KEY(ProductKey) REFERENCES dim_products(ProductKey),
ADD CONSTRAINT fk_sales_date FOREIGN KEY(OrderDate) REFERENCES dim_dates(Date);
