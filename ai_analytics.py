import os

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI


# ==================================================
# ENVIRONMENT
# ==================================================

load_dotenv()


def get_openai_api_key():
    """
    Get the OpenAI API key from either:

    1. Local .env file
    2. Streamlit Cloud Secrets
    """

    # Local environment / .env
    api_key = os.getenv("OPENAI_API_KEY")

    if api_key:
        return api_key

    # Streamlit Cloud Secrets
    try:
        import streamlit as st

        if "OPENAI_API_KEY" in st.secrets:
            return st.secrets["OPENAI_API_KEY"]

    except Exception:
        pass

    return None


# ==================================================
# DATASET SUMMARY
# ==================================================

def prepare_dataset_summary(df: pd.DataFrame) -> str:
    """
    Create a compact business summary of the dataset
    for Raremotion AI.
    """

    summary = []

    summary.append(
        f"Number of rows: {len(df)}"
    )

    summary.append(
        f"Number of columns: {len(df.columns)}"
    )

    summary.append(
        "Columns: "
        + ", ".join(
            df.columns.astype(str)
        )
    )

    numeric_columns = (
        df.select_dtypes(
            include="number"
        )
        .columns
        .tolist()
    )

    summary.append(
        "Numeric columns: "
        + (
            ", ".join(numeric_columns)
            if numeric_columns
            else "None"
        )
    )

    summary.append(
        f"Total missing values: "
        f"{int(df.isna().sum().sum())}"
    )

    summary.append(
        f"Duplicate rows: "
        f"{int(df.duplicated().sum())}"
    )

    # ==================================================
    # REVENUE
    # ==================================================

    if "Revenue" in df.columns:

        total_revenue = (
            df["Revenue"].sum()
        )

        average_revenue = (
            df["Revenue"].mean()
        )

        highest_revenue = (
            df["Revenue"].max()
        )

        summary.append(
            f"Total revenue: "
            f"₦{total_revenue:,.2f}"
        )

        summary.append(
            f"Average revenue per record: "
            f"₦{average_revenue:,.2f}"
        )

        summary.append(
            f"Highest revenue transaction: "
            f"₦{highest_revenue:,.2f}"
        )

    # ==================================================
    # COST
    # ==================================================

    if "Cost" in df.columns:

        total_cost = (
            df["Cost"].sum()
        )

        summary.append(
            f"Total cost: "
            f"₦{total_cost:,.2f}"
        )

    # ==================================================
    # PROFIT
    # ==================================================

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

        summary.append(
            f"Total profit: "
            f"₦{total_profit:,.2f}"
        )

        summary.append(
            f"Profit margin: "
            f"{profit_margin:.2f}%"
        )

    # ==================================================
    # UNITS
    # ==================================================

    if "Units" in df.columns:

        total_units = (
            df["Units"].sum()
        )

        summary.append(
            f"Total units: "
            f"{total_units:,.0f}"
        )

    # ==================================================
    # PRODUCT PERFORMANCE
    # ==================================================

    if (
        "Product" in df.columns
        and "Revenue" in df.columns
    ):

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

            summary.append(
                "Top product by revenue: "
                f"{product_revenue.index[0]} "
                f"(₦{product_revenue.iloc[0]:,.2f})"
            )

            product_breakdown = []

            for product, revenue in product_revenue.items():

                product_breakdown.append(
                    f"{product}: "
                    f"₦{revenue:,.2f}"
                )

            summary.append(
                "Revenue by product: "
                + "; ".join(
                    product_breakdown
                )
            )

    # ==================================================
    # REGION PERFORMANCE
    # ==================================================

    if (
        "Region" in df.columns
        and "Revenue" in df.columns
    ):

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

            summary.append(
                "Top region by revenue: "
                f"{region_revenue.index[0]} "
                f"(₦{region_revenue.iloc[0]:,.2f})"
            )

            region_breakdown = []

            for region, revenue in region_revenue.items():

                region_breakdown.append(
                    f"{region}: "
                    f"₦{revenue:,.2f}"
                )

            summary.append(
                "Revenue by region: "
                + "; ".join(
                    region_breakdown
                )
            )

    # ==================================================
    # CATEGORY PERFORMANCE
    # ==================================================

    if (
        "Category" in df.columns
        and "Revenue" in df.columns
    ):

        category_revenue = (
            df.groupby(
                "Category"
            )["Revenue"]
            .sum()
            .sort_values(
                ascending=False
            )
        )

        if not category_revenue.empty:

            category_breakdown = []

            for category, revenue in category_revenue.items():

                category_breakdown.append(
                    f"{category}: "
                    f"₦{revenue:,.2f}"
                )

            summary.append(
                "Revenue by category: "
                + "; ".join(
                    category_breakdown
                )
            )

    return "\n".join(summary)


