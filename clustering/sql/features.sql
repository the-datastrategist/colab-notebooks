-- Visit-level feature table
-- IMPORTANT: aggregate at natural grain before joining

WITH base AS (
  SELECT
    CONCAT(CAST(fullVisitorId AS STRING), '-', CAST(visitId AS STRING)) AS visit_id,
    PARSE_DATE('%Y%m%d', date) AS date_id,
    totals.pageviews AS pageviews,
    totals.hits AS hits,
    totals.timeOnSite AS time_on_site_sec,
    totals.transactions AS transactions,
    totals.transactionRevenue AS transaction_revenue
  FROM `{dataset}.{table_pattern}`
  WHERE _TABLE_SUFFIX >= '{date_from}'
    AND _TABLE_SUFFIX < '{date_to}'
),

pages AS (
  SELECT
    CONCAT(CAST(fullVisitorId AS STRING), '-', CAST(visitId AS STRING)) AS visit_id,
    COUNT(DISTINCT h.page.pagePath) AS unique_pages
  FROM `{dataset}.{table_pattern}`,
       UNNEST(hits) h
  WHERE _TABLE_SUFFIX >= '{date_from}'
    AND _TABLE_SUFFIX < '{date_to}'
  GROUP BY 1
)

SELECT
  b.*,
  p.unique_pages,
  SAFE_DIVIDE(b.time_on_site_sec, NULLIF(b.pageviews, 0)) AS time_on_site_sec_per_pageview,
  SAFE_DIVIDE(b.hits, NULLIF(b.pageviews, 0)) AS hits_per_pageview
FROM base b
LEFT JOIN pages p USING (visit_id);
