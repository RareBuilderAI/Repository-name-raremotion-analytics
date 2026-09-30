import streamlit as st
import pandas as pd
import plotly.express as px

from auth import show_auth
from analysis_access import require_analysis_access

from ai_analytics import (
    prepare_dataset_summary,
    generate_local_insights,
    ask_raremotion_ai,
)


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Raremotion Analytics",
    page_icon="📊",
    layout="wide",
)

user = show_auth()


# ==================================================
# HEADER
# ==================================================

st.title("📊 Raremotion Analytics")

st.write(
    "Turn business data into useful insights."
)


# ==================================================
# FILE UPLOAD
# ==================================================

uploaded_file = st.file_uploader(
    "Upload a CSV file",
    type=["csv"],
)


if uploaded_file is None:

    st.session_state.pop("analysis_access", None)

    st.info(
        "Upload a CSV file to begin analyzing your data."
    )

    st.stop()


# ==================================================
# LOAD DATASET
# ==================================================

try:

    df = pd.read_csv(uploaded_file)

except Exception as error:

    st.error(
        f"Unable to read the CSV file: {error}"
    )

    st.stop()


if df.empty:

    st.warning(
        "The uploaded CSV file is empty."
    )

    st.stop()


st.success(
    "Dataset loaded successfully!"
)


require_analysis_access(user, uploaded_file.getvalue())

# ==================================================
# CLEAN COLUMN NAMES
# ==================================================

df.columns = (
    df.columns
    .astype(str)
    .str.strip()
)


# ==================================================
# CONVERT BUSINESS COLUMNS TO NUMBERS
# ==================================================

for column in [
    "Units",
    "Revenue",
    "Cost",
]:

    if column in df.columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )


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
# PREPARE DATE COLUMN
# ==================================================

date_column = None


for column in df.columns:

    if column.lower() in [
        "date",
        "order_date",
        "sale_date",
        "created_at",
    ]:

        converted_date = pd.to_datetime(
            df[column],
            errors="coerce",
        )

        if converted_date.notna().any():

            df[column] = converted_date

            date_column = column

            break


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
        total_revenue
        - total_cost
    )

    profit_margin = (
        (
            total_profit
            / total_revenue
        )
        * 100
        if total_revenue != 0
        else 0
    )

    total_units = (
        df["Units"].sum()
        if "Units" in df.columns
        else 0
    )


    col1, col2, col3, col4, col5 = (
        st.columns(5)
    )


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
        "Revenue and Cost columns were not detected."
    )


# ==================================================
# DATASET OVERVIEW
# ==================================================

st.header(
    "Dataset Overview"
)


overview1, overview2, overview3, overview4 = (
    st.columns(4)
)


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
    f"{int(df.isna().sum().sum()):,}",
)


overview4.metric(
    "Duplicate Rows",
    f"{int(df.duplicated().sum()):,}",
)


with st.expander(
    "View Raw Data"
):

    st.dataframe(
        df,
        use_container_width=True,
    )


# ==================================================
# REVENUE & PROFIT TREND
# ==================================================

if (
    date_column is not None
    and "Revenue" in df.columns
):

    st.header(
        "Revenue & Profit Trend"
    )


    trend_columns = [
        "Revenue"
    ]


    if "Profit" in df.columns:

        trend_columns.append(
            "Profit"
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
        y=trend_columns,
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
        df.groupby(
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
        df.groupby(
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
        df.groupby(
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


missing_values = (
    df.isna().sum()
)


missing_values = (
    missing_values[
        missing_values > 0
    ]
)


if missing_values.empty:

    st.success(
        "No missing values detected."
    )

else:

    st.warning(
        "Missing values were detected."
    )


    missing_table = pd.DataFrame(
        {
            "Column":
                missing_values.index,

            "Missing Values":
                missing_values.values,
        }
    )


    st.dataframe(
        missing_table,
        use_container_width=True,
    )


# ==================================================
# STATISTICS
# ==================================================

st.header(
    "Statistics"
)


numeric_columns = (
    df.select_dtypes(
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
        "No numeric columns are available."
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


st.subheader(
    "Business Summary"
)


local_insights = (
    generate_local_insights(
        df
    )
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
# ASK RAREMOTION AI — V5
# ==================================================

st.header(
    "🤖 Ask Raremotion AI"
)


st.caption(
    "Ask Raremotion AI questions about "
    "the business data you uploaded."
)


st.markdown(
    """
Try asking:

- What are the three most important things I should know about this business?
- What does this business performance tell me?
- Which product is strongest and why?
- Which region should I pay attention to?
- How profitable is this business?
- Summarize the business performance.
- What are the most important insights in this data?
"""
)


business_question = (
    st.text_area(
        "Ask a question about your data",
        placeholder=(
            "Example: What are the three most important "
            "things I should know about this business?"
        ),
        height=110,
        key="raremotion_ai_question",
    )
)


ask_ai_button = (
    st.button(
        "Ask Raremotion AI",
        type="primary",
        key="ask_raremotion_ai_button",
    )
)


if ask_ai_button:

    if not business_question.strip():

        st.warning(
            "Please enter a question first."
        )

    else:

        with st.spinner(
            "Raremotion AI is analyzing "
            "your business data..."
        ):

            answer, answer_source = (
                ask_raremotion_ai(
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


        if answer_source == "AI":

            st.success(
                "🤖 Answer generated by "
                "Raremotion AI."
            )

        else:

            st.info(
                "⚙️ Answer generated by "
                "the local analytics engine."
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
            df.groupby(
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
            df.groupby(
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
    df.select_dtypes(
        include="number"
    )
    .columns
    .tolist()
)


if numeric_options:

    selected_column = (
        st.selectbox(
            "Choose a numeric column",
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

        explore_chart = (
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

        explore_chart = (
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
        explore_chart,
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
    "Raremotion Analytics • "
    "Built by Raremotion Labs"
)