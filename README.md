# Superstore Sales Insights
Python + MySQL 8 + Power BI analysis of sales, margin and customer/shipping performance.

![Sales overview](bussines%20sales%20insight%20dashboard.png)

## Workflow
1. **Python / pandas:** read the supplied CSV, trim text, parse dates, check required fields and add a unique line key.
2. **MySQL 8:** load staging rows, build product/date dimensions, join the sales fact, calculate shipping days and discount bands, and execute 13 analysis queries.
3. **Power BI:** import the three SQL-view exports and use 22 DAX measures for interactive analysis. The saved report embeds those exports for portable viewing.

The Python pipeline connects to MySQL and executes the SQL files. MySQL is required to rebuild the data. Opening the saved PBIX uses the last verified SQL snapshot.

## Findings
- **$1,924,337.88 sales**, **$224,077.61 profit**, **11.64% margin**.
- **1,365 distinct orders**, **1,130 customers**, **1,952 order lines**.
- **956 negative-profit lines (48.98%)** warrant subcategory and discount-band review.
- Average order-to-ship time: **1.94 days**.

## Dashboard
Three pages cover sales overview, margin diagnostics, and customers/shipping. Visuals include a sales/margin combo, profit waterfall, discount/margin scatter, cumulative sales and dynamic rankings. Hover for report-page tooltips; right-click a subcategory for **Drill through → Subcategory Detail**. Ctrl+click action buttons in Power BI Desktop.

## Files
- [Power BI dashboard](bussiness%20sales%20insights%20dashboard.pbix)
- [Editable Power BI source and complete pipeline](powerbi-source.zip)
- [Python pipeline](src/run_pipeline.py) · [MySQL schema and queries](queries)
- [Executed SQL results](reports/sql_results) · [Run and reconciliation checks](reports/pipeline_run.json)
- [DAX measures](measures.dax) · [Theme](theme.json) · [Source dataset](dataset)

## Reproduce
Requires Python 3.10+, MySQL 8 and an account that can create a dedicated project database.

    python -m pip install -r requirements.txt
    python -m zipfile -e powerbi-source.zip powerbi-source
    python src/run_pipeline.py --mysql-user root

The last command prompts for the MySQL password. Host, port, user and database can be supplied as command options or MYSQL_HOST, MYSQL_PORT, MYSQL_USER and MYSQL_DATABASE environment variables; MYSQL_PASSWORD is optional. Do not commit credentials. Use a dedicated schema: the pipeline rebuilds only its own tagged project tables and refuses an unrelated existing schema.

Open powerbi-source/Superstore_Sales_Insights.pbip, select **Refresh**, then **File → Save as → Power BI file (.pbix)**. The extracted source also runs independently with its included dataset, queries and Python script.

## Validation and definitions
Executed on **MySQL 8.0.46**: 13 analysis queries, three Power BI exports and 12 passing reconciliation checks. Python and SQL agree on record/order/customer counts, sales, profit, missing margins, shipping days, discount bands, running totals and join coverage.

The sample covers **January–June 2015**. Order lines are distinct from orders. Source RowID repeats once, so LineKey preserves all 1,952 records. Sixteen missing base-margin values remain blank; recorded profit is retained. Repeat-customer share describes this six-month sample. Shipping days measure dispatch timing. Discount comparisons are descriptive.
