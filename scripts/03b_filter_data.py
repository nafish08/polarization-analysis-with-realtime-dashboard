from pathlib import Path
import pandas as pd
import numpy as np


def apply_range_filter(df: pd.DataFrame, column: str, min_val=None, max_val=None):
    """
    Replace out-of-range values in a column with NaN.
    Returns the modified dataframe and the count of replaced values.
    """
    if column not in df.columns:
        return df, 0

    mask = pd.Series(False, index=df.index)

    if min_val is not None:
        mask |= df[column] < min_val
    if max_val is not None:
        mask |= df[column] > max_val

    replaced_count = int(mask.sum())
    df.loc[mask, column] = np.nan
    return df, replaced_count


def main():
    project_root = Path(__file__).resolve().parents[1]

    input_file = project_root / "data" / "processed" / "polarization_cleaned.csv"
    output_file = project_root / "data" / "processed" / "polarization_filtered.csv"
    logs_dir = project_root / "outputs" / "logs"
    tables_dir = project_root / "outputs" / "tables"

    logs_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)

    if not input_file.exists():
        print(f"ERROR: Input file not found:\n{input_file}")
        print("Run 02_clean_polarization_data.py first.")
        return

    print("=" * 80)
    print("STEP 3B: LIGHT FILTERING OF NON-PHYSICAL VALUES")
    print("=" * 80)

    df = pd.read_csv(input_file, parse_dates=["timestamp"])
    filtered_df = df.copy()

    original_rows = len(filtered_df)

    filter_summary = []

    # -------------------------------------------------------------------------
    # Core physical range filters
    # -------------------------------------------------------------------------
    rules = [
        ("azimuth_deg", -90, 90, "Common azimuth convention"),
        ("ellipticity_deg", -45, 45, "Common ellipticity convention"),
        ("dop_pct", 0, 100, "Degree of polarization physically expected in [0,100]"),
        ("docp_pct", -100, 100, "Degree of circular polarization expected in [-100,100]"),
        ("dolp_pct", 0, 100, "Degree of linear polarization expected in [0,100]"),
        ("power_mw", 0, None, "Optical power should not be negative"),
        ("pol_power_mw", 0, None, "Polarized power should not be negative"),
        ("unpol_power_mw", 0, None, "Unpolarized power should not be negative"),
        ("sample_interval_sec", 0, None, "Sample interval should be positive"),
    ]

    for column, min_val, max_val, reason in rules:
        before_missing = filtered_df[column].isna().sum() if column in filtered_df.columns else None
        filtered_df, replaced_count = apply_range_filter(filtered_df, column, min_val, max_val)
        after_missing = filtered_df[column].isna().sum() if column in filtered_df.columns else None

        filter_summary.append({
            "column": column,
            "min_allowed": min_val,
            "max_allowed": max_val,
            "newly_replaced_with_nan": replaced_count,
            "missing_before": int(before_missing) if before_missing is not None else None,
            "missing_after": int(after_missing) if after_missing is not None else None,
            "reason": reason
        })

    # -------------------------------------------------------------------------
    # Optional row-level filtering rule:
    # Only remove rows if timestamp is missing (should already be clean)
    # -------------------------------------------------------------------------
    invalid_timestamp_rows = int(filtered_df["timestamp"].isna().sum())
    filtered_df = filtered_df.dropna(subset=["timestamp"]).copy()

    # -------------------------------------------------------------------------
    # Save filtered data
    # -------------------------------------------------------------------------
    filtered_df.to_csv(output_file, index=False)

    summary_df = pd.DataFrame(filter_summary)
    summary_table_file = tables_dir / "filtering_summary.csv"
    summary_df.to_csv(summary_table_file, index=False)

    # -------------------------------------------------------------------------
    # Write log report
    # -------------------------------------------------------------------------
    report_file = logs_dir / "filtering_report.txt"
    with report_file.open("w", encoding="utf-8") as report:
        report.write("FILTERING REPORT\n")
        report.write("=" * 80 + "\n\n")

        report.write("INPUT / OUTPUT\n")
        report.write("-" * 80 + "\n")
        report.write(f"Input file:  {input_file}\n")
        report.write(f"Output file: {output_file}\n\n")

        report.write("ROW COUNTS\n")
        report.write("-" * 80 + "\n")
        report.write(f"Original rows: {original_rows}\n")
        report.write(f"Filtered rows: {len(filtered_df)}\n")
        report.write(f"Rows removed due to invalid timestamp: {invalid_timestamp_rows}\n\n")

        report.write("FILTER RULES SUMMARY\n")
        report.write("-" * 80 + "\n")
        report.write(summary_df.to_string(index=False))
        report.write("\n\n")

        report.write("FINAL MISSING VALUES\n")
        report.write("-" * 80 + "\n")
        report.write(filtered_df.isna().sum().to_string())
        report.write("\n\n")

        report.write("NOTES\n")
        report.write("-" * 80 + "\n")
        report.write(
            "This is a light filtering step. Invalid values were replaced with NaN instead of deleting full rows.\n"
        )
        report.write(
            "This preserves the time axis and is more appropriate for time-series analysis.\n"
        )
        report.write(
            "The original cleaned dataset remains unchanged for traceability.\n"
        )

    # -------------------------------------------------------------------------
    # Console output
    # -------------------------------------------------------------------------
    print("\nFiltering summary:")
    print(summary_df.to_string(index=False))

    print("\nFinal missing values:")
    print(filtered_df.isna().sum())

    print(f"\nFiltered data saved to:\n{output_file}")
    print(f"Filtering summary table saved to:\n{summary_table_file}")
    print(f"Filtering report saved to:\n{report_file}")

    print("\nDone.")


if __name__ == "__main__":
    main()