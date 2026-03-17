from pathlib import Path
import pandas as pd
import numpy as np


def safe_corr(x: pd.Series, y: pd.Series) -> float:
    """
    Compute Pearson correlation safely.
    Returns NaN if there are not enough valid paired samples.
    """
    valid = pd.DataFrame({"x": x, "y": y}).dropna()
    if len(valid) < 2:
        return np.nan
    return valid["x"].corr(valid["y"])


def safe_linear_slope(x: pd.Series, y: pd.Series) -> float:
    """
    Compute simple linear regression slope y = a*x + b safely.
    Returns NaN if there are not enough valid paired samples or x has no variance.
    """
    valid = pd.DataFrame({"x": x, "y": y}).dropna()
    if len(valid) < 2:
        return np.nan
    if valid["x"].nunique() < 2:
        return np.nan

    slope, intercept = np.polyfit(valid["x"], valid["y"], 1)
    return slope


def main():
    project_root = Path(__file__).resolve().parents[1]

    input_file = project_root / "data" / "processed" / "polarization_weather_merged_hourly.csv"
    tables_dir = project_root / "outputs" / "tables"
    logs_dir = project_root / "outputs" / "logs"

    tables_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    if not input_file.exists():
        print(f"ERROR: Input file not found:\n{input_file}")
        print("Run 06_merge_datasets.py first.")
        return

    print("=" * 80)
    print("STEP 7: DAILY CORRELATION ANALYSIS")
    print("=" * 80)

    df = pd.read_csv(input_file, parse_dates=["timestamp", "sunrise_local", "sunset_local"])

    if "surface_pressure_hpa" not in df.columns:
        print("ERROR: surface_pressure_hpa column not found.")
        return

    df["date"] = df["timestamp"].dt.date

    results = []

    for current_date, day_df in df.groupby("date"):
        row = {
            "date": current_date,
            "hourly_samples": len(day_df),

            "azimuth_mean_deg": day_df["azimuth_deg"].mean(),
            "azimuth_std_deg": day_df["azimuth_deg"].std(),
            "azimuth_min_deg": day_df["azimuth_deg"].min(),
            "azimuth_max_deg": day_df["azimuth_deg"].max(),
            "azimuth_range_deg": day_df["azimuth_deg"].max() - day_df["azimuth_deg"].min(),

            "ellipticity_mean_deg": day_df["ellipticity_deg"].mean(),
            "ellipticity_std_deg": day_df["ellipticity_deg"].std(),
            "ellipticity_min_deg": day_df["ellipticity_deg"].min(),
            "ellipticity_max_deg": day_df["ellipticity_deg"].max(),
            "ellipticity_range_deg": day_df["ellipticity_deg"].max() - day_df["ellipticity_deg"].min(),

            "surface_pressure_mean_hpa": day_df["surface_pressure_hpa"].mean(),
            "surface_pressure_std_hpa": day_df["surface_pressure_hpa"].std(),
            "surface_pressure_min_hpa": day_df["surface_pressure_hpa"].min(),
            "surface_pressure_max_hpa": day_df["surface_pressure_hpa"].max(),
            "surface_pressure_range_hpa": day_df["surface_pressure_hpa"].max() - day_df["surface_pressure_hpa"].min(),

            "corr_azimuth_vs_pressure": safe_corr(day_df["surface_pressure_hpa"], day_df["azimuth_deg"]),
            "corr_ellipticity_vs_pressure": safe_corr(day_df["surface_pressure_hpa"], day_df["ellipticity_deg"]),

            "slope_azimuth_vs_pressure": safe_linear_slope(day_df["surface_pressure_hpa"], day_df["azimuth_deg"]),
            "slope_ellipticity_vs_pressure": safe_linear_slope(day_df["surface_pressure_hpa"], day_df["ellipticity_deg"]),

            "daylight_hours_in_dataset": day_df["is_daylight"].sum() if "is_daylight" in day_df.columns else np.nan,
        }
        results.append(row)

    results_df = pd.DataFrame(results).sort_values("date").reset_index(drop=True)

    output_table = tables_dir / "daily_correlation_results.csv"
    results_df.to_csv(output_table, index=False)

    report_file = logs_dir / "daily_correlation_report.txt"
    with report_file.open("w", encoding="utf-8") as report:
        report.write("DAILY CORRELATION ANALYSIS REPORT\n")
        report.write("=" * 80 + "\n\n")

        report.write(f"Input file: {input_file}\n")
        report.write(f"Number of daily groups: {len(results_df)}\n\n")

        report.write("RESULTS TABLE\n")
        report.write("-" * 80 + "\n")
        report.write(results_df.to_string(index=False))
        report.write("\n\n")

        report.write("INTERPRETATION NOTES\n")
        report.write("-" * 80 + "\n")
        report.write(
            "Pearson correlation values close to +1 or -1 indicate stronger linear association.\n"
        )
        report.write(
            "Values near 0 indicate weak or no linear relationship.\n"
        )
        report.write(
            "The regression slope shows how strongly azimuth or ellipticity changes per 1 hPa pressure change.\n"
        )
        report.write(
            "With only a few hourly points per day, daily correlations should be interpreted cautiously.\n"
        )

    print("\nDaily correlation results:")
    print(results_df.to_string(index=False))

    print(f"\nDaily correlation table saved to:\n{output_table}")
    print(f"Daily correlation report saved to:\n{report_file}")

    print("\nDone.")


if __name__ == "__main__":
    main()