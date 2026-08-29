"""Lab 6 starter: your extension of the Monday-morning dashboard.

This is a copy of dashboards/monday_dashboard.py with the four lab tasks marked
as TODO in the places where the code belongs. Everything already here is
working; you are adding to it, not repairing it.

Run it from the repository root:

    streamlit run dashboards/lab_6_dashboard_starter.py

Streamlit reruns this script top to bottom whenever a control changes, so a
filter added to the sidebar takes effect everywhere below it without any
callback or refresh logic.

The lab prompt is at the end of Chapter 6, under Exercises. Submit this script
together with a screenshot of the running dashboard.
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

# TODO (task 1): add a channel filter.
# The region filter above is the model to copy: a st.sidebar.multiselect over
# sorted(lines["channel"].unique()), assigned to a variable named `channels`.

view = lines[(lines["order_date"].dt.date >= start) & (lines["order_date"].dt.date <= end)]
if regions:
    view = view[view["region"].isin(regions)]

# TODO (task 1, second half): apply the channel filter to `view`, the same way
# the region filter is applied on the line above. An empty selection means "no
# filter", which is why each block is guarded by `if`.

# ---- KPI row ----
st.title("Prairie Wholesale Supply")

# TODO (task 2): add a fourth KPI, the median order total for the current view.
# Change st.columns(3) to st.columns(4) and unpack a fourth column.
#
# The median is of ORDER totals, not of line totals, so aggregate to the order
# level first. The chapters do this with
#     view.groupby("order_id")["line_total"].sum().median()
# Label it so that a reader knows it is a median rather than a mean: "Median
# order", not "Order total". An unlabeled median invites the wrong comparison
# against the revenue figure beside it.
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

# TODO (task 3): add one chart of your own choosing.
#
# Start from the question, not the chart type. Write the question down as a
# comment here, then choose the chart that answers it. The chapter's design
# section argues that a dashboard showing everything communicates nothing, so a
# chart that answers a stated question beats an extra chart that merely fits.
#
# Name the aggregation in the axis label. "Revenue ($)" leaves a reader guessing
# whether that is a sum or an average; "Total revenue ($)" does not. Build it
# from `view` so that it responds to the sidebar filters like the two above.
#
# My question:

# ---- task 4: the ten-second test ----
# Not code. Show the running dashboard to another person for ten seconds, then
# ask what they think the headline is. Record their answer and whether it
# matched what you intended. If it did not, make one change in response, run the
# test again, and report whether the second answer improved.
#
# Write your answers in the submission, in at most three sentences.
