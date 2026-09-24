import streamlit as st
import pandas as pd
import plotly.express as px

from ai_analytics import (
    answer_business_question,
    generate_local_insights,
    prepare_dataset_summary,
)


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Raremotion Analytics",
    page_icon="📊",
    layout="wide",
)


# ==================================================
# HEADER
# ==================================================

st.title("📊 Raremotion Analytics")

st.caption(
    "Turn business data into useful insights."
)


# ==================================================
# FILE UPLOAD
# ==================================================

uploaded_file = st.file_uploader(
    "Upload a CSV file",
    type=["csv"],
    help=(
        "Upload business, sales, customer, financial, "
        "or other structured data."
    ),
)


if uploaded_file is None:

    st.info(
        "Upload a CSV file to begin analyzing your data."
    )

    st.stop()


# ==================================================
# LOAD CSV
# ==================================================

try:

    df = pd.read_csv(
        uploaded_file
    )

except Exception as error:

    st.error(
        f"Could not read this CSV file: {error}"
    )

    st.stop()


if df.empty:

    st.warning(
        "The uploaded CSV file contains no data."
    )

    st.stop()


st.success(
    "Dataset loaded successfully!"
)


# ==================================================
# PREPARE DATA
# ==================================================

date_column = None


possible_date_columns = [
    "date",
    "order_date",
    "sale_date",
    "created_at",
]


for column in df.columns:

    if column.lower() in possible_date_columns:

        converted_dates = pd.to_datetime(
            df[column],
            errors="coerce",
        )

        if converted_dates.notna().any():

            df[column] = converted_dates

            date_column = column

            break


# ==================================================
# CREATE PROFIT COLUMN
# ==================================================

if (
    "Revenue" in df.columns
    and "Cost" in df.columns
):

    df["Profit"] = (
        df["Revenue"]
        - df["Cost"]
    )


# ==================================================
# BUSINESS OVERVIEW
# ==================================================

st.header(
    "Business Overview"
)


if (
    "Revenue" in df.columns
    and "Cost" in df.columns
):

    total_revenue = (
        df["Revenue"].sum()
    )

    total_cost = (
        df["Cost"].sum()
    )

    total_profit = (
        df["Profit"].sum()
    )


    if total_revenue != 0:

        profit_margin = (
            total_profit
            / total_revenue
        ) * 100

    else:

        profit_margin = 0


    if "Units" in df.columns:

        total_units = (
            df["Units"].sum()
        )

    else:

        total_units = 0


    (
        metric1,
        metric2,
        metric3,
        metric4,
        metric5,
    ) = st.columns(5)


    metric1.metric(
        "Total Revenue",
        f"₦{total_revenue:,.0f}",
    )


    metric2.metric(
        "Total Cost",
        f"₦{total_cost:,.0f}",
    )


    metric3.metric(
        "Total Profit",
        f"₦{total_profit:,.0f}",
    )


    metric4.metric(
        "Profit Margin",
        f"{profit_margin:.1f}%",
    )


    metric5.metric(
        "Units Sold",
        f"{total_units:,.0f}",
    )


else:

    st.info(
        "Revenue and Cost columns were not detected, "
        "so business KPIs cannot be calculated."
    )


# ==================================================
# DATASET OVERVIEW
# ==================================================

st.header(
    "Dataset Overview"
)


(
    overview1,
    overview2,
    overview3,
    overview4,
) = st.columns(4)


overview1.metric(
    "Rows",
    f"{len(df):,}",
)


overview2.metric(
    "Columns",
    len(df.columns),
)


overview3.metric(
    "Missing Values",
    f"{df.isna().sum().sum():,}",
)


overview4.metric(
    "Duplicate Rows",
    f"{df.duplicated().sum():,}",
)


with st.expander(
    "View Raw Data",
    expanded=False,
):

    st.dataframe(
        df,
        use_container_width=True,
    )


