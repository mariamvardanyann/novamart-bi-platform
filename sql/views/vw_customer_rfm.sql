USE novamart;
GO

CREATE OR ALTER VIEW dbo.vw_customer_rfm
AS
WITH order_sales AS (
    SELECT
        o.order_id,
        o.customer_id,
        o.order_timestamp,
        SUM(oi.quantity * oi.unit_price - oi.line_discount) AS sales_revenue
    FROM dbo.orders o
    INNER JOIN dbo.order_items oi
        ON o.order_id = oi.order_id
    WHERE
        o.status IN ('paid', 'fulfilled', 'shipped', 'delivered')
        AND EXISTS (
            SELECT 1
            FROM dbo.payments p_eligible
            WHERE p_eligible.order_id = o.order_id
              AND p_eligible.payment_status = 'succeeded'
        )
        AND o.customer_id IS NOT NULL
    GROUP BY
        o.order_id,
        o.customer_id,
        o.order_timestamp
),
order_refunds AS (
    SELECT
        r.order_id,
        SUM(r.refund_amount) AS refund_amount
    FROM dbo.refunds r
    GROUP BY r.order_id
),
customer_metrics AS (
    SELECT
        os.customer_id,
        DATEDIFF(
            DAY,
            MAX(os.order_timestamp),
            (
                SELECT MAX(o2.order_timestamp)
                FROM dbo.orders o2
                WHERE o2.status IN ('paid', 'fulfilled', 'shipped', 'delivered')
                  AND EXISTS (
                      SELECT 1 FROM dbo.payments p2
                      WHERE p2.order_id = o2.order_id
                        AND p2.payment_status = 'succeeded'
                  )
            )
        ) AS recency_days,
        COUNT(DISTINCT os.order_id) AS frequency,
        SUM(os.sales_revenue - ISNULL(rf.refund_amount, 0)) AS monetary_value
    FROM order_sales os
    LEFT JOIN order_refunds rf
        ON os.order_id = rf.order_id
    GROUP BY os.customer_id
),
rfm_scores AS (
    SELECT
        customer_id,
        recency_days,
        frequency,
        monetary_value,
        6 - NTILE(5) OVER (ORDER BY recency_days ASC) AS recency_score,
        NTILE(5) OVER (ORDER BY frequency ASC) AS frequency_score,
        NTILE(5) OVER (ORDER BY monetary_value ASC) AS monetary_score
    FROM customer_metrics
)
SELECT
    customer_id,
    recency_days,
    frequency,
    monetary_value,
    recency_score,
    frequency_score,
    monetary_score,
    recency_score + frequency_score + monetary_score AS rfm_score,
    CONCAT(recency_score, frequency_score, monetary_score) AS rfm_code
FROM rfm_scores;
GO

SELECT TOP 20 *
FROM dbo.vw_customer_rfm
ORDER BY
    rfm_score DESC,
    recency_score DESC,
    frequency_score DESC,
    monetary_score DESC;
