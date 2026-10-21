# Credit Risk Portfolio Analytics (SQL Window Functions & Markov Roll Rates)

**Author:** Wembley Emmanuel Ibarra Tepato ([github.com/Wembley003](https://github.com/Wembley003))  
**Focus:** Delinquency Transition Matrices (Markov Chains), Vintage Analysis, and Expected Loss ($EL = PD 	imes LGD 	imes EAD$) Decomposition in SQL and Python.

## Overview
Reproducible analytical pipeline using **SQL (`sqlite3`)** and **Python (`pandas`, `numpy`)** to monitor consumer and commercial credit portfolios:
- **Markov Transition Matrices (Roll Rates)**: Uses SQL `LAG() OVER (PARTITION BY loan_id ORDER BY snapshot_month)` and window aggregations to estimate transition probabilities across delinquency buckets (`0_CURRENT`, `1-29 DPD`, `30-59 DPD`, `60-89 DPD`, `90+ DEFAULT`).
- **Expected Loss Decomposition**: Separates Exposure at Default ($EAD$), Probability of Default ($PD$), and Loss Given Default ($LGD$) by risk tier.

```bash
pip install -r requirements.txt
python -m src.portfolio_analytics
pytest -v
```
