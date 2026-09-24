import pandas as pd


def prepare_dataset_summary(df: pd.DataFrame) -> str:
    """Prepare a compact business summary for AI analysis."""

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
        f"Total missing values: {int(df.isna().sum().sum())}"
    )

    summary.append(
        f"Duplicate rows: {int(df.duplicated().sum())}"
    )

    # Revenue
    if "Revenue" in df.columns:
        total_revenue = df["Revenue"].sum()

        summary.append(
            f"Total revenue: {total_revenue:,.2f}"
        )

    # Cost
    if "Cost" in df.columns:
        total_cost = df["Cost"].sum()

        summary.append(
            f"Total cost: {total_cost:,.2f}"
        )

    # Profit
    if (
        "Revenue" in df.columns
        and "Cost" in df.columns
    ):
        total_profit = (
            df["Revenue"].sum()
            - df["Cost"].sum()
        )

        summary.append(
            f"Total profit: {total_profit:,.2f}"
        )

    # Top product
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

    # Top region
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
    """Generate business insights without an external AI API."""

    insights = []

    # Revenue insight
    if "Revenue" in df.columns:
        revenue = df["Revenue"].sum()

        insights.append(
            f"Total revenue is ₦{revenue:,.0f}."
        )

    # Profit insight
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
            f"The dataset generated ₦{profit:,.0f} "
            f"in profit with a {margin:.1f}% "
            f"profit margin."
        )

    # Product insight
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
                f"{top_product} is the highest-revenue "
                f"product at ₦{top_revenue:,.0f}."
            )

    # Region insight
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
                f"{top_region} is the highest-revenue "
                f"region at ₦{top_revenue:,.0f}."
            )

    # Units insight
    if "Units" in df.columns:
        units = df["Units"].sum()

        insights.append(
            f"A total of {units:,.0f} units were recorded."
        )

    if not insights:
        insights.append(
            "The dataset loaded successfully, but standard "
            "business columns such as Revenue, Cost, Product, "
            "Region, or Units were not detected."
        )

    return insights