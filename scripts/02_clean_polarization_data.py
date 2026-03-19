from pathlib import Path
import pandas as pd
import numpy as np


def find_header_line(file_path: Path, expected_keyword: str = "Time[date hh:mm:ss]") -> int:
    """
    Find the line index where the actual CSV header starts.
    """
    with file_path.open("r", encoding="utf-8-sig", errors="replace") as f:
        for i, line in enumerate(f):
            if expected_keyword in line:
                return i
    raise ValueError(f"Could not find header line containing: {expected_keyword}")


def parse_elapsed_time_to_seconds(value: str) -> float:
    """
    Convert elapsed time strings like:
    '0.00:50:30:777' -> total seconds

    Format interpretation:
    days.hours:minutes:seconds:milliseconds
    Example:
    0.00:50:30:777 = 0 days, 0 hours, 50 min, 30 sec, 777 ms
    """
    if pd.isna(value):
        return np.nan

    value = str(value).strip()

    try:
        day_part, rest = value.split(".", 1)
        hh, mm, ss, ms = rest.split(":")
        total_seconds = (
            int(day_part) * 24 * 3600
            + int(hh) * 3600
            + int(mm) * 60
            + int(ss)
            + int(ms) / 1000.0
        )
        return total_seconds
    except Exception:
        return np.nan


