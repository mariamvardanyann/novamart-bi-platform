USE novamart;
GO

CREATE OR ALTER VIEW dbo.vw_product_sales
AS

WITH line_sales AS (
    SELECT
        oi.order_line_id,
        oi.order_id,
        oi.product_id,
        oi.quantity,

        CAST(
            oi.quantity * oi.unit_price
            - oi.line_discount
            AS decimal(18, 4)
        ) AS sales_revenue

    FROM dbo.order_items oi

    INNER JOIN dbo.orders o
        ON oi.order_id = o.order_id

    WHERE o.status IN ('paid', 'fulfilled', 'shipped', 'delivered')
        AND EXISTS (
            SELECT 1
            FROM dbo.payments p_eligible
            WHERE p_eligible.order_id = o.order_id
              AND p_eligible.payment_status = 'succeeded'
        )
),

order_totals AS (
    SELECT
        order_id,
        SUM(sales_revenue) AS order_sales_revenue

    FROM line_sales

    GROUP BY
        order_id
),

linked_refunds AS (
    SELECT
        rt.order_line_id,

        SUM(rf.refund_amount)
            AS linked_refund_amount

    FROM dbo.refunds rf

    INNER JOIN dbo.returns rt
        ON rf.return_id = rt.return_id

    WHERE rf.return_id IS NOT NULL

    GROUP BY
        rt.order_line_id
),

unlinked_refunds AS (
    SELECT
        order_id,

        SUM(refund_amount)
            AS unlinked_refund_amount

    FROM dbo.refunds

    WHERE return_id IS NULL

    GROUP BY
        order_id
),

unlinked_allocation_base AS (
    SELECT
        ls.order_line_id,
        ls.order_id,

        ur.unlinked_refund_amount,

        ROW_NUMBER() OVER (
            PARTITION BY ls.order_id
            ORDER BY
                ls.sales_revenue DESC,
                ls.order_line_id
        ) AS allocation_row,

        CASE
            WHEN ot.order_sales_revenue <> 0
            THEN
                CAST(
                    ROUND(
                        ur.unlinked_refund_amount
                        * ls.sales_revenue
                        / ot.order_sales_revenue,
                        2
                    )
                    AS decimal(18, 2)
                )
            ELSE 0
        END AS proportional_refund

    FROM line_sales ls

    INNER JOIN order_totals ot
        ON ls.order_id = ot.order_id

    INNER JOIN unlinked_refunds ur
        ON ls.order_id = ur.order_id
),

unlinked_allocations AS (
    SELECT
        order_line_id,
        order_id,

        CASE
            WHEN allocation_row = 1
            THEN
                CAST(
                    unlinked_refund_amount
                    -
                    SUM(
                        CASE
                            WHEN allocation_row <> 1
                            THEN proportional_refund
                            ELSE 0
                        END
                    ) OVER (
                        PARTITION BY order_id
                    )
                    AS decimal(18, 2)
                )

            ELSE proportional_refund
        END AS allocated_unlinked_refund

    FROM unlinked_allocation_base
),

line_financials AS (
    SELECT
        ls.order_line_id,
        ls.order_id,
        ls.product_id,
        ls.quantity,
        ls.sales_revenue,

        CAST(
            ISNULL(lr.linked_refund_amount, 0)
            +
            ISNULL(ua.allocated_unlinked_refund, 0)
            AS decimal(18, 2)
        ) AS refund_amount

    FROM line_sales ls

    LEFT JOIN linked_refunds lr
        ON ls.order_line_id = lr.order_line_id

    LEFT JOIN unlinked_allocations ua
        ON ls.order_line_id = ua.order_line_id
)

SELECT
    p.product_id,
    p.product_name,

    c.category_id,
    c.category_name,

    COUNT(DISTINCT lf.order_id)
        AS order_count,

    SUM(lf.quantity)
        AS units_sold,

    CAST(
        SUM(lf.sales_revenue)
        AS decimal(18, 2)
    ) AS sales_revenue,

    CAST(
        SUM(lf.refund_amount)
        AS decimal(18, 2)
    ) AS refund_amount,

    CAST(
        SUM(
            lf.sales_revenue
            - lf.refund_amount
        )
        AS decimal(18, 2)
    ) AS net_revenue

FROM line_financials lf

INNER JOIN dbo.products p
    ON lf.product_id = p.product_id

INNER JOIN dbo.categories c
    ON p.category_id = c.category_id

GROUP BY
    p.product_id,
    p.product_name,
    c.category_id,
    c.category_name;
GO


SELECT
    SUM(sales_revenue) AS total_sales_revenue,
    SUM(refund_amount) AS total_refunds,
    SUM(net_revenue) AS total_net_revenue
FROM dbo.vw_product_sales;