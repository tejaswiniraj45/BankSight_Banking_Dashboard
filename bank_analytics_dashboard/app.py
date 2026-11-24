import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="BankSight | Analytics", page_icon="🏦", layout="wide")
st.markdown("""
<style>
/* Main dashboard background */
.stApp {
    background-color: #f5f7fb;
    color: #142b4a;
}

/* Main headings */
h1, h2, h3 {
    color: #142b4a !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #eaf0f8;
}

/* Sidebar text */
section[data-testid="stSidebar"] * {
    color: #142b4a;
}

/* KPI cards */
[data-testid="stMetric"] {
    background-color: #ffffff;
    padding: 20px;
    border-radius: 14px;
    border: 1px solid #dce5f0;
    box-shadow: 0 3px 10px rgba(0,0,0,0.05);
}

/* KPI text */
[data-testid="stMetric"] label,
[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #142b4a !important;
}

/* Tabs */
button[data-baseweb="tab"] {
    color: #142b4a !important;
    font-weight: 600;
}

/* General text */
p, label, span {
    color: #263b55;
}
</style>
""", unsafe_allow_html=True)

st.title("🏦 BankSight")
st.caption("Banking performance • Transactions • Customer accounts • Income patterns")
DATA = Path(__file__).parent / "data"

@st.cache_data
def load_csv(path):
    return pd.read_csv(path)

def locate_file(candidates):
    for name in candidates:
        p = DATA / name
        if p.exists():
            return p
    return None

customer_path = locate_file(["customer_data.csv", "synthetic_customer_data.csv", "customers.csv"])
transaction_path = locate_file(["transaction_data.csv", "synthetic_transaction_data.csv", "transactions.csv"])
bank_path = locate_file(["bank_data.csv", "synthetic_bank_data.csv", "branches.csv"])

st.sidebar.header("Dashboard filters")
if not all([customer_path, transaction_path, bank_path]):
    st.warning("Add the three Kaggle CSV files to the `data` folder to load the dashboard.")
    st.markdown("""
    **Expected files**
    - `customer_data.csv` — customer profiles
    - `transaction_data.csv` — transactions and account balances
    - `bank_data.csv` — branch revenue and expenses

    The app also recognizes the `synthetic_...csv` names described on the Kaggle dataset page.
    """)
    st.info("Download the Kaggle dataset linked in the project README, extract it, and copy the three CSV files into `data/`.")
    st.stop()

customers = load_csv(customer_path)
transactions = load_csv(transaction_path)
branches = load_csv(bank_path)

# Normalize common Kaggle column names
def col(df, options):
    lookup = {str(c).strip().lower().replace(" ", "_"): c for c in df.columns}
    for opt in options:
        if opt in lookup:
            return lookup[opt]
    return None

date_c = col(transactions, ["transaction_date", "date", "transaction_time"])
amount_c = col(transactions, ["transaction_amount", "amount", "transaction_value"])
customer_id_t = col(transactions, ["customer_id", "customerid"])
customer_id_c = col(customers, ["customer_id", "customerid"])
balance_c = col(transactions, ["total_balance", "account_balance", "balance"])
account_c = col(transactions, ["account_type", "account"])
type_c = col(transactions, ["transaction_type", "type", "transaction"])
income_c = col(customers, ["annual_income", "income", "customer_income"])
revenue_c = col(branches, ["firm_revenue", "revenue", "branch_revenue"])
expense_c = col(branches, ["expenses", "expense", "branch_expenses"])
city_b = col(branches, ["city", "branch_city"])
region_b = col(branches, ["region", "branch_region"])

if date_c:
    transactions[date_c] = pd.to_datetime(transactions[date_c], errors="coerce")
    transactions = transactions.dropna(subset=[date_c])
if amount_c:
    transactions[amount_c] = pd.to_numeric(transactions[amount_c], errors="coerce").fillna(0)
if income_c:
    customers[income_c] = pd.to_numeric(customers[income_c], errors="coerce")
if revenue_c:
    branches[revenue_c] = pd.to_numeric(branches[revenue_c], errors="coerce").fillna(0)
if expense_c:
    branches[expense_c] = pd.to_numeric(branches[expense_c], errors="coerce").fillna(0)

if date_c:
    min_d, max_d = transactions[date_c].min().date(), transactions[date_c].max().date()
    date_range = st.sidebar.date_input("Transaction date range", (min_d, max_d), min_value=min_d, max_value=max_d)
    if isinstance(date_range, tuple) and len(date_range) == 2:
        filtered = transactions[transactions[date_c].dt.date.between(date_range[0], date_range[1])].copy()
    else:
        filtered = transactions.copy()
else:
    filtered = transactions.copy()
if type_c:
    vals = sorted(filtered[type_c].dropna().astype(str).unique())
    selected = st.sidebar.multiselect("Transaction type", vals, default=vals)
    filtered = filtered[filtered[type_c].astype(str).isin(selected)]
if account_c:
    vals = sorted(filtered[account_c].dropna().astype(str).unique())
    selected = st.sidebar.multiselect("Account type", vals, default=vals)
    filtered = filtered[filtered[account_c].astype(str).isin(selected)]

