"""Support package for *Python for Business Analytics*.

Deliberately tiny. The course teaches pandas, Plotly, scikit-learn,
statsmodels, and PuLP directly; nothing here wraps or hides them. The
package holds only:

- DATA_DIR: an absolute path to the bundled datasets, so a plain
  pd.read_csv(DATA_DIR / "pw_orders.csv") works from Jupyter, a Quarto
  render, or the terminal alike.
- pyba.exam: the per-student seeded exam dataset generator.
"""
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "assets" / "data"
