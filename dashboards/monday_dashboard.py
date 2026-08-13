"""The Monday-morning dashboard from Chapter 6.

Run from the repository root:

    streamlit run dashboards/monday_dashboard.py

Every element is built from the same pandas and Plotly calls the chapters
teach. Streamlit reruns this script top to bottom whenever a control
changes; there is no other machinery.
"""
import pandas as pd
import plotly.express as px
import streamlit as st

from pyba import DATA_DIR

st.set_page_config(page_title="Prairie Wholesale - Monday morning", layout="wide")


@st.cache_data  # load once, not on every interaction
def load_lines():
    orders = pd.read_csv(DATA_DIR / "pw_orders.csv", parse_dates=["order_date"])
    products = pd.read_csv(DATA_DIR / "pw_products.csv")
    customers = pd.read_csv(DATA_DIR / "pw_customers.csv")
    product_cols = products[["sku", "product_name", "category", "unit_cost"]]
    lines = orders.merge(product_cols, on="sku", how="left", validate="many_to_one")
    lines = lines.merge(customers[["customer_id", "region", "business_type"]],
                        on="customer_id", how="left", validate="many_to_one")
    lines["margin_dollars"] = lines["line_total"] - lines["quantity"] * lines["unit_cost"]
    return lines


lines = load_lines()

# ---- global filters (sidebar) ----
st.sidebar.header("Filters")
regions = st.sidebar.multiselect("Region", sorted(lines["region"].unique()))
start, end = st.sidebar.slider(
    "Date range",
    min_value=lines["order_date"].min().date(),
    max_value=lines["order_date"].max().date(),
    value=(lines["order_date"].min().date(), lines["order_date"].max().date()),
)

view = lines[(lines["order_date"].dt.date >= start) & (lines["order_date"].dt.date <= end)]
if regions:
    view = view[view["region"].isin(regions)]

# ---- KPI row ----
st.title("Prairie Wholesale Supply")
k1, k2, k3 = st.columns(3)
k1.metric("Revenue", f"${view['line_total'].sum():,.0f}")
k2.metric("Margin", f"${view['margin_dollars'].sum():,.0f}")
k3.metric("Orders", f"{view['order_id'].nunique():,}")

# ---- revenue over time ----
monthly = view.set_index("order_date")["line_total"].resample("ME").sum().reset_index()
st.plotly_chart(
    px.line(monthly, x="order_date", y="line_total",
            labels={"order_date": "", "line_total": "Monthly revenue ($)"}),
    use_container_width=True)

# ---- category x region ----
by_cat = (view.groupby(["region", "category"], as_index=False)["line_total"].sum()
          .sort_values("line_total", ascending=False))
st.plotly_chart(
    px.bar(by_cat, x="line_total", y="category", color="region", orientation="h",
           labels={"line_total": "Revenue ($)", "category": ""}),
    use_container_width=True)
