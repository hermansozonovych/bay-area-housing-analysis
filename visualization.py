import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import pandas as pd


def plot_home_values(housing, output_folder):
    """Plot and save historical home values for selected cities."""
    fig, ax = plt.subplots(figsize=(12, 7))

    for city, city_data in housing.groupby("City"):
        city_data = city_data.sort_values("Date")

        ax.plot(
            city_data["Date"],
            city_data["HomeValue"],
            label=city,
            linewidth=2
        )

    ax.set_title("Housing Values in Selected Bay Area Cities")
    ax.set_xlabel("Year")
    ax.set_ylabel("Typical Home Value (USD)")

    ax.yaxis.set_major_formatter(
        FuncFormatter(
            lambda value, position: f"${value / 1_000_000:.1f}M"
        )
    )

    ax.legend(title="City", loc="upper left")
    ax.grid(True, alpha=0.3)

    fig.text(
        0.01,
        0.01,
        "Source: Zillow Research | ZHVI, All Homes, "
        "smoothed and seasonally adjusted",
        fontsize=9
    )

    fig.tight_layout(rect=(0, 0.04, 1, 1))

    output_folder.mkdir(parents=True, exist_ok=True)

    fig.savefig(
        output_folder / "housing_values_by_city.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()
    plt.close(fig)

def plot_total_growth(housing, output_folder):
    """Compare cumulative home value growth from a common start date."""
    values = housing.pivot(
        index="Date",
        columns="City",
        values="HomeValue"
    ).sort_index()

    # Use dates with values available for every selected city
    values = values.dropna()

    if values.empty:
        raise ValueError("No common dates available for comparison.")

    # Compare every month with the first common month
    growth = (values / values.iloc[0] - 1) * 100

    start_date = growth.index[0].strftime("%B %Y")

    fig, ax = plt.subplots(figsize=(12, 7))

    for city in growth.columns:
        ax.plot(
            growth.index,
            growth[city],
            label=city,
            linewidth=2
        )

    ax.set_title(
        f"Home Value Growth in Selected Bay Area Cities\n"
        f"Change Since {start_date}"
    )
    ax.set_xlabel("Year")
    ax.set_ylabel("Cumulative Change (%)")

    ax.yaxis.set_major_formatter(
        FuncFormatter(lambda value, position: f"{value:.0f}%")
    )

    ax.axhline(0, color="black", linewidth=1, linestyle="--")
    ax.legend(title="City", loc="upper left")
    ax.grid(True, alpha=0.3)

    fig.text(
        0.01,
        0.01,
        "Source: Zillow Research | ZHVI | "
        "Nominal growth, not adjusted for inflation",
        fontsize=9
    )

    fig.tight_layout(rect=(0, 0.04, 1, 1))

    output_folder.mkdir(parents=True, exist_ok=True)

    fig.savefig(
        output_folder / "housing_growth_by_city.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()
    plt.close(fig)

def plot_latest_yearly_change(housing, output_folder):
    """Compare year-over-year changes for the latest common month."""
    yearly_changes = housing.pivot(
        index="Date",
        columns="City",
        values="YearlyChangePct"
    ).sort_index().dropna()

    if yearly_changes.empty:
        raise ValueError("No common month with yearly changes available.")

    latest_date = yearly_changes.index[-1]
    changes = yearly_changes.iloc[-1].sort_values()

    # Green indicates growth; red indicates decline
    colors = [
        "#2a9d8f" if value >= 0 else "#e76f51"
        for value in changes
    ]

    fig, ax = plt.subplots(figsize=(10, 6))

    bars = ax.barh(
        changes.index,
        changes.values,
        color=colors
    )

    ax.bar_label(
        bars,
        labels=[f"{value:+.2f}%" for value in changes],
        padding=5
    )

    ax.axvline(0, color="black", linewidth=1)

    ax.set_title(
        "Annual Home Value Change in Selected Bay Area Cities\n"
        f"{latest_date:%B %Y} vs. "
        f"{latest_date - pd.DateOffset(years=1):%B %Y}"
    )
    ax.set_xlabel("Year-over-Year Change (%)")
    ax.set_ylabel("")

    ax.margins(x=0.2)
    ax.grid(axis="x", alpha=0.3)
    ax.set_axisbelow(True)

    fig.text(
        0.01,
        0.01,
        "Source: Zillow Research | ZHVI | "
        "Nominal change, not adjusted for inflation",
        fontsize=9
    )

    fig.tight_layout(rect=(0, 0.04, 1, 1))

    output_folder.mkdir(parents=True, exist_ok=True)

    fig.savefig(
        output_folder / "latest_yearly_change.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()
    plt.close(fig)