
import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------------------
# 1. PAGE CONFIGURATION
# ----------------------------
st.set_page_config(
    page_title="Walmart Sales Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("Walmart Sales Analytics Dashboard")
st.caption("Exploring store performance, sales trends, and holiday effects")

# ----------------------------
# 2. LOAD DATA
# ----------------------------
@st.cache_data
def load_data():
    data = pd.read_csv("Walmart_Sales.csv")
    data["Date"] = pd.to_datetime(data["Date"], dayfirst=True)
    data["Year"] = data["Date"].dt.year
    data["Month"] = data["Date"].dt.month
    data["Month_Name"] = data["Date"].dt.strftime("%b")
    data["Holiday_Status"] = data["Holiday_Flag"].map(
        {1: "Holiday", 0: "Non-Holiday"}
    )
    return data

df = load_data()

# ----------------------------
# 3. SIDEBAR FILTERS
# ----------------------------
st.sidebar.header("Dashboard Filters")

years = sorted(df["Year"].dropna().unique())
selected_years = st.sidebar.multiselect(
    "Select year(s)",
    years,
    default=years
)

stores = sorted(df["Store"].dropna().unique())
selected_stores = st.sidebar.multiselect(
    "Select store(s)",
    stores,
    default=stores
)

holiday_options = ["Holiday", "Non-Holiday"]
selected_holidays = st.sidebar.multiselect(
    "Holiday status",
    holiday_options,
    default=holiday_options
)

filtered = df[
    df["Year"].isin(selected_years)
    & df["Store"].isin(selected_stores)
    & df["Holiday_Status"].isin(selected_holidays)
].copy()

if filtered.empty:
    st.warning("No records match your selected filters.")
    st.stop()

# ----------------------------
# 4. KPI CARDS
# ----------------------------
total_sales = filtered["Weekly_Sales"].sum()
average_sales = filtered["Weekly_Sales"].mean()
highest_sale = filtered["Weekly_Sales"].max()
number_of_stores = filtered["Store"].nunique()

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Sales", f"${total_sales:,.0f}")
c2.metric("Average Weekly Record", f"${average_sales:,.0f}")
c3.metric("Highest Weekly Sale", f"${highest_sale:,.0f}")
c4.metric("Stores Selected", f"{number_of_stores}")

st.divider()

# ----------------------------
# 5. SALES TREND
# ----------------------------
st.subheader("Sales Trend Over Time")

sales_trend = (
    filtered.groupby("Date", as_index=False)["Weekly_Sales"]
    .sum()
    .sort_values("Date")
)

fig_trend = px.line(
    sales_trend,
    x="Date",
    y="Weekly_Sales",
    markers=True,
    title="Total Sales Across Stores by Week"
)

st.plotly_chart(fig_trend, use_container_width=True)

# ----------------------------
# 6. STORE PERFORMANCE
# ----------------------------
left, right = st.columns(2)

with left:
    st.subheader("Top 10 Stores")

    store_sales = (
        filtered.groupby("Store", as_index=False)["Weekly_Sales"]
        .sum()
        .sort_values("Weekly_Sales", ascending=False)
    )

    fig_top = px.bar(
        store_sales.head(10).sort_values("Weekly_Sales"),
        x="Weekly_Sales",
        y="Store",
        orientation="h",
        title="Top 10 by Total Sales"
    )

    st.plotly_chart(fig_top, use_container_width=True)

with right:
    st.subheader("Holiday Comparison")

    holiday_sales = (
        filtered.groupby("Holiday_Status", as_index=False)
        .agg(
            Average_Sales=("Weekly_Sales", "mean"),
            Total_Sales=("Weekly_Sales", "sum")
        )
    )

    fig_holiday = px.bar(
        holiday_sales,
        x="Holiday_Status",
        y="Average_Sales",
        color="Holiday_Status",
        title="Average Sales: Holiday vs Non-Holiday"
    )

    st.plotly_chart(fig_holiday, use_container_width=True)

# ----------------------------
# 7. MONTHLY SALES
# ----------------------------
st.subheader("Monthly Sales Performance")

monthly_sales = (
    filtered.groupby(["Year", "Month", "Month_Name"], as_index=False)
    ["Weekly_Sales"].sum()
)

monthly_sales["Period"] = (
    monthly_sales["Year"].astype(str)
    + "-"
    + monthly_sales["Month"].astype(str).str.zfill(2)
)

fig_monthly = px.line(
    monthly_sales,
    x="Period",
    y="Weekly_Sales",
    markers=True,
    title="Monthly Sales by Year"
)

st.plotly_chart(fig_monthly, use_container_width=True)

# ----------------------------
# 8. ECONOMIC FACTORS
# ----------------------------
st.subheader("Sales and Economic Factors")

factor = st.selectbox(
    "Choose a factor",
    ["Temperature", "Fuel_Price", "CPI", "Unemployment"]
)

fig_factor = px.scatter(
    filtered,
    x=factor,
    y="Weekly_Sales",
    opacity=0.5,
    title=f"Weekly Sales vs {factor}"
)

st.plotly_chart(fig_factor, use_container_width=True)

correlation = filtered["Weekly_Sales"].corr(filtered[factor])

st.write(f"Pearson correlation: **{correlation:.3f}**")

# ----------------------------
# 9. DATA TABLE
# ----------------------------
with st.expander("View filtered data"):
    st.dataframe(filtered, use_container_width=True)

st.caption("Walmart Sales Analysis | Data analytics portfolio project")
