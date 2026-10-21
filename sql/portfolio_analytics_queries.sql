-- Credit Risk Portfolio Analytics: Delinquency Transition Matrix (Roll Rates) & Vintage Analysis
-- Author: Wembley Emmanuel Ibarra Tepato (github.com/Wembley003)

WITH monthly_buckets AS (
    SELECT
        loan_id,
        segment,
        origination_cohort,
        snapshot_month,
        ead_mxn,
        lgd_rate,
        dpd,
        CASE
            WHEN dpd = 0 THEN '0_CURRENT'
            WHEN dpd BETWEEN 1 AND 29 THEN '1_DPD_1_29'
            WHEN dpd BETWEEN 30 AND 59 THEN '2_DPD_30_59'
            WHEN dpd BETWEEN 60 AND 89 THEN '3_DPD_60_89'
            ELSE '4_DEFAULT_90_PLUS'
        END AS current_bucket
    FROM loan_snapshots
),
lagged_transitions AS (
    SELECT
        loan_id,
        segment,
        origination_cohort,
        snapshot_month,
        ead_mxn,
        lgd_rate,
        LAG(current_bucket) OVER (PARTITION BY loan_id ORDER BY snapshot_month) AS prev_bucket,
        current_bucket
    FROM monthly_buckets
)
SELECT
    prev_bucket,
    current_bucket,
    COUNT(*) AS loan_count,
    ROUND(SUM(ead_mxn), 2) AS transitioned_ead_mxn,
    ROUND(
        100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY prev_bucket),
        2
    ) AS transition_probability_pct
FROM lagged_transitions
WHERE prev_bucket IS NOT NULL
GROUP BY prev_bucket, current_bucket
ORDER BY prev_bucket, current_bucket;
