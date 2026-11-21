from pathlib import Path

from data_processing import (
    load_and_prepare_data,
    validate_data,
    calculate_changes,
    create_summary
)

from visualization import (
    plot_home_values,
    plot_total_growth,
    plot_latest_yearly_change
)


def main():
    # Define project paths
    project_folder = Path(__file__).resolve().parent
    file_path = project_folder / "data" / "zillow_city_zhvi.csv"
    output_folder = project_folder / "outputs"

    # Prepare and validate the data
    housing = load_and_prepare_data(file_path)
    validate_data(housing)

    # Calculate changes and create the summary
    housing = calculate_changes(housing)
    summary = create_summary(housing)

    # Save analysis tables
    output_folder.mkdir(parents=True, exist_ok=True)

    housing.to_csv(
        output_folder / "housing_processed.csv",
        index=False,
        date_format="%Y-%m-%d"
    )

    summary.to_csv(
        output_folder / "housing_summary.csv",
        index=False,
        date_format="%Y-%m-%d"
    )

    # Display the latest values for each city
    latest_values = (
        housing.groupby("RegionID")
        .tail(1)
        .sort_values("City")
    )

    print("\nLatest housing values and growth:")
    print(
        latest_values[
            [
                "City",
                "Date",
                "HomeValue",
                "MonthlyChangePct",
                "YearlyChangePct"
            ]
        ].round({
            "HomeValue": 2,
            "MonthlyChangePct": 2,
            "YearlyChangePct": 2
        }).to_string(index=False)
    )

    # Display the summary
    display_summary = summary.copy()
    numeric_columns = display_summary.select_dtypes(
        include="number"
    ).columns

    display_summary[numeric_columns] = (
        display_summary[numeric_columns].round(2)
    )

    print("\nHousing market summary:")
    print(display_summary.to_string(index=False))

    # Create and save charts
    plot_home_values(housing, output_folder)
    plot_total_growth(housing, output_folder)
    plot_latest_yearly_change(housing, output_folder)


if __name__ == "__main__":
    main()