# ==================================================
# LOCAL BUSINESS INSIGHTS
# ==================================================

def generate_local_insights(
    df: pd.DataFrame,
) -> list:

    insights = []

    # ==================================================
    # REVENUE
    # ==================================================

    if "Revenue" in df.columns:

        revenue = (
            df["Revenue"].sum()
        )

        insights.append(
            f"Total revenue is "
            f"₦{revenue:,.0f}."
        )

    # ==================================================
    # PROFIT
    # ==================================================

    if (
        "Revenue" in df.columns
        and "Cost" in df.columns
    ):

        revenue = (
            df["Revenue"].sum()
        )

        cost = (
            df["Cost"].sum()
        )

        profit = (
            revenue - cost
        )

        margin = (
            (
                profit
                / revenue
            )
            * 100
            if revenue != 0
            else 0
        )

        insights.append(
            f"The dataset generated "
            f"₦{profit:,.0f} in profit "
            f"with a {margin:.1f}% "
            f"profit margin."
        )

    # ==================================================
    # PRODUCT
    # ==================================================

    if (
        "Product" in df.columns
        and "Revenue" in df.columns
    ):

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

            top_revenue = (
                product_revenue.iloc[0]
            )

            insights.append(
                f"{top_product} is the "
                f"highest-revenue product "
                f"at ₦{top_revenue:,.0f}."
            )

    # ==================================================
    # REGION
    # ==================================================

    if (
        "Region" in df.columns
        and "Revenue" in df.columns
    ):

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

            top_revenue = (
                region_revenue.iloc[0]
            )

            insights.append(
                f"{top_region} is the "
                f"highest-revenue region "
                f"at ₦{top_revenue:,.0f}."
            )

    # ==================================================
    # UNITS
    # ==================================================

    if "Units" in df.columns:

        units = (
            df["Units"].sum()
        )

        insights.append(
            f"A total of "
            f"{units:,.0f} units "
            f"were recorded."
        )

    if not insights:

        insights.append(
            "The dataset loaded successfully, "
            "but standard business columns such as "
            "Revenue, Cost, Product, Region, or Units "
            "were not detected."
        )

    return insights


# ==================================================
# LOCAL QUESTION ENGINE
# ==================================================

def answer_business_question(
    df: pd.DataFrame,
    question: str,
) -> str:

    if not question:

        return (
            "Please enter a question."
        )

    question_lower = (
        question
        .lower()
        .strip()
    )

    # ==================================================
    # REVENUE
    # ==================================================

    if (
        "revenue" in question_lower
        and any(
            word in question_lower
            for word in [
                "total",
                "how much",
                "overall",
            ]
        )
    ):

        if "Revenue" in df.columns:

            revenue = (
                df["Revenue"].sum()
            )

            return (
                f"Total revenue is "
                f"₦{revenue:,.0f}."
            )

        return (
            "I could not find a "
            "Revenue column in this dataset."
        )

    # ==================================================
    # PROFIT
    # ==================================================

    if "profit" in question_lower:

        if (
            "Revenue" in df.columns
            and "Cost" in df.columns
        ):

            revenue = (
                df["Revenue"].sum()
            )

            cost = (
                df["Cost"].sum()
            )

            profit = (
                revenue - cost
            )

            margin = (
                (
                    profit
                    / revenue
                )
                * 100
                if revenue != 0
                else 0
            )

            return (
                f"Total profit is "
                f"₦{profit:,.0f}, "
                f"with a profit margin "
                f"of {margin:.1f}%."
            )

        return (
            "I need Revenue and Cost "
            "columns to calculate profit."
        )

    # ==================================================
    # COST
    # ==================================================

    if "cost" in question_lower:

        if "Cost" in df.columns:

            cost = (
                df["Cost"].sum()
            )

            return (
                f"Total cost is "
                f"₦{cost:,.0f}."
            )

        return (
            "I could not find a "
            "Cost column in this dataset."
        )

    # ==================================================
    # TOP PRODUCT
    # ==================================================

    if (
        "product" in question_lower
        and any(
            word in question_lower
            for word in [
                "best",
                "top",
                "highest",
                "most",
                "performing",
                "strongest",
            ]
        )
    ):

        if (
            "Product" in df.columns
            and "Revenue" in df.columns
        ):

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

                product = (
                    product_revenue.index[0]
                )

                revenue = (
                    product_revenue.iloc[0]
                )

                return (
                    f"{product} is the "
                    f"highest-revenue product, "
                    f"generating "
                    f"₦{revenue:,.0f}."
                )

        return (
            "I need Product and Revenue "
            "columns to determine "
            "the top product."
        )

    # ==================================================
    # TOP REGION
    # ==================================================

    if (
        "region" in question_lower
        and any(
            word in question_lower
            for word in [
                "best",
                "top",
                "highest",
                "most",
                "performing",
                "strongest",
            ]
        )
    ):

        if (
            "Region" in df.columns
            and "Revenue" in df.columns
        ):

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

                region = (
                    region_revenue.index[0]
                )

                revenue = (
                    region_revenue.iloc[0]
                )

                return (
                    f"{region} is the "
                    f"highest-revenue region, "
                    f"generating "
                    f"₦{revenue:,.0f}."
                )

        return (
            "I need Region and Revenue "
            "columns to determine "
            "the top region."
        )

    # ==================================================
    # UNITS
    # ==================================================

    if (
        "unit" in question_lower
        or "units" in question_lower
    ):

        if "Units" in df.columns:

            units = (
                df["Units"].sum()
            )

            return (
                f"A total of "
                f"{units:,.0f} units "
                f"were recorded."
            )

        return (
            "I could not find a "
            "Units column in this dataset."
        )

    # ==================================================
    # SUMMARY
    # ==================================================

    if any(
        word in question_lower
        for word in [
            "summary",
            "summarize",
            "overview",
        ]
    ):

        insights = (
            generate_local_insights(
                df
            )
        )

        return "\n\n".join(
            f"• {insight}"
            for insight in insights
        )

    return (
        "I cannot answer that question "
        "with the local analytics engine."
    )


