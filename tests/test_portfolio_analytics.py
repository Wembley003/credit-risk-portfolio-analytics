import numpy as np
from src.portfolio_analytics import CreditPortfolioAnalytics


def test_markov_transition_probabilities_sum_to_100():
    analytics = CreditPortfolioAnalytics(random_seed=42)
    analytics.generate_synthetic_portfolio(n_loans=300, n_months=5)
    tm = analytics.compute_transition_matrix_sql()
    row_sums = tm.groupby("prev_bucket")["transition_probability_pct"].sum()
    for bucket, total_pct in row_sums.items():
        assert np.isclose(total_pct, 100.0, atol=0.2), f"Row {bucket} summed to {total_pct}"


def test_segment_expected_loss_monotonicity():
    analytics = CreditPortfolioAnalytics(random_seed=42)
    analytics.generate_synthetic_portfolio(n_loans=500, n_months=6)
    seg_df = analytics.compute_segment_expected_loss().set_index("segment")
    assert seg_df.loc["SUBPRIME", "observed_pd_pct"] >= seg_df.loc["PRIME", "observed_pd_pct"]
