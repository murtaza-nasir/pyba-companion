"""Per-student seeded datasets for the BSAN 775 exams.

Student-facing use (printed on the exam):

    from pyba import exam
    exam.dataset("a123b456", "midterm")     # writes my_orders.csv etc. next
                                            # to the notebook and returns paths

The grading-side answer key is NOT part of this package; it exists only
in the instructor's private materials and reuses these same perturbation
functions.

Design: a student's WSU ID is hashed to a seed, and the seed drives a
deterministic perturbation of the base Prairie Wholesale data (a subsample
of orders with re-scaled quantities and jittered discounts, and a jittered
customer snapshot). Every student therefore analyzes structurally identical
but numerically distinct data, and every numeric exam answer differs by
student. The answer key recomputes each student's data from the roster and
evaluates the exam questions on it.

The perturbation never touches pw_products.csv, so joins remain valid.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from . import DATA_DIR

EXAMS = ("midterm", "final")


def _seed(student_id: str, exam: str) -> int:
    """Deterministic seed from a student ID; case- and space-insensitive."""
    key = f"pyba-775|{exam}|{student_id.strip().lower()}"
    return int.from_bytes(hashlib.sha256(key.encode()).digest()[:8], "big")


def _perturb_orders(rng: np.random.Generator) -> pd.DataFrame:
    orders = pd.read_csv(DATA_DIR / "pw_orders.csv", parse_dates=["order_date"])

    # one global price level per student (±10%), so summary statistics
    # differ meaningfully between students while every relationship holds
    price_scale = rng.uniform(0.90, 1.10)

    # keep a per-student ~85% subsample of whole orders
    ids = orders["order_id"].unique()
    keep = rng.choice(ids, size=int(len(ids) * 0.85), replace=False)
    sub = orders[orders["order_id"].isin(keep)].copy()
    sub["unit_price"] = (sub["unit_price"] * price_scale).round(2)

    # re-scale quantities per line (small, always >= 1) and jitter discounts
    scale = rng.lognormal(0.0, 0.10, size=len(sub))
    sub["quantity"] = np.maximum(1, (sub["quantity"] * scale).round()).astype(int)
    sub["discount_pct"] = (sub["discount_pct"]
                           + rng.normal(0, 0.005, size=len(sub))).clip(0, 0.30).round(3)
    sub["line_total"] = (sub["quantity"] * sub["unit_price"]
                         * (1 - sub["discount_pct"])).round(2)
    return sub.reset_index(drop=True)


def _perturb_snapshot(rng: np.random.Generator) -> pd.DataFrame:
    snap = pd.read_csv(DATA_DIR / "pw_customer_snapshot.csv")
    snap = snap.sample(frac=0.9, random_state=rng.integers(2**31)).reset_index(drop=True)

    # global scale per student, then per-row jitter
    money_scale = rng.uniform(0.90, 1.10)
    for col in ("revenue_12m", "avg_order_value"):
        snap[col] = snap[col] * money_scale

    jitter = {
        "orders_12m": 0.10, "revenue_12m": 0.08, "avg_order_value": 0.08,
        "tenure_months": 0.05, "weeks_since_last_order": 0.10,
    }
    for col, sd in jitter.items():
        snap[col] = (snap[col] * rng.lognormal(0.0, sd, size=len(snap))).round(2)
    snap["orders_12m"] = snap["orders_12m"].round().astype(int).clip(lower=1)
    return snap


def dataset(student_id: str, exam: str = "midterm", out_dir: str | Path = ".") -> dict:
    """Write this student's exam data next to their notebook; return the paths."""
    if exam not in EXAMS:
        raise ValueError(f"exam must be one of {EXAMS}")
    rng = np.random.default_rng(_seed(student_id, exam))
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    written = {}

    if exam == "midterm":
        orders = _perturb_orders(rng)
        orders.to_csv(out / "my_orders.csv", index=False)
        pd.read_csv(DATA_DIR / "pw_products.csv").to_csv(out / "my_products.csv", index=False)
        pd.read_csv(DATA_DIR / "pw_customers.csv").to_csv(out / "my_customers.csv", index=False)
        written = {k: str(out / f"my_{k}.csv") for k in ("orders", "products", "customers")}
    else:
        snap = _perturb_snapshot(rng)
        snap.to_csv(out / "my_snapshot.csv", index=False)
        orders = _perturb_orders(rng)
        orders.to_csv(out / "my_orders.csv", index=False)
        written = {"snapshot": str(out / "my_snapshot.csv"),
                   "orders": str(out / "my_orders.csv")}

    print(f"Data for {student_id} ({exam}) written:")
    for name, path in written.items():
        print(f"  {name}: {path}")
    return written
