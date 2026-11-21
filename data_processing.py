import pandas as pd


SELECTED_CITIES = [
    "San Jose",
    "Santa Clara",
    "Sunnyvale",
    "Mountain View",
    "Palo Alto",
    "Fremont",
    "Oakland",
    "San Francisco"
]


def load_and_prepare_data(file_path):
    """Load Zillow data and reshape selected cities into long format."""
    df = pd.read_csv(file_path)

    # Select cities in California
    housing = df.loc[
        (df["State"] == "CA")
        & (df["RegionName"].isin(SELECTED_CITIES))
    ].copy()

    missing_cities = set(SELECTED_CITIES) - set(housing["RegionName"])

    if missing_cities:
        raise ValueError(f"Cities not found: {sorted(missing_cities)}")

    # Identify monthly value columns
    date_columns = df.columns[
        df.columns.str.fullmatch(r"\d{4}-\d{2}-\d{2}")
    ].tolist()

    if not date_columns:
        raise ValueError("No monthly columns found.")

    identifiers = ["RegionID", "RegionName", "State", "CountyName"]
    housing = housing[identifiers + date_columns]

    # Remove completely identical rows
    housing = housing.drop_duplicates()

    # Convert monthly columns into rows
    housing_long = housing.melt(
        id_vars=identifiers,
        value_vars=date_columns,
        var_name="Date",
        value_name="HomeValue"
    )

    housing_long = housing_long.rename(
        columns={"RegionName": "City"}
    )

    # Convert column types
    housing_long["Date"] = pd.to_datetime(
        housing_long["Date"],
        format="%Y-%m-%d",
        errors="raise"
    )

    housing_long["HomeValue"] = pd.to_numeric(
        housing_long["HomeValue"],
        errors="raise"
    )

    return housing_long.sort_values(
        ["RegionID", "Date"]
    ).reset_index(drop=True)


def validate_data(housing):
    """Check data quality and monthly continuity."""
    missing_values = (
        housing.groupby("City")["HomeValue"]
        .apply(lambda values: values.isna().sum())
    )

    duplicate_count = housing.duplicated(
        subset=["RegionID", "Date"]
    ).sum()

    invalid_count = (housing["HomeValue"] <= 0).sum()

    print("\nMissing home values by city:")
    print(missing_values)
    print("\nDuplicate city-month observations:", duplicate_count)
    print("Zero or negative home values:", invalid_count)
    print("Total observations:", len(housing))

    # Stop if data needs further investigation
    if missing_values.sum() > 0:
        raise ValueError("Missing home values require review.")

    if duplicate_count > 0:
        raise ValueError("Duplicate city-month observations require review.")

    if invalid_count > 0:
        raise ValueError("Zero or negative home values require review.")

    for region_id, group in housing.groupby("RegionID"):
        months = group["Date"].sort_values().dt.to_period("M")

        expected_months = pd.period_range(
            start=months.min(),
            end=months.max(),
            freq="M"
        )

        if months.tolist() != expected_months.tolist():
            raise ValueError(
                f"Missing or repeated months for region {region_id}"
            )


def calculate_changes(housing):
    """Calculate monthly and yearly percentage changes."""
    housing = housing.copy()

    housing = housing.sort_values(
        ["RegionID", "Date"]
    ).reset_index(drop=True)

    city_values = housing.groupby("RegionID")["HomeValue"]

    housing["MonthlyChangePct"] = (
        city_values.pct_change(periods=1, fill_method=None) * 100
    )

    housing["YearlyChangePct"] = (
        city_values.pct_change(periods=12, fill_method=None) * 100
    )

    return housing

def create_summary(housing):
    """Summarize housing values over a common analysis period."""
    values = housing.pivot(
        index="Date",
        columns="City",
        values="HomeValue"
    ).sort_index().dropna()

    if values.empty:
        raise ValueError("No common dates available for comparison.")

    start_date = values.index[0]
    end_date = values.index[-1]

    summary = pd.DataFrame({
        "StartValue": values.iloc[0],
        "EndValue": values.iloc[-1]
    })

    summary.index.name = "City"

    summary["TotalChangeUSD"] = (
            summary["EndValue"] - summary["StartValue"]
    )

    summary["TotalGrowthPct"] = (
                                        summary["EndValue"] / summary["StartValue"] - 1
                                ) * 100

    # Match annual changes to the same end date
    yearly_changes = (
        housing.loc[housing["Date"] == end_date]
        .set_index("City")["YearlyChangePct"]
    )

    summary["LatestYearlyChangePct"] = yearly_changes
    summary["StartDate"] = start_date
    summary["EndDate"] = end_date

    return (
        summary.reset_index()
        .sort_values("TotalGrowthPct", ascending=False)
        .reset_index(drop=True)
    )