# ==================================================
# RAREMOTION AI — V5
# ==================================================

def ask_raremotion_ai(
    df: pd.DataFrame,
    question: str,
) -> tuple:

    if not question.strip():

        return (
            "Please enter a question.",
            "Local fallback",
        )

    # ==================================================
    # GET API KEY
    # ==================================================

    api_key = (
        get_openai_api_key()
    )

    # ==================================================
    # NO API KEY
    # ==================================================

    if not api_key:

        return (
            (
                "Raremotion AI connection error: "
                "OPENAI_API_KEY was not found. "
                "Check Streamlit Secrets."
            ),
            "Local fallback",
        )

    # ==================================================
    # DATASET CONTEXT
    # ==================================================

    dataset_summary = (
        prepare_dataset_summary(
            df
        )
    )

    # ==================================================
    # OPENAI CLIENT
    # ==================================================

    client = OpenAI(
        api_key=api_key
    )

    # ==================================================
    # RAREMOTION AI INSTRUCTIONS
    # ==================================================

    instructions = """
You are Raremotion AI, the business intelligence
assistant inside Raremotion Analytics.

Your job is to help users understand the business
dataset that has already been analyzed by the
Raremotion Analytics Python engine.

Rules:

1. Base your answer only on the supplied dataset
   context.

2. Never invent numbers, products, regions,
   categories, trends, or facts that are not
   supported by the supplied context.

3. If the supplied context does not contain enough
   information to answer the user's question,
   clearly say so.

4. Keep answers concise, useful, and written in
   simple business language.

5. Use Nigerian naira (₦) when discussing monetary
   values from this dataset.

6. When appropriate, explain what a result could
   mean for the business, but distinguish calculated
   facts from suggestions.

7. Do not claim that correlation proves causation.

8. You are part of Raremotion Analytics, built by
   Raremotion Labs.
"""

    user_input = f"""
DATASET CONTEXT

{dataset_summary}


USER QUESTION

{question}
"""

    # ==================================================
    # OPENAI REQUEST
    # ==================================================

    try:

        response = (
            client.responses.create(
                model="gpt-5.6-luna",
                instructions=instructions,
                input=user_input,
            )
        )

        answer = (
            response
            .output_text
            .strip()
        )

        if not answer:

            raise ValueError(
                "Raremotion AI returned "
                "an empty response."
            )

        return (
            answer,
            "AI",
        )

    # ==================================================
    # TEMPORARY DEPLOYMENT DIAGNOSTICS
    # ==================================================

    except Exception as error:

        return (
            f"Raremotion AI connection error: {error}",
            "Local fallback",
        )