def main():
    project_root = Path(__file__).resolve().parents[1]

    raw_file = project_root / "data" / "raw" / "20.02.2025_to_26.02.2025_sund_to_ef-FZE-IOF_port-2.csv"
    processed_dir = project_root / "data" / "processed"
    logs_dir = project_root / "outputs" / "logs"

    processed_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    if not raw_file.exists():
        print(f"File not found locally:\n{raw_file}")
        print("Downloading from Zenodo...")
        import urllib.request
        url = "https://zenodo.org/records/17078970/files/20.02.2025_to_26.02.2025_sund_to_ef-FZE-IOF_port-2.csv?download=1"
        raw_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            urllib.request.urlretrieve(url, raw_file)
            print("Download complete.")
        except Exception as e:
            print(f"ERROR downloading file: {e}")
            return

    print("=" * 80)
    print("STEP 2: CLEAN POLARIZATION DATA")
    print("=" * 80)

    # Detect header row
    header_line = find_header_line(raw_file)
    print(f"Detected header line: {header_line}")

    # Load raw table
    df = pd.read_csv(
        raw_file,
        sep=";",
        skiprows=header_line,
        encoding="utf-8-sig",
        engine="python"
    )

    # Clean column names
    df.columns = [col.strip() for col in df.columns]

    # Original row count
    original_rows = len(df)

    # Rename columns to clean analysis-friendly names
    rename_map = {
        "Time[date hh:mm:ss]": "timestamp",
        "Elapsed Time [hh:mm:ss:ms]": "elapsed_time_raw",
        "Normalized s 1": "normalized_s1",
        "Normalized s 2": "normalized_s2",
        "Normalized s 3": "normalized_s3",
        "S 0 [mW]": "s0_mw",
        "S 1 [mW]": "s1_mw",
        "S 2 [mW]": "s2_mw",
        "S 3 [mW]": "s3_mw",
        "Azimuth[°]": "azimuth_deg",
        "Ellipticity[°]": "ellipticity_deg",
        "DOP[%]": "dop_pct",
        "DOCP[%]": "docp_pct",
        "DOLP[%]": "dolp_pct",
        "Power[mW]": "power_mw",
        "Pol Power[mW]": "pol_power_mw",
        "Unpol Power[mW]": "unpol_power_mw",
        "Power[dBm]": "power_dbm",
        "Pol Power[dBm]": "pol_power_dbm",
        "Unpol Power[dBm]": "unpol_power_dbm",
        "Power-Split-Ratio": "power_split_ratio",
        "Phase Difference[°]": "phase_difference_deg",
        "Warning": "warning"
    }

    df = df.rename(columns=rename_map)

    # Parse timestamp
    df["timestamp"] = pd.to_datetime(
        df["timestamp"].astype(str).str.strip(),
        format="%Y-%m-%d %H:%M:%S.%f",
        errors="coerce"
    )

    # Parse elapsed time
    df["elapsed_time_sec"] = df["elapsed_time_raw"].apply(parse_elapsed_time_to_seconds)

    # Convert warning column to string only if it contains values; otherwise keep as NaN
    if "warning" in df.columns:
        df["warning"] = df["warning"].replace(r"^\s*$", np.nan, regex=True)

    # Convert all numeric columns safely
    numeric_columns = [
        "normalized_s1", "normalized_s2", "normalized_s3",
        "s0_mw", "s1_mw", "s2_mw", "s3_mw",
        "azimuth_deg", "ellipticity_deg",
        "dop_pct", "docp_pct", "dolp_pct",
        "power_mw", "pol_power_mw", "unpol_power_mw",
        "power_dbm", "pol_power_dbm", "unpol_power_dbm",
        "power_split_ratio", "phase_difference_deg",
        "elapsed_time_sec"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Detect placeholder values often used by instruments
    placeholder_value = -99.990
    placeholder_summary = {}

    for col in numeric_columns:
        count_placeholder = (df[col] == placeholder_value).sum()
        if count_placeholder > 0:
            placeholder_summary[col] = int(count_placeholder)

    # Create a copy for cleaned analysis
    cleaned_df = df.copy()

    # Create a dataset of the "wrong" or anomalous data
    wrong_mask = pd.Series(False, index=df.index)
    for col in numeric_columns:
        wrong_mask = wrong_mask | (df[col] == placeholder_value)
    wrong_mask = wrong_mask | df["timestamp"].isna()
    
    wrong_df = df[wrong_mask].copy()
    wrong_file = processed_dir / "wrong_data.csv"
    wrong_df.to_csv(wrong_file, index=False)

    # Replace placeholder -99.990 with NaN
    for col in numeric_columns:
        cleaned_df.loc[cleaned_df[col] == placeholder_value, col] = np.nan

    # Drop rows where timestamp is invalid
    invalid_timestamp_rows = cleaned_df["timestamp"].isna().sum()
    cleaned_df = cleaned_df.dropna(subset=["timestamp"]).copy()

    # Sort by time just in case
    cleaned_df = cleaned_df.sort_values("timestamp").reset_index(drop=True)

    # Add sample interval column
    cleaned_df["sample_interval_sec"] = cleaned_df["timestamp"].diff().dt.total_seconds()

    # Basic summary
    cleaned_rows = len(cleaned_df)
    removed_rows = original_rows - cleaned_rows

    # Save cleaned data
    cleaned_file = processed_dir / "polarization_cleaned.csv"
    cleaned_df.to_csv(cleaned_file, index=False)

    # Save cleaning report
    report_file = logs_dir / "cleaning_report.txt"
    with report_file.open("w", encoding="utf-8") as report:
        report.write("CLEANING REPORT\n")
        report.write("=" * 80 + "\n")
        report.write(f"Raw file: {raw_file}\n")
        report.write(f"Detected header line: {header_line}\n\n")

        report.write("ROW COUNTS\n")
        report.write("-" * 80 + "\n")
        report.write(f"Original rows: {original_rows}\n")
        report.write(f"Rows after cleaning: {cleaned_rows}\n")
        report.write(f"Removed rows: {removed_rows}\n")
        report.write(f"Rows with invalid timestamp removed: {invalid_timestamp_rows}\n\n")

        report.write("COLUMN NAMES\n")
        report.write("-" * 80 + "\n")
        for col in cleaned_df.columns:
            report.write(f"{col}\n")
        report.write("\n")

        report.write("MISSING VALUES AFTER CLEANING\n")
        report.write("-" * 80 + "\n")
        report.write(cleaned_df.isna().sum().to_string())
        report.write("\n\n")

        report.write("PLACEHOLDER VALUES REPLACED (-99.990 -> NaN)\n")
        report.write("-" * 80 + "\n")
        if placeholder_summary:
            for col, count in placeholder_summary.items():
                report.write(f"{col}: {count}\n")
        else:
            report.write("No placeholder values detected.\n")
        report.write("\n")

        report.write("TIME RANGE\n")
        report.write("-" * 80 + "\n")
        report.write(f"Start timestamp: {cleaned_df['timestamp'].min()}\n")
        report.write(f"End timestamp: {cleaned_df['timestamp'].max()}\n")
        report.write(
            f"Duration: {cleaned_df['timestamp'].max() - cleaned_df['timestamp'].min()}\n"
        )

    print("\nCleaning complete.")
    print(f"Original rows: {original_rows}")
    print(f"Rows after cleaning: {cleaned_rows}")
    print(f"Removed rows: {removed_rows}")
    print(f"Rows with invalid timestamp removed: {invalid_timestamp_rows}")

    print("\nPlaceholder values replaced (-99.990 -> NaN):")
    if placeholder_summary:
        for col, count in placeholder_summary.items():
            print(f"  {col}: {count}")
    else:
        print("  None")

    print("\nMissing values after cleaning:")
    print(cleaned_df.isna().sum())

    print("\nTime range:")
    print("Start:", cleaned_df["timestamp"].min())
    print("End:  ", cleaned_df["timestamp"].max())
    print("Duration:", cleaned_df["timestamp"].max() - cleaned_df["timestamp"].min())

    print(f"\nCleaned data saved to:\n{cleaned_file}")
    print(f"Cleaning report saved to:\n{report_file}")
    print("\nDone.")


if __name__ == "__main__":
    main()