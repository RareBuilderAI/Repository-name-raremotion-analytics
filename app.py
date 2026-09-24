import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Raremotion Analytics",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Raremotion Analytics")
st.caption("Turn raw business data into useful insights.")

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

# Dataset overview
st.header("Dataset Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Rows", f"{len(df):,}")
col2.metric("Columns", len(df.columns))
col3.metric("Missing Values", f"{df.isna().sum().sum():,}")
col4.metric("Duplicate Rows", f"{df.duplicated().sum():,}")

with st.expander("View Raw Data", expanded=True):
    st.dataframe(df, use_container_width=True)

# Detect column types
numeric_columns = df.select_dtypes(include="number").columns.tolist()
text_columns = df.select_dtypes(exclude="number").columns.tolist()

st.header("Column Analysis")

left, right = st.columns(2)

with left:
    st.subheader("Numeric Columns")

    if numeric_columns:
        for column in numeric_columns:
            st.write(f"• {column}")
    else:
        st.write("No numeric columns detected.")

with right:
    st.subheader("Text / Other Columns")

    if text_columns:
        for column in text_columns:
            st.write(f"• {column}")
    else:
        st.write("No text columns detected.")

# Data quality
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

    st.dataframe(missing_df, use_container_width=True)

# Statistics
st.header("Statistics")

if numeric_columns:
    st.dataframe(
        df[numeric_columns].describe().T,
        use_container_width=True,
    )
else:
    st.info("No numeric data is available for statistical analysis.")

# Visual analysis
st.header("Visual Analysis")

if numeric_columns:
    selected_numeric = st.selectbox(
        "Choose a numeric column",
        numeric_columns,
    )

    chart_type = st.selectbox(
        "Choose a chart",
        ["Histogram", "Box Plot"],
    )

    if chart_type == "Histogram":
        figure = px.histogram(
            df,
            x=selected_numeric,
            title=f"Distribution of {selected_numeric}",
        )
    else:
        figure = px.box(
            df,
            y=selected_numeric,
            title=f"Distribution of {selected_numeric}",
        )

    st.plotly_chart(figure, use_container_width=True)

else:
    st.info("No numeric columns are available for charts.")

# Category analysis
st.header("Category Analysis")

if text_columns:
    category_column = st.selectbox(
        "Choose a category",
        text_columns,
    )

    category_counts = (
        df[category_column]
        .fillna("Missing")
        .astype(str)
        .value_counts()
        .head(15)
        .reset_index()
    )

    category_counts.columns = [category_column, "Count"]

    category_chart = px.bar(
        category_counts,
        x=category_column,
        y="Count",
        title=f"Top values in {category_column}",
    )

    st.plotly_chart(category_chart, use_container_width=True)

else:
    st.info("No categorical columns are available.")

# Automatic insights
st.header("Automatic Insights")

st.write(
    f"""
**Raremotion Analytics found:**

- {len(df):,} records
- {len(df.columns)} columns
- {len(numeric_columns)} numeric columns
- {len(text_columns)} text/other columns
- {df.isna().sum().sum():,} missing values
- {df.duplicated().sum():,} duplicate rows
"""
)

if numeric_columns:
    st.subheader("Numeric Highlights")

    for column in numeric_columns[:5]:
        clean_values = df[column].dropna()

        if not clean_values.empty:
            st.write(
                f"**{column}:** "
                f"Average = {clean_values.mean():,.2f} | "
                f"Minimum = {clean_values.min():,.2f} | "
                f"Maximum = {clean_values.max():,.2f}"
            )

st.divider()
st.caption("Raremotion Analytics • Built by Raremotion Labs")