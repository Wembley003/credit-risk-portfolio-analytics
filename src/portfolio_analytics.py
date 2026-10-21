"""
Credit Risk Portfolio Analytics: SQL Window Functions, Markov Roll-Rate Matrices & Vintage Analysis.
Author: Wembley Emmanuel Ibarra Tepato
"""
import sqlite3
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict


class CreditPortfolioAnalytics:
    def __init__(self, random_seed: int = 42):
        self.rng = np.random.default_rng(random_seed)
        self.conn = sqlite3.connect(":memory:")

    def generate_synthetic_portfolio(self, n_loans: int = 400, n_months: int = 6) -> pd.DataFrame:
        segments = ["PRIME", "NEAR_PRIME", "SUBPRIME"]
        cohorts = ["2026-01", "2026-02", "2026-03"]
        records = []

        for loan_id in range(1, n_loans + 1):
            seg = str(self.rng.choice(segments, p=[0.50, 0.35, 0.15]))
            cohort = str(self.rng.choice(cohorts))
            ead = float(self.rng.uniform(15000, 180000))
            lgd = 0.35 if seg == "PRIME" else (0.50 if seg == "NEAR_PRIME" else 0.65)
            dpd = 0

            for m in range(1, n_months + 1):
                if m > 1:
                    Cure_prob = 0.30 if dpd in (15, 45) else 0.05
                    worsen_prob = 0.04 if seg == "PRIME" else (0.10 if seg == "NEAR_PRIME" else 0.22)
                    u = self.rng.random()
                    if dpd > 0 and u < Cure_prob:
                        dpd = 0
                    elif u > (1.0 - worsen_prob):
                        dpd = min(dpd + 30, 120)

                records.append({
                    "loan_id": loan_id,
                    "segment": seg,
                    "origination_cohort": cohort,
                    "snapshot_month": m,
                    "ead_mxn": round(ead, 2),
                    "lgd_rate": lgd,
                    "dpd": int(dpd),
                })

        df = pd.DataFrame(records)
        df.to_sql("loan_snapshots", self.conn, index=False, if_exists="replace")
        return df

    def compute_transition_matrix_sql(self) -> pd.DataFrame:
        sql_path = Path(__file__).resolve().parent.parent / "sql" / "portfolio_analytics_queries.sql"
        query = sql_path.read_text(encoding="utf-8")
        return pd.read_sql_query(query, self.conn)

    def compute_segment_expected_loss(self) -> pd.DataFrame:
        query = """
        WITH latest_snapshot AS (
            SELECT
                *,
                ROW_NUMBER() OVER (PARTITION BY loan_id ORDER BY snapshot_month DESC) AS rn
            FROM loan_snapshots
        )
        SELECT
            segment,
            COUNT(*) AS active_loans,
            ROUND(SUM(ead_mxn), 2) AS total_ead_mxn,
            ROUND(100.0 * AVG(CASE WHEN dpd >= 90 THEN 1.0 ELSE 0.0 END), 2) AS observed_pd_pct,
            ROUND(100.0 * AVG(lgd_rate), 2) AS avg_lgd_pct,
            ROUND(SUM(ead_mxn * (CASE WHEN dpd >= 30 THEN 0.35 ELSE 0.03 END) * lgd_rate), 2) AS expected_loss_mxn
        FROM latest_snapshot
        WHERE rn = 1
        GROUP BY segment
        ORDER BY total_ead_mxn DESC;
        """
        return pd.read_sql_query(query, self.conn)


if __name__ == "__main__":
    analytics = CreditPortfolioAnalytics(random_seed=42)
    analytics.generate_synthetic_portfolio()
    print("=== TRANSITION MATRIX (ROLL RATES) ===")
    print(analytics.compute_transition_matrix_sql().to_string(index=False))
    print("\n=== EXPECTED LOSS BY SEGMENT ===")
    print(analytics.compute_segment_expected_loss().to_string(index=False))