# ==================================================
# REVENUE AND PROFIT TREND
# ==================================================

if (
    date_column is not None
    and "Revenue" in df.columns
    and "Profit" in df.columns
):

    st.header(
        "Revenue & Profit Trend"
    )


    trend_data = (
        df
        .dropna(
            subset=[date_column]
        )
        .sort_values(
            date_column
        )
    )


    trend_chart = px.line(
        trend_data,
        x=date_column,
        y=[
            "Revenue",
            "Profit",
        ],
        markers=True,
        title=(
            "Revenue and Profit Over Time"
        ),
    )


    st.plotly_chart(
        trend_chart,
        use_container_width=True,
    )


# ==================================================
# PRODUCT PERFORMANCE
# ==================================================

if (
    "Product" in df.columns
    and "Revenue" in df.columns
):

    st.header(
        "Product Performance"
    )


    product_data = (
        df
        .groupby(
            "Product",
            as_index=False,
        )["Revenue"]
        .sum()
        .sort_values(
            "Revenue",
            ascending=False,
        )
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


# ==================================================
# REGIONAL PERFORMANCE
# ==================================================

if (
    "Region" in df.columns
    and "Revenue" in df.columns
):

    st.header(
        "Regional Performance"
    )


    region_data = (
        df
        .groupby(
            "Region",
            as_index=False,
        )["Revenue"]
        .sum()
        .sort_values(
            "Revenue",
            ascending=False,
        )
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


# ==================================================
# CATEGORY PERFORMANCE
# ==================================================

if (
    "Category" in df.columns
    and "Revenue" in df.columns
):

    st.header(
        "Category Performance"
    )


    category_data = (
        df
        .groupby(
            "Category",
            as_index=False,
        )["Revenue"]
        .sum()
        .sort_values(
            "Revenue",
            ascending=False,
        )
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


# ==================================================
# DATA QUALITY
# ==================================================

st.header(
    "Data Quality"
)


missing_data = (
    df
    .isna()
    .sum()
)


missing_data = (
    missing_data[
        missing_data > 0
    ]
)


if missing_data.empty:

    st.success(
        "No missing values detected."
    )

else:

    st.warning(
        "Some columns contain missing values."
    )


    missing_dataframe = pd.DataFrame(
        {
            "Column": missing_data.index,
            "Missing Values": missing_data.values,
        }
    )


    st.dataframe(
        missing_dataframe,
        use_container_width=True,
    )


# ==================================================
# STATISTICS
# ==================================================

st.header(
    "Statistics"
)


numeric_columns = (
    df
    .select_dtypes(
        include="number"
    )
    .columns
    .tolist()
)


if numeric_columns:

    statistics = (
        df[numeric_columns]
        .describe()
        .T
    )


    st.dataframe(
        statistics,
        use_container_width=True,
    )

else:

    st.info(
        "No numeric data is available "
        "for statistical analysis."
    )


# ==================================================
# RAREMOTION INTELLIGENCE
# ==================================================

st.header(
    "🧠 Raremotion Intelligence"
)


st.caption(
    "Automatic business insights generated "
    "from your uploaded dataset."
)


local_insights = (
    generate_local_insights(
        df
    )
)


st.subheader(
    "Business Summary"
)


for insight in local_insights:

    st.write(
        f"• {insight}"
    )


# ==================================================
# ANALYTICS ENGINE SUMMARY
# ==================================================

with st.expander(
    "View Analytics Engine Summary"
):

    dataset_summary = (
        prepare_dataset_summary(
            df
        )
    )


    st.code(
        dataset_summary
    )


# ==================================================
# ASK RAREMOTION AI
# ==================================================

st.header(
    "🤖 Ask Raremotion AI"
)


st.caption(
    "Ask questions about the business data "
    "you uploaded."
)


st.write(
    "Try questions like:"
)


st.markdown(
    """
- What is my total revenue?
- How much profit did I make?
- Which product is performing best?
- Which region is performing best?
- How many units were sold?
- Summarize the business.
"""
)


business_question = st.text_input(
    "Ask a question about your data",
    placeholder=(
        "Example: Which product is performing best?"
    ),
)


ask_button = st.button(
    "Ask Raremotion AI",
    type="primary",
)


if ask_button:

    if not business_question.strip():

        st.warning(
            "Enter a question first."
        )

    else:

        answer = (
            answer_business_question(
                df,
                business_question,
            )
        )


        st.subheader(
            "Answer"
        )


        st.write(
            answer
        )


# ==================================================
# SMART BUSINESS INSIGHTS
# ==================================================

st.header(
    "Smart Business Insights"
)


if "Revenue" in df.columns:

    average_revenue = (
        df["Revenue"].mean()
    )


    highest_revenue = (
        df["Revenue"].max()
    )


    st.write(
        f"**Average revenue per record:** "
        f"₦{average_revenue:,.0f}"
    )


    st.write(
        f"**Highest revenue transaction:** "
        f"₦{highest_revenue:,.0f}"
    )


    # ----------------------------------------------
    # TOP PRODUCT
    # ----------------------------------------------

    if "Product" in df.columns:

        product_revenue = (
            df
            .groupby(
                "Product"
            )["Revenue"]
            .sum()
            .sort_values(
                ascending=False
            )
        )


        if not product_revenue.empty:

            top_product = (
                product_revenue.index[0]
            )


            top_product_revenue = (
                product_revenue.iloc[0]
            )


            st.write(
                f"**Top product:** "
                f"{top_product} "
                f"(₦{top_product_revenue:,.0f} revenue)"
            )


    # ----------------------------------------------
    # TOP REGION
    # ----------------------------------------------

    if "Region" in df.columns:

        region_revenue = (
            df
            .groupby(
                "Region"
            )["Revenue"]
            .sum()
            .sort_values(
                ascending=False
            )
        )


        if not region_revenue.empty:

            top_region = (
                region_revenue.index[0]
            )


            top_region_revenue = (
                region_revenue.iloc[0]
            )


            st.write(
                f"**Top region:** "
                f"{top_region} "
                f"(₦{top_region_revenue:,.0f} revenue)"
            )


    # ----------------------------------------------
    # TOTAL PROFIT
    # ----------------------------------------------

    if "Profit" in df.columns:

        total_profit = (
            df["Profit"].sum()
        )


        st.write(
            f"**Total profit generated:** "
            f"₦{total_profit:,.0f}"
        )


else:

    st.info(
        "A Revenue column was not detected, "
        "so revenue-based insights are unavailable."
    )


# ==================================================
# EXPLORE YOUR DATA
# ==================================================

st.header(
    "Explore Your Data"
)


numeric_options = (
    df
    .select_dtypes(
        include="number"
    )
    .columns
    .tolist()
)


if numeric_options:

    selected_column = (
        st.selectbox(
            "Choose a numeric column to explore",
            numeric_options,
        )
    )


    chart_type = (
        st.selectbox(
            "Choose visualization",
            [
                "Histogram",
                "Box Plot",
            ],
        )
    )


    if chart_type == "Histogram":

        custom_chart = (
            px.histogram(
                df,
                x=selected_column,
                title=(
                    f"Distribution of "
                    f"{selected_column}"
                ),
            )
        )

    else:

        custom_chart = (
            px.box(
                df,
                y=selected_column,
                title=(
                    f"Distribution of "
                    f"{selected_column}"
                ),
            )
        )


    st.plotly_chart(
        custom_chart,
        use_container_width=True,
    )

else:

    st.info(
        "No numeric columns are available "
        "for exploration."
    )


# ==================================================
# FOOTER
# ==================================================

st.divider()


st.caption(
    "Raremotion Analytics • Built by Raremotion Labs"
)