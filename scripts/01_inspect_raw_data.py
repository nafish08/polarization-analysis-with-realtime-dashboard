from pathlib import Path
import pandas as pd


def find_header_line(file_path: Path, expected_keyword: str = "Time[date hh:mm:ss]") -> int:
    """
    Find the line index where the real CSV header starts.
    """
    with file_path.open("r", encoding="utf-8-sig", errors="replace") as f:
        for i, line in enumerate(f):
            if expected_keyword in line:
                return i
    raise ValueError(f"Could not find header line containing: {expected_keyword}")


def main():
    # Project root = one level above /scripts
    project_root = Path(__file__).resolve().parents[1]

    raw_file = project_root / "data" / "raw" / "erfurt_sundhausen_1hour_raw.csv"
    output_dir = project_root / "outputs" / "logs"
    output_dir.mkdir(parents=True, exist_ok=True)

    if not raw_file.exists():
        print(f"ERROR: File not found:\n{raw_file}")
        print("Put your CSV file into data/raw/ and rename it to:")
        print("erfurt_sundhausen_1hour_raw.csv")
        return

    print("=" * 80)
    print("STEP 1: RAW FILE INSPECTION")
    print("=" * 80)
    print(f"File: {raw_file}")
    print(f"File size: {raw_file.stat().st_size / 1024:.2f} KB")

    # Show first 15 raw lines
    print("\nFirst 15 lines of the raw file:\n")
    with raw_file.open("r", encoding="utf-8-sig", errors="replace") as f:
        for i in range(15):
            line = f.readline()
            if not line:
                break
            print(f"{i:02d}: {line.rstrip()}")

    # Detect actual header row
    header_line = find_header_line(raw_file)
    print("\nDetected table header at line index:", header_line)

    # Load CSV from the detected header line
    df = pd.read_csv(
        raw_file,
        sep=";",
        skiprows=header_line,
        encoding="utf-8-sig",
        engine="python"
    )

    # Clean column names
    df.columns = [col.strip() for col in df.columns]

    print("\n" + "=" * 80)
    print("DATAFRAME OVERVIEW")
    print("=" * 80)
    print(f"Rows: {df.shape[0]}")
    print(f"Columns: {df.shape[1]}")

    print("\nColumn names:")
    for idx, col in enumerate(df.columns, start=1):
        print(f"{idx:02d}. {col}")

    print("\nData types:")
    print(df.dtypes)

    print("\nFirst 5 rows:")
    print(df.head())

    print("\nLast 5 rows:")
    print(df.tail())

    print("\nMissing values per column:")
    print(df.isna().sum())

    # Save a simple inspection report
    report_path = output_dir / "raw_data_inspection_report.txt"
    with report_path.open("w", encoding="utf-8") as report:
        report.write("RAW DATA INSPECTION REPORT\n")
        report.write("=" * 80 + "\n")
        report.write(f"File: {raw_file}\n")
        report.write(f"File size: {raw_file.stat().st_size / 1024:.2f} KB\n")
        report.write(f"Detected header line index: {header_line}\n")
        report.write(f"Rows: {df.shape[0]}\n")
        report.write(f"Columns: {df.shape[1]}\n\n")

        report.write("Column names:\n")
        for idx, col in enumerate(df.columns, start=1):
            report.write(f"{idx:02d}. {col}\n")

        report.write("\nData types:\n")
        report.write(df.dtypes.to_string())
        report.write("\n\nMissing values per column:\n")
        report.write(df.isna().sum().to_string())
        report.write("\n")

    print(f"\nInspection report saved to:\n{report_path}")
    print("\nDone.")


if __name__ == "__main__":
    main()