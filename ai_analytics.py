import pandas as pd


def prepare_dataset_summary(df: pd.DataFrame) -> str:
    """
    Prepare a compact business summary of the dataset.
    """

    summary = []

    summary.append(f"Number of rows: {len(df)}")
    summary.append(f"Number of columns: {len(df.columns)}")

    summary.append(
        "Columns: " + ", ".join(df.columns.astype(str))
    )

    numeric_columns = (
        df.select_dtypes(include="number")
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

    if "Revenue" in df.columns:
        total_revenue = df["Revenue"].sum()

        summary.append(
            f"Total revenue: "
            f"{total_revenue:,.2f}"
        )

    if "Cost" in df.columns:
        total_cost = df["Cost"].sum()

        summary.append(
            f"Total cost: "
            f"{total_cost:,.2f}"
        )

    if (
        "Revenue" in df.columns
        and "Cost" in df.columns
    ):
        total_profit = (
            df["Revenue"].sum()
            - df["Cost"].sum()
        )

        summary.append(
            f"Total profit: "
            f"{total_profit:,.2f}"
        )

    if (
        "Product" in df.columns
        and "Revenue" in df.columns
    ):
        product_revenue = (
            df.groupby("Product")["Revenue"]
            .sum()
            .sort_values(ascending=False)
        )

        if not product_revenue.empty:
            summary.append(
                f"Top product by revenue: "
                f"{product_revenue.index[0]} "
                f"({product_revenue.iloc[0]:,.2f})"
            )

    if (
        "Region" in df.columns
        and "Revenue" in df.columns
    ):
        region_revenue = (
            df.groupby("Region")["Revenue"]
            .sum()
            .sort_values(ascending=False)
        )

        if not region_revenue.empty:
            summary.append(
                f"Top region by revenue: "
                f"{region_revenue.index[0]} "
                f"({region_revenue.iloc[0]:,.2f})"
            )

    return "\n".join(summary)


def generate_local_insights(df: pd.DataFrame) -> list:
    """
    Generate automatic business insights locally.
    """

    insights = []

    if "Revenue" in df.columns:
        revenue = df["Revenue"].sum()

        insights.append(
            f"Total revenue is ₦{revenue:,.0f}."
        )

    if (
        "Revenue" in df.columns
        and "Cost" in df.columns
    ):
        revenue = df["Revenue"].sum()
        cost = df["Cost"].sum()

        profit = revenue - cost

        margin = (
            (profit / revenue) * 100
            if revenue != 0
            else 0
        )

        insights.append(
            f"The dataset generated "
            f"₦{profit:,.0f} in profit "
            f"with a {margin:.1f}% profit margin."
        )

    if (
        "Product" in df.columns
        and "Revenue" in df.columns
    ):
        product_revenue = (
            df.groupby("Product")["Revenue"]
            .sum()
            .sort_values(ascending=False)
        )

        if not product_revenue.empty:
            top_product = product_revenue.index[0]
            top_revenue = product_revenue.iloc[0]

            insights.append(
                f"{top_product} is the "
                f"highest-revenue product "
                f"at ₦{top_revenue:,.0f}."
            )

    if (
        "Region" in df.columns
        and "Revenue" in df.columns
    ):
        region_revenue = (
            df.groupby("Region")["Revenue"]
            .sum()
            .sort_values(ascending=False)
        )

        if not region_revenue.empty:
            top_region = region_revenue.index[0]
            top_revenue = region_revenue.iloc[0]

            insights.append(
                f"{top_region} is the "
                f"highest-revenue region "
                f"at ₦{top_revenue:,.0f}."
            )

    if "Units" in df.columns:
        units = df["Units"].sum()

        insights.append(
            f"A total of "
            f"{units:,.0f} units were recorded."
        )

    if not insights:
        insights.append(
            "The dataset loaded successfully, "
            "but standard business columns such as "
            "Revenue, Cost, Product, Region, or Units "
            "were not detected."
        )

    return insights


def answer_business_question(
    df: pd.DataFrame,
    question: str,
) -> str:
    """
    Answer common business questions using
    the uploaded dataset.

    This is the local V4 question engine.
    """

    if not question:
        return "Please enter a question."

    question_lower = question.lower().strip()

    # ----------------------------------------------
    # TOTAL REVENUE
    # ----------------------------------------------

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
            revenue = df["Revenue"].sum()

            return (
                f"Total revenue is "
                f"₦{revenue:,.0f}."
            )

        return (
            "I could not find a Revenue "
            "column in this dataset."
        )

    # ----------------------------------------------
    # PROFIT
    # ----------------------------------------------

    if "profit" in question_lower:
        if (
            "Revenue" in df.columns
            and "Cost" in df.columns
        ):
            revenue = df["Revenue"].sum()
            cost = df["Cost"].sum()

            profit = revenue - cost

            margin = (
                (profit / revenue) * 100
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
            "I need Revenue and Cost columns "
            "to calculate profit."
        )

    # ----------------------------------------------
    # COST
    # ----------------------------------------------

    if "cost" in question_lower:
        if "Cost" in df.columns:
            cost = df["Cost"].sum()

            return (
                f"Total cost is "
                f"₦{cost:,.0f}."
            )

        return (
            "I could not find a Cost "
            "column in this dataset."
        )

    # ----------------------------------------------
    # BEST / TOP PRODUCT
    # ----------------------------------------------

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
            ]
        )
    ):
        if (
            "Product" in df.columns
            and "Revenue" in df.columns
        ):
            product_revenue = (
                df.groupby("Product")["Revenue"]
                .sum()
                .sort_values(ascending=False)
            )

            if not product_revenue.empty:
                product = product_revenue.index[0]
                revenue = product_revenue.iloc[0]

                return (
                    f"{product} is the "
                    f"highest-revenue product, "
                    f"generating ₦{revenue:,.0f}."
                )

        return (
            "I need Product and Revenue columns "
            "to determine the top product."
        )

    # ----------------------------------------------
    # BEST / TOP REGION
    # ----------------------------------------------

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
            ]
        )
    ):
        if (
            "Region" in df.columns
            and "Revenue" in df.columns
        ):
            region_revenue = (
                df.groupby("Region")["Revenue"]
                .sum()
                .sort_values(ascending=False)
            )

            if not region_revenue.empty:
                region = region_revenue.index[0]
                revenue = region_revenue.iloc[0]

                return (
                    f"{region} is the "
                    f"highest-revenue region, "
                    f"generating ₦{revenue:,.0f}."
                )

        return (
            "I need Region and Revenue columns "
            "to determine the top region."
        )

    # ----------------------------------------------
    # UNITS
    # ----------------------------------------------

    if (
        "unit" in question_lower
        or "units" in question_lower
    ):
        if "Units" in df.columns:
            units = df["Units"].sum()

            return (
                f"A total of "
                f"{units:,.0f} units "
                f"were recorded."
            )

        return (
            "I could not find a Units "
            "column in this dataset."
        )

    # ----------------------------------------------
    # SUMMARY
    # ----------------------------------------------

    if any(
        word in question_lower
        for word in [
            "summary",
            "summarize",
            "overview",
        ]
    ):
        insights = generate_local_insights(df)

        return "\n\n".join(
            f"• {insight}"
            for insight in insights
        )

    # ----------------------------------------------
    # HELP
    # ----------------------------------------------

    return (
        "I cannot answer that question locally yet. "
        "Try asking about total revenue, profit, cost, "
        "top product, top region, total units, "
        "or ask me to summarize the business."
    )