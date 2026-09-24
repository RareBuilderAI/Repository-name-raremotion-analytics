import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Raremotion Analytics",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Raremotion Analytics")
st.caption("Turn business data into useful insights.")

# --------------------------------------------------
# FILE UPLOAD
# --------------------------------------------------

uploaded_file = st.file_uploader(
    "Upload a CSV file",
    type=["csv"],
    help="Upload business, sales, customer, financial, or other structured data.",
)

if uploaded_file is None:
    st.info("Upload a CSV file to begin analyzing your data.")
    st.stop()

try:
    df = pd.read_csv(uploaded_file)
except Exception as error:
    st.error(f"Could not read this CSV file: {error}")
    st.stop()

if df.empty:
    st.warning("The uploaded CSV file contains no data.")
    st.stop()

st.success("Dataset loaded successfully!")

# --------------------------------------------------
# PREPARE DATA
# --------------------------------------------------

# Detect and convert a Date column if one exists
date_column = None

for column in df.columns:
    if column.lower() in ["date", "order_date", "sale_date", "created_at"]:
        converted = pd.to_datetime(df[column], errors="coerce")

        if converted.notna().any():
            df[column] = converted
            date_column = column
            break

# Create Profit when Revenue and Cost exist
if "Revenue" in df.columns and "Cost" in df.columns:
    df["Profit"] = df["Revenue"] - df["Cost"]

# --------------------------------------------------
# BUSINESS OVERVIEW
# --------------------------------------------------

st.header("Business Overview")

if "Revenue" in df.columns and "Cost" in df.columns:
    total_revenue = df["Revenue"].sum()
    total_cost = df["Cost"].sum()
    total_profit = df["Profit"].sum()

    profit_margin = (
        (total_profit / total_revenue) * 100
        if total_revenue != 0
        else 0
    )

    total_units = (
        df["Units"].sum()
        if "Units" in df.columns
        else 0
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "Total Revenue",
        f"₦{total_revenue:,.0f}",
    )

    col2.metric(
        "Total Cost",
        f"₦{total_cost:,.0f}",
    )

    col3.metric(
        "Total Profit",
        f"₦{total_profit:,.0f}",
    )

    col4.metric(
        "Profit Margin",
        f"{profit_margin:.1f}%",
    )

    col5.metric(
        "Units Sold",
        f"{total_units:,.0f}",
    )

else:
    st.info(
        "Revenue and Cost columns were not detected, "
        "so business KPIs cannot be calculated."
    )

# --------------------------------------------------
# DATASET OVERVIEW
# --------------------------------------------------

st.header("Dataset Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Rows", f"{len(df):,}")
col2.metric("Columns", len(df.columns))
col3.metric(
    "Missing Values",
    f"{df.isna().sum().sum():,}",
)
col4.metric(
    "Duplicate Rows",
    f"{df.duplicated().sum():,}",
)

with st.expander("View Raw Data"):
    st.dataframe(
        df,
        use_container_width=True,
    )

# --------------------------------------------------
# REVENUE & PROFIT TREND
# --------------------------------------------------

if (
    date_column
    and "Revenue" in df.columns
    and "Profit" in df.columns
):
    st.header("Revenue & Profit Trend")

    trend_data = (
        df.dropna(subset=[date_column])
        .sort_values(date_column)
    )

    trend_chart = px.line(
        trend_data,
        x=date_column,
        y=["Revenue", "Profit"],
        markers=True,
        title="Revenue and Profit Over Time",
    )

    st.plotly_chart(
        trend_chart,
        use_container_width=True,
    )

# --------------------------------------------------
# PRODUCT PERFORMANCE
# --------------------------------------------------

if "Product" in df.columns and "Revenue" in df.columns:
    st.header("Product Performance")

    product_data = (
        df.groupby("Product", as_index=False)["Revenue"]
        .sum()
        .sort_values("Revenue", ascending=False)
    )

    product_chart = px.bar(
        product_data,
        x="Product",
        y="Revenue",
        title="Revenue by Product",
    )

    st.plotly_chart(
        product_chart,
        use_container_width=True,
    )

# --------------------------------------------------
# REGION PERFORMANCE
# --------------------------------------------------

