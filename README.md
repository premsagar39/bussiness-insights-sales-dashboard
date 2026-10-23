# Superstore Sales Insights

Power BI analysis of 1,952 order lines from January–June 2015. The report connects sales performance, margin diagnostics and customer/shipping patterns using one filter-aware model.

![Sales overview](bussines%20sales%20insight%20dashboard.png)

## Findings
- Recorded sales: **$1,924,337.88**; profit: **$224,077.61**; margin: **11.64%**.
- **1,365 distinct orders** from **1,130 customers**. Order lines are counted separately.
- **956 lines (48.98%)** have negative profit, despite a positive overall margin. Review these by subcategory and discount band before proposing pricing changes.
- Average elapsed time from order date to ship date: **1.94 days**. This measures dispatch timing; delivery dates and promised service levels are not available.

## Explore
- **Sales overview:** monthly sales/margin combo, category profit waterfall, region comparisons and dynamic Top 8 subcategories.
- **Margin diagnostics:** discount/margin scatter with sales-sized bubbles, loss measures and a subcategory review table.
- **Customers & shipping:** within-sample repeat customers, shipping times, cumulative sales and a region/segment matrix.
- Hover over charts for a contextual report-page tooltip. Right-click a subcategory and choose **Drill through → Subcategory Detail** for the order-line view. Navigation and reset buttons are included. In Power BI Desktop, Ctrl+click action buttons.

## Files
- [Power BI report](bussiness%20sales%20insights%20dashboard.pbix)
- [Editable Power BI project and prepared data](powerbi-source.zip)
- [DAX measures](measures.dax) · [Report theme](theme.json)
- Existing [MySQL analysis](queries) and [source dataset](dataset) remain available.

The source package contains the PBIP report definition, semantic model, prepared CSV snapshots, a Python preparation script and SQLite reconciliation queries. The report uses embedded snapshots, so opening or refreshing it does not require a local MySQL connection. The existing MySQL scripts are a separate analysis route.

## Definitions and checks
Profit margin is total profit divided by total sales. Average discount is a line-weighted arithmetic mean. Repeat customers have more than one distinct order within this six-month sample; this is not lifetime retention. Discount and shipping comparisons are descriptive.

The CSV and Excel sources reconcile on row count, sales and profit. A separate LineKey preserves all records because the source has 1,951 distinct RowID values across 1,952 lines. Sixteen missing base-margin values remain blank; recorded profit is not reconstructed from them. Only January–June 2015 is present, so the report does not claim a full-year result or year-over-year growth.
