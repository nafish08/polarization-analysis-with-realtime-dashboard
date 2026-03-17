from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def iqr_outlier_summary(series: pd.Series, multiplier: float = 1.5) -> dict:
    """
    Return IQR-based outlier statistics for a numeric pandas Series.
    """
    s = series.dropna()
    if s.empty:
        return {
            "count": 0,
            "q1": np.nan,
            "q3": np.nan,
            "iqr": np.nan,
            "lower_bound": np.nan,
            "upper_bound": np.nan,
            "outlier_count": 0,
            "outlier_pct": np.nan,
        }

    q1 = s.quantile(0.25)
    q3 = s.quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - multiplier * iqr
    upper_bound = q3 + multiplier * iqr

    mask = (s < lower_bound) | (s > upper_bound)
    outlier_count = int(mask.sum())
    outlier_pct = 100 * outlier_count / len(s)

    return {
        "count": int(len(s)),
        "q1": float(q1),
        "q3": float(q3),
        "iqr": float(iqr),
        "lower_bound": float(lower_bound),
        "upper_bound": float(upper_bound),
        "outlier_count": outlier_count,
        "outlier_pct": float(outlier_pct),
    }


def save_histogram(series: pd.Series, title: str, xlabel: str, output_path: Path, bins=50):
    plt.figure(figsize=(10, 5))
    plt.hist(series.dropna(), bins=bins)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def save_boxplot(series: pd.Series, title: str, ylabel: str, output_path: Path):
    plt.figure(figsize=(6, 5))
    plt.boxplot(series.dropna(), vert=True)
    plt.title(title)
    plt.ylabel(ylabel)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def save_time_series_plot(df: pd.DataFrame, x_col: str, y_col: str, title: str, ylabel: str, output_path: Path):
    plt.figure(figsize=(12, 5))
    plt.plot(df[x_col], df[y_col], linewidth=0.8)
    plt.title(title)
    plt.xlabel("Time")
    plt.ylabel(ylabel)
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def main():
    project_root = Path(__file__).resolve().parents[1]

    input_file = project_root / "data" / "processed" / "polarization_cleaned.csv"
    figures_dir = project_root / "outputs" / "figures"
    tables_dir = project_root / "outputs" / "tables"
    logs_dir = project_root / "outputs" / "logs"

    figures_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    if not input_file.exists():
        print(f"ERROR: Cleaned data file not found:\n{input_file}")
        print("Run 02_clean_polarization_data.py first.")
        return

    print("=" * 80)
    print("STEP 3: ERROR ANALYSIS")
    print("=" * 80)

    df = pd.read_csv(input_file, parse_dates=["timestamp"])

    print(f"Loaded cleaned dataset: {input_file}")
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")

    # -------------------------------------------------------------------------
    # A1) Measurement time frame
    # -------------------------------------------------------------------------
    start_time = df["timestamp"].min()
    end_time = df["timestamp"].max()
    duration = end_time - start_time

    # -------------------------------------------------------------------------
    # A2) Data size and quantities
    # -------------------------------------------------------------------------
    memory_usage_bytes = df.memory_usage(deep=True).sum()
    memory_usage_mb = memory_usage_bytes / (1024 ** 2)
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    # -------------------------------------------------------------------------
    # A3) Pollution / suspicious values
    # -------------------------------------------------------------------------
    suspicious_summary = []

    for col in numeric_cols:
        suspicious_summary.append({
            "column": col,
            "missing_count": int(df[col].isna().sum()),
            "missing_pct": 100 * df[col].isna().sum() / len(df),
            "min": df[col].min(),
            "max": df[col].max(),
            "mean": df[col].mean(),
            "std": df[col].std(),
        })

    suspicious_df = pd.DataFrame(suspicious_summary)
    suspicious_df.to_csv(tables_dir / "column_summary_statistics.csv", index=False)

    # -------------------------------------------------------------------------
    # A4) Extreme outliers (focus on core variables)
    # -------------------------------------------------------------------------
    target_columns = [
        "azimuth_deg",
        "ellipticity_deg",
        "dop_pct",
        "docp_pct",
        "dolp_pct",
        "power_mw",
        "unpol_power_mw",
        "power_dbm",
        "unpol_power_dbm",
        "phase_difference_deg",
        "sample_interval_sec",
    ]

    outlier_rows = []
    for col in target_columns:
        if col in df.columns:
            summary = iqr_outlier_summary(df[col], multiplier=1.5)
            summary["column"] = col
            outlier_rows.append(summary)

    outlier_df = pd.DataFrame(outlier_rows)
    outlier_df = outlier_df[
        ["column", "count", "q1", "q3", "iqr", "lower_bound", "upper_bound", "outlier_count", "outlier_pct"]
    ]
    outlier_df.to_csv(tables_dir / "outlier_summary_iqr.csv", index=False)

    # -------------------------------------------------------------------------
    # A5) Physical range checks
    # These ranges are common/expected for polarization quantities.
    # They may depend on instrument convention, so present them carefully.
    # -------------------------------------------------------------------------
    range_checks = []

    # Azimuth: often expected roughly in [-90, 90] degrees
    if "azimuth_deg" in df.columns:
        s = df["azimuth_deg"]
        below = int((s < -90).sum())
        above = int((s > 90).sum())
        range_checks.append({
            "column": "azimuth_deg",
            "expected_range": "[-90, 90] deg (common convention)",
            "below_range_count": below,
            "above_range_count": above,
            "total_out_of_range": below + above,
        })

    # Ellipticity: often expected roughly in [-45, 45] degrees
    if "ellipticity_deg" in df.columns:
        s = df["ellipticity_deg"]
        below = int((s < -45).sum())
        above = int((s > 45).sum())
        range_checks.append({
            "column": "ellipticity_deg",
            "expected_range": "[-45, 45] deg (common convention)",
            "below_range_count": below,
            "above_range_count": above,
            "total_out_of_range": below + above,
        })

    # DOP: physically expected around [0, 100]%
    if "dop_pct" in df.columns:
        s = df["dop_pct"]
        below = int((s < 0).sum())
        above = int((s > 100).sum())
        range_checks.append({
            "column": "dop_pct",
            "expected_range": "[0, 100] %",
            "below_range_count": below,
            "above_range_count": above,
            "total_out_of_range": below + above,
        })

    # DOCP: often expected around [-100, 100]%
    if "docp_pct" in df.columns:
        s = df["docp_pct"]
        below = int((s < -100).sum())
        above = int((s > 100).sum())
        range_checks.append({
            "column": "docp_pct",
            "expected_range": "[-100, 100] %",
            "below_range_count": below,
            "above_range_count": above,
            "total_out_of_range": below + above,
        })

    # DOLP: often expected around [0, 100]%
    if "dolp_pct" in df.columns:
        s = df["dolp_pct"]
        below = int((s < 0).sum())
        above = int((s > 100).sum())
        range_checks.append({
            "column": "dolp_pct",
            "expected_range": "[0, 100] %",
            "below_range_count": below,
            "above_range_count": above,
            "total_out_of_range": below + above,
        })

    range_df = pd.DataFrame(range_checks)
    range_df.to_csv(tables_dir / "physical_range_checks.csv", index=False)

    # -------------------------------------------------------------------------
    # A6) Sample rate / sample interval analysis
    # -------------------------------------------------------------------------
    sample_interval = df["sample_interval_sec"].dropna()

    sample_rate_summary = {
        "sample_count": int(sample_interval.count()),
        "min_interval_sec": float(sample_interval.min()),
        "max_interval_sec": float(sample_interval.max()),
        "mean_interval_sec": float(sample_interval.mean()),
        "median_interval_sec": float(sample_interval.median()),
        "std_interval_sec": float(sample_interval.std()),
    }

    if sample_interval.mean() > 0:
        sample_rate_summary["effective_sample_rate_hz"] = float(1.0 / sample_interval.mean())
    else:
        sample_rate_summary["effective_sample_rate_hz"] = np.nan

    sample_rate_df = pd.DataFrame([sample_rate_summary])
    sample_rate_df.to_csv(tables_dir / "sample_rate_summary.csv", index=False)

    # -------------------------------------------------------------------------
    # Figures
    # -------------------------------------------------------------------------
    if "sample_interval_sec" in df.columns:
        save_histogram(
            df["sample_interval_sec"],
            "Histogram of Sample Intervals",
            "Sample interval [s]",
            figures_dir / "sample_interval_histogram.png",
            bins=50
        )

    if "azimuth_deg" in df.columns:
        save_boxplot(
            df["azimuth_deg"],
            "Boxplot of Azimuth",
            "Azimuth [deg]",
            figures_dir / "azimuth_boxplot.png"
        )
        save_time_series_plot(
            df, "timestamp", "azimuth_deg",
            "Azimuth over Time",
            "Azimuth [deg]",
            figures_dir / "azimuth_time_series.png"
        )

    if "ellipticity_deg" in df.columns:
        save_boxplot(
            df["ellipticity_deg"],
            "Boxplot of Ellipticity",
            "Ellipticity [deg]",
            figures_dir / "ellipticity_boxplot.png"
        )
        save_time_series_plot(
            df, "timestamp", "ellipticity_deg",
            "Ellipticity over Time",
            "Ellipticity [deg]",
            figures_dir / "ellipticity_time_series.png"
        )

    if "dop_pct" in df.columns:
        save_boxplot(
            df["dop_pct"],
            "Boxplot of DOP",
            "DOP [%]",
            figures_dir / "dop_boxplot.png"
        )

    # -------------------------------------------------------------------------
    # Text report
    # -------------------------------------------------------------------------
    report_path = logs_dir / "error_analysis_report.txt"
    with report_path.open("w", encoding="utf-8") as report:
        report.write("ERROR ANALYSIS REPORT\n")
        report.write("=" * 80 + "\n\n")

        report.write("A) MEASUREMENT TIME FRAME\n")
        report.write("-" * 80 + "\n")
        report.write(f"Start timestamp: {start_time}\n")
        report.write(f"End timestamp:   {end_time}\n")
        report.write(f"Total duration:  {duration}\n\n")

        report.write("B) DATA SIZE AND QUANTITIES\n")
        report.write("-" * 80 + "\n")
        report.write(f"Rows: {len(df)}\n")
        report.write(f"Columns: {len(df.columns)}\n")
        report.write(f"Memory usage: {memory_usage_mb:.3f} MB\n")
        report.write("Numeric columns:\n")
        for col in numeric_cols:
            report.write(f"  - {col}\n")
        report.write("\n")

        report.write("C) SUSPICIOUS / MISSING VALUES SUMMARY\n")
        report.write("-" * 80 + "\n")
        report.write(suspicious_df.to_string(index=False))
        report.write("\n\n")

        report.write("D) IQR OUTLIER SUMMARY\n")
        report.write("-" * 80 + "\n")
        report.write(outlier_df.to_string(index=False))
        report.write("\n\n")

        report.write("E) PHYSICAL RANGE CHECKS\n")
        report.write("-" * 80 + "\n")
        report.write(range_df.to_string(index=False))
        report.write("\n\n")

        report.write("F) SAMPLE INTERVAL ANALYSIS\n")
        report.write("-" * 80 + "\n")
        for key, value in sample_rate_summary.items():
            report.write(f"{key}: {value}\n")
        report.write("\n")

        report.write("G) DISCUSSION NOTES\n")
        report.write("-" * 80 + "\n")
        report.write(
            "The expected polarization ranges depend on the instrument convention. "
            "The checks here use common conventions for azimuth, ellipticity, and degree-of-polarization variables.\n"
        )
        report.write(
            "IQR outlier detection identifies statistically extreme values, but not all such points are necessarily non-physical.\n"
        )
        report.write(
            "For final reporting, visually inspect the generated plots before deciding whether any values should be removed.\n"
        )

    # -------------------------------------------------------------------------
    # Console summary
    # -------------------------------------------------------------------------
    print("\nMeasurement time frame:")
    print(f"Start:    {start_time}")
    print(f"End:      {end_time}")
    print(f"Duration: {duration}")

    print("\nData size:")
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")
    print(f"Memory usage: {memory_usage_mb:.3f} MB")

    print("\nSample interval summary:")
    for key, value in sample_rate_summary.items():
        print(f"{key}: {value}")

    print("\nPhysical range checks:")
    print(range_df.to_string(index=False))

    print("\nSaved outputs:")
    print(f"  Figures: {figures_dir}")
    print(f"  Tables:  {tables_dir}")
    print(f"  Report:  {report_path}")

    print("\nDone.")


if __name__ == "__main__":
    main()