from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def compute_regression(x: pd.Series, y: pd.Series):
    """
    Compute linear regression y = a*x + b
    Returns slope, intercept, and valid data count.
    """
    df = pd.DataFrame({"x": x, "y": y}).dropna()

    if len(df) < 2 or df["x"].nunique() < 2:
        return np.nan, np.nan, len(df)

    slope, intercept = np.polyfit(df["x"], df["y"], 1)
    return slope, intercept, len(df)


def main():
    project_root = Path(__file__).resolve().parents[1]

    input_file = project_root / "data" / "processed" / "polarization_weather_merged_hourly.csv"
    figures_dir = project_root / "outputs" / "figures"
    tables_dir = project_root / "outputs" / "tables"
    logs_dir = project_root / "outputs" / "logs"

    figures_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    if not input_file.exists():
        print(f"ERROR: Input file not found:\n{input_file}")
        print("Run 06_merge_datasets.py first.")
        return

    print("=" * 80)
    print("STEP 8: FULL TREND ANALYSIS")
    print("=" * 80)

    df = pd.read_csv(input_file, parse_dates=["timestamp"])

    # -------------------------------------------------------------------------
    # Global correlations
    # -------------------------------------------------------------------------
    corr_az = df["azimuth_deg"].corr(df["surface_pressure_hpa"])
    corr_el = df["ellipticity_deg"].corr(df["surface_pressure_hpa"])

    slope_az, intercept_az, n_az = compute_regression(
        df["surface_pressure_hpa"], df["azimuth_deg"]
    )

    slope_el, intercept_el, n_el = compute_regression(
        df["surface_pressure_hpa"], df["ellipticity_deg"]
    )

    # -------------------------------------------------------------------------
    # Save summary table
    # -------------------------------------------------------------------------
    summary_df = pd.DataFrame([{
        "corr_azimuth_vs_pressure": corr_az,
        "corr_ellipticity_vs_pressure": corr_el,
        "slope_azimuth_vs_pressure": slope_az,
        "slope_ellipticity_vs_pressure": slope_el,
        "valid_samples_azimuth": n_az,
        "valid_samples_ellipticity": n_el
    }])

    summary_file = tables_dir / "global_trend_summary.csv"
    summary_df.to_csv(summary_file, index=False)

    # -------------------------------------------------------------------------
    # TIME SERIES PLOTS
    # -------------------------------------------------------------------------
    # Azimuth
    plt.figure(figsize=(12, 5))
    plt.plot(df["timestamp"], df["azimuth_deg"], label="Azimuth")
    plt.title("Azimuth over Time")
    plt.xlabel("Time")
    plt.ylabel("Azimuth [deg]")
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig(figures_dir / "azimuth_trend.png", dpi=200)
    plt.close()

    # Ellipticity
    plt.figure(figsize=(12, 5))
    plt.plot(df["timestamp"], df["ellipticity_deg"], label="Ellipticity")
    plt.title("Ellipticity over Time")
    plt.xlabel("Time")
    plt.ylabel("Ellipticity [deg]")
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig(figures_dir / "ellipticity_trend.png", dpi=200)
    plt.close()

    # Surface pressure
    plt.figure(figsize=(12, 5))
    plt.plot(df["timestamp"], df["surface_pressure_hpa"], label="Pressure")
    plt.title("Surface Pressure over Time")
    plt.xlabel("Time")
    plt.ylabel("Pressure [hPa]")
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig(figures_dir / "pressure_trend.png", dpi=200)
    plt.close()

    # -------------------------------------------------------------------------
    # SCATTER PLOTS + REGRESSION LINE
    # -------------------------------------------------------------------------
    # Azimuth vs pressure
    plt.figure(figsize=(6, 5))
    plt.scatter(df["surface_pressure_hpa"], df["azimuth_deg"], alpha=0.5)

    if not np.isnan(slope_az):
        x_vals = np.linspace(df["surface_pressure_hpa"].min(), df["surface_pressure_hpa"].max(), 100)
        y_vals = slope_az * x_vals + intercept_az
        plt.plot(x_vals, y_vals)

    plt.title("Azimuth vs Surface Pressure")
    plt.xlabel("Surface Pressure [hPa]")
    plt.ylabel("Azimuth [deg]")
    plt.tight_layout()
    plt.savefig(figures_dir / "azimuth_vs_pressure.png", dpi=200)
    plt.close()

    # Ellipticity vs pressure
    plt.figure(figsize=(6, 5))
    plt.scatter(df["surface_pressure_hpa"], df["ellipticity_deg"], alpha=0.5)

    if not np.isnan(slope_el):
        x_vals = np.linspace(df["surface_pressure_hpa"].min(), df["surface_pressure_hpa"].max(), 100)
        y_vals = slope_el * x_vals + intercept_el
        plt.plot(x_vals, y_vals)

    plt.title("Ellipticity vs Surface Pressure")
    plt.xlabel("Surface Pressure [hPa]")
    plt.ylabel("Ellipticity [deg]")
    plt.tight_layout()
    plt.savefig(figures_dir / "ellipticity_vs_pressure.png", dpi=200)
    plt.close()

    # -------------------------------------------------------------------------
    # REPORT
    # -------------------------------------------------------------------------
    report_file = logs_dir / "trend_analysis_report.txt"
    with report_file.open("w", encoding="utf-8") as report:
        report.write("GLOBAL TREND ANALYSIS REPORT\n")
        report.write("=" * 80 + "\n\n")

        report.write("CORRELATION RESULTS\n")
        report.write("-" * 80 + "\n")
        report.write(f"Azimuth vs Pressure:     {corr_az}\n")
        report.write(f"Ellipticity vs Pressure: {corr_el}\n\n")

        report.write("LINEAR REGRESSION\n")
        report.write("-" * 80 + "\n")
        report.write(f"Azimuth slope:     {slope_az}\n")
        report.write(f"Ellipticity slope: {slope_el}\n\n")

        report.write("INTERPRETATION\n")
        report.write("-" * 80 + "\n")
        report.write(
            "Low correlation values indicate weak or no linear relationship between polarization and pressure.\n"
        )
        report.write(
            "The slope represents the change in polarization per 1 hPa pressure change.\n"
        )

    # -------------------------------------------------------------------------
    # Console output
    # -------------------------------------------------------------------------
    print("\nGLOBAL RESULTS:")
    print(f"Correlation (Azimuth vs Pressure):     {corr_az}")
    print(f"Correlation (Ellipticity vs Pressure): {corr_el}")

    print(f"\nSlope (Azimuth vs Pressure):     {slope_az}")
    print(f"Slope (Ellipticity vs Pressure): {slope_el}")

    print(f"\nSummary saved to:\n{summary_file}")
    print(f"Figures saved to:\n{figures_dir}")
    print(f"Report saved to:\n{report_file}")

    print("\nDone.")


if __name__ == "__main__":
    main()