# Summary KPIs
total_tx = len(filtered)
total_value = filtered[amount_c].sum() if amount_c else 0
active_customers = filtered[customer_id_t].nunique() if customer_id_t else (customers[customer_id_c].nunique() if customer_id_c else len(customers))
avg_tx = filtered[amount_c].mean() if amount_c and total_tx else 0
k1,k2,k3,k4 = st.columns(4)
k1.metric("Transactions", f"{total_tx:,}")
k2.metric("Transaction value", f"₹{total_value:,.0f}" if amount_c else "N/A")
k3.metric("Active customers", f"{active_customers:,}")
k4.metric("Average transaction", f"₹{avg_tx:,.0f}" if amount_c else "N/A")

tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "💳 Transactions", "👥 Customers & accounts", "💰 Income & branches"])

with tab1:
    left, right = st.columns(2)
    with left:
        st.subheader("Transaction activity over time")
        if date_c:
            freq = filtered.set_index(date_c).resample("MS").size().rename("Transactions").reset_index()
            freq[date_c] = freq[date_c].dt.strftime("%b %Y")
            st.plotly_chart(px.line(freq, x=date_c, y="Transactions", markers=True), use_container_width=True)
        else: st.info("No recognizable transaction date column.")
    with right:
        st.subheader("Transaction value by type")
        if amount_c and type_c:
            agg = filtered.groupby(type_c, dropna=False)[amount_c].sum().reset_index().sort_values(amount_c, ascending=False)
            st.plotly_chart(px.bar(agg, x=type_c, y=amount_c, color=type_c), use_container_width=True)
        elif amount_c:
            st.plotly_chart(px.histogram(filtered, x=amount_c, nbins=30), use_container_width=True)
        else: st.info("No recognizable transaction amount column.")

with tab2:
    st.subheader("Transaction analysis")
    a,b = st.columns(2)
    with a:
        if amount_c:
            st.plotly_chart(px.histogram(filtered, x=amount_c, nbins=40, title="Transaction amount distribution"), use_container_width=True)
    with b:
        if type_c:
            counts = filtered[type_c].astype(str).value_counts().rename_axis("Type").reset_index(name="Count")
            st.plotly_chart(px.pie(counts, names="Type", values="Count", hole=.45, title="Transaction mix"), use_container_width=True)
    st.subheader("Transaction records")
    st.dataframe(filtered.head(500), use_container_width=True, hide_index=True)

with tab3:
    st.subheader("Customer profile")
    a,b = st.columns(2)
    age_c = col(customers, ["age"])
    segment_c = col(customers, ["customer_type", "customer_segment", "segment"])
    city_c = col(customers, ["city"])
    with a:
        if segment_c:
            seg = customers[segment_c].astype(str).value_counts().rename_axis("Customer type").reset_index(name="Customers")
            st.plotly_chart(px.bar(seg, x="Customer type", y="Customers", title="Customers by type"), use_container_width=True)
        elif age_c:
            st.plotly_chart(px.histogram(customers, x=age_c, title="Customer age distribution"), use_container_width=True)
    with b:
        if income_c:
            st.plotly_chart(px.histogram(customers.dropna(subset=[income_c]), x=income_c, nbins=30, title="Annual income distribution"), use_container_width=True)
        elif city_c:
            city = customers[city_c].astype(str).value_counts().head(12).rename_axis("City").reset_index(name="Customers")
            st.plotly_chart(px.bar(city, x="City", y="Customers", title="Top customer cities"), use_container_width=True)
    st.metric("Total customer records", f"{len(customers):,}")
    st.dataframe(customers.head(300), use_container_width=True, hide_index=True)

with tab4:
    st.subheader("Branch income and profitability")
    if revenue_c:
        total_rev = branches[revenue_c].sum()
        total_exp = branches[expense_c].sum() if expense_c else 0
        x,y,z = st.columns(3)
        x.metric("Total branch revenue", f"₹{total_rev:,.0f}")
        y.metric("Total expenses", f"₹{total_exp:,.0f}" if expense_c else "N/A")
        z.metric("Revenue less expenses", f"₹{total_rev-total_exp:,.0f}" if expense_c else "N/A")
        if city_b:
            st.plotly_chart(px.bar(branches.groupby(city_b, as_index=False)[revenue_c].sum().sort_values(revenue_c, ascending=False).head(15),
                                   x=city_b, y=revenue_c, title="Revenue by city"), use_container_width=True)
        elif region_b:
            st.plotly_chart(px.bar(branches.groupby(region_b, as_index=False)[revenue_c].sum(),
                                   x=region_b, y=revenue_c, title="Revenue by region"), use_container_width=True)
        if expense_c:
            branches["Calculated_Profit"] = branches[revenue_c] - branches[expense_c]
            st.plotly_chart(px.bar(branches, x=city_b or branches.columns[0], y="Calculated_Profit",
                                   title="Estimated branch profit"), use_container_width=True)
    else:
        st.info("The Kaggle bank/branch file does not contain a recognized revenue field. Check its column names.")
    st.dataframe(branches.head(300), use_container_width=True, hide_index=True)

st.caption("Data source: Kaggle Banking and Customer Transaction Data. Dataset is synthetic; figures are for analysis/demo use, not real bank reporting.")