if "Region" in df.columns and "Revenue" in df.columns:
    st.header("Regional Performance")

    region_data = (
        df.groupby("Region", as_index=False)["Revenue"]
        .sum()
        .sort_values("Revenue", ascending=False)
    )

    region_chart = px.bar(
        region_data,
        x="Region",
        y="Revenue",
        title="Revenue by Region",
    )

    st.plotly_chart(
        region_chart,
        use_container_width=True,
    )

# --------------------------------------------------
# CATEGORY PERFORMANCE
# --------------------------------------------------

if "Category" in df.columns and "Revenue" in df.columns:
    st.header("Category Performance")

    category_data = (
        df.groupby("Category", as_index=False)["Revenue"]
        .sum()
        .sort_values("Revenue", ascending=False)
    )

    category_chart = px.bar(
        category_data,
        x="Category",
        y="Revenue",
        title="Revenue by Category",
    )

    st.plotly_chart(
        category_chart,
        use_container_width=True,
    )

# --------------------------------------------------
# DATA QUALITY
# --------------------------------------------------

st.header("Data Quality")

missing_data = df.isna().sum()
missing_data = missing_data[missing_data > 0]

if missing_data.empty:
    st.success("No missing values detected.")
else:
    st.warning("Some columns contain missing values.")

    missing_df = pd.DataFrame({
        "Column": missing_data.index,
        "Missing Values": missing_data.values,
    })

    st.dataframe(
        missing_df,
        use_container_width=True,
    )

# --------------------------------------------------
# NUMERIC STATISTICS
# --------------------------------------------------

numeric_columns = (
    df.select_dtypes(include="number")
    .columns
    .tolist()
)

st.header("Statistics")

if numeric_columns:
    st.dataframe(
        df[numeric_columns].describe().T,
        use_container_width=True,
    )
else:
    st.info(
        "No numeric data is available for statistical analysis."
    )

# --------------------------------------------------
# SMART BUSINESS INSIGHTS
# --------------------------------------------------

st.header("Smart Business Insights")

if "Revenue" in df.columns:

    average_revenue = df["Revenue"].mean()
    highest_revenue = df["Revenue"].max()

    st.write(
        f"**Average revenue per record:** "
        f"₦{average_revenue:,.0f}"
    )

    st.write(
        f"**Highest revenue transaction:** "
        f"₦{highest_revenue:,.0f}"
    )

    if "Product" in df.columns:
        product_revenue = (
            df.groupby("Product")["Revenue"]
            .sum()
            .sort_values(ascending=False)
        )

        if not product_revenue.empty:
            top_product = product_revenue.index[0]
            top_product_revenue = product_revenue.iloc[0]

            st.write(
                f"**Top product:** {top_product} "
                f"(₦{top_product_revenue:,.0f} revenue)"
            )

    if "Region" in df.columns:
        region_revenue = (
            df.groupby("Region")["Revenue"]
            .sum()
            .sort_values(ascending=False)
        )

        if not region_revenue.empty:
            top_region = region_revenue.index[0]
            top_region_revenue = region_revenue.iloc[0]

            st.write(
                f"**Top region:** {top_region} "
                f"(₦{top_region_revenue:,.0f} revenue)"
            )

    if "Profit" in df.columns:
        total_profit = df["Profit"].sum()

        st.write(
            f"**Total profit generated:** "
            f"₦{total_profit:,.0f}"
        )

# --------------------------------------------------
# CUSTOM ANALYSIS
# --------------------------------------------------

st.header("Explore Your Data")

numeric_options = (
    df.select_dtypes(include="number")
    .columns
    .tolist()
)

if numeric_options:
    selected_column = st.selectbox(
        "Choose a numeric column to explore",
        numeric_options,
    )

    chart_type = st.selectbox(
        "Choose visualization",
        ["Histogram", "Box Plot"],
    )

    if chart_type == "Histogram":
        custom_chart = px.histogram(
            df,
            x=selected_column,
            title=f"Distribution of {selected_column}",
        )
    else:
        custom_chart = px.box(
            df,
            y=selected_column,
            title=f"Distribution of {selected_column}",
        )

    st.plotly_chart(
        custom_chart,
        use_container_width=True,
    )

st.divider()

st.caption(
    "Raremotion Analytics • Built by Raremotion Labs"
)