USE novamart;
GO

CREATE OR ALTER VIEW dbo.vw_customer_retention
AS

SELECT
    acquisition_month,

    COUNT(*) AS acquired_customers,

    SUM(
        CASE
            WHEN is_retained_next_month = 1
            THEN 1
            ELSE 0
        END
    ) AS retained_next_month,

    CAST(
        SUM(
            CASE
                WHEN is_retained_next_month = 1
                THEN 1
                ELSE 0
            END
        ) * 100.0
        / NULLIF(COUNT(*), 0)
        AS decimal(10,2)
    ) AS retention_rate_pct

FROM dbo.customer_cohorts

GROUP BY
    acquisition_month;
GO

SELECT *
FROM dbo.vw_customer_retention
ORDER BY acquisition_month;