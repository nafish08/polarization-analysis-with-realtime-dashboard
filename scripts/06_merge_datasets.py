from pathlib import Path
import pandas as pd


def main():
    project_root = Path(__file__).resolve().parents[1]

    pol_file = project_root / "data" / "processed" / "polarization_filtered.csv"
    weather_file = project_root / "data" / "external" / "weather_surface_pressure.csv"
    sun_file = project_root / "data" / "external" / "sunrise_sunset.csv"

    output_dir = project_root / "data" / "processed"
    logs_dir = project_root / "outputs" / "logs"

    output_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    if not pol_file.exists():
        print(f"ERROR: Missing polarization file:\n{pol_file}")
        return
    if not weather_file.exists():
        print(f"ERROR: Missing weather file:\n{weather_file}")
        return
    if not sun_file.exists():
        print(f"ERROR: Missing sunrise/sunset file:\n{sun_file}")
        return

    print("=" * 80)
    print("STEP 6: MERGE POLARIZATION + WEATHER + SUNRISE/SUNSET")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # Load files
    # -------------------------------------------------------------------------
    pol_df = pd.read_csv(pol_file, parse_dates=["timestamp"])
    weather_df = pd.read_csv(weather_file, parse_dates=["timestamp"])
    sun_df = pd.read_csv(sun_file, parse_dates=["sunrise_local", "sunset_local"])

    print(f"Polarization rows: {len(pol_df)}")
    print(f"Weather rows:      {len(weather_df)}")
    print(f"Sun rows:          {len(sun_df)}")

    # -------------------------------------------------------------------------
    # Prepare date columns
    # -------------------------------------------------------------------------
    pol_df = pol_df.sort_values("timestamp").reset_index(drop=True)
    weather_df = weather_df.sort_values("timestamp").reset_index(drop=True)

    pol_df["date"] = pol_df["timestamp"].dt.date
    weather_df["date"] = weather_df["timestamp"].dt.date
    sun_df["date"] = pd.to_datetime(sun_df["date"]).dt.date

    # -------------------------------------------------------------------------
    # HIGH-FREQUENCY MERGE
    # -------------------------------------------------------------------------
    highfreq_df = pd.merge_asof(
        pol_df.sort_values("timestamp"),
        weather_df[["timestamp", "surface_pressure_hpa"]].sort_values("timestamp"),
        on="timestamp",
        direction="nearest"
    )

    highfreq_df = highfreq_df.merge(
        sun_df[["date", "sunrise_local", "sunset_local", "day_length_hours"]],
        on="date",
        how="left"
    )

    highfreq_df["is_daylight"] = (
        (highfreq_df["timestamp"] >= highfreq_df["sunrise_local"]) &
        (highfreq_df["timestamp"] <= highfreq_df["sunset_local"])
    )

    highfreq_output = output_dir / "polarization_weather_merged_highfreq.csv"
    highfreq_df.to_csv(highfreq_output, index=False)

    # -------------------------------------------------------------------------
    # HOURLY AGGREGATED MERGE
    # -------------------------------------------------------------------------
    pol_hourly = pol_df.copy().set_index("timestamp")

    numeric_cols = pol_hourly.select_dtypes(include="number").columns.tolist()

    # use lowercase "h" for newer pandas versions
    pol_hourly_agg = pol_hourly[numeric_cols].resample("1h").mean().reset_index()
    pol_hourly_agg["date"] = pol_hourly_agg["timestamp"].dt.date

    hourly_df = pol_hourly_agg.merge(
        weather_df[["timestamp", "surface_pressure_hpa"]],
        on="timestamp",
        how="left"
    )

    hourly_df = hourly_df.merge(
        sun_df[["date", "sunrise_local", "sunset_local", "day_length_hours"]],
        on="date",
        how="left"
    )

    hourly_df["is_daylight"] = (
        (hourly_df["timestamp"] >= hourly_df["sunrise_local"]) &
        (hourly_df["timestamp"] <= hourly_df["sunset_local"])
    )

    hourly_output = output_dir / "polarization_weather_merged_hourly.csv"
    hourly_df.to_csv(hourly_output, index=False)

    # -------------------------------------------------------------------------
    # Report
    # -------------------------------------------------------------------------
    report_file = logs_dir / "merge_report.txt"
    with report_file.open("w", encoding="utf-8") as report:
        report.write("MERGE REPORT\n")
        report.write("=" * 80 + "\n\n")

        report.write("INPUT FILES\n")
        report.write("-" * 80 + "\n")
        report.write(f"Polarization:   {pol_file}\n")
        report.write(f"Weather:        {weather_file}\n")
        report.write(f"Sunrise/Sunset: {sun_file}\n\n")

        report.write("ROW COUNTS\n")
        report.write("-" * 80 + "\n")
        report.write(f"Polarization rows: {len(pol_df)}\n")
        report.write(f"Weather rows:      {len(weather_df)}\n")
        report.write(f"Sun rows:          {len(sun_df)}\n")
        report.write(f"High-frequency merged rows: {len(highfreq_df)}\n")
        report.write(f"Hourly merged rows:         {len(hourly_df)}\n\n")

        report.write("TIME RANGE\n")
        report.write("-" * 80 + "\n")
        report.write(f"High-frequency start: {highfreq_df['timestamp'].min()}\n")
        report.write(f"High-frequency end:   {highfreq_df['timestamp'].max()}\n")
        report.write(f"Hourly start:         {hourly_df['timestamp'].min()}\n")
        report.write(f"Hourly end:           {hourly_df['timestamp'].max()}\n\n")

        report.write("MISSING VALUES IN MERGED DATASETS\n")
        report.write("-" * 80 + "\n")
        report.write("High-frequency merged missing values:\n")
        report.write(highfreq_df.isna().sum().to_string())
        report.write("\n\n")
        report.write("Hourly merged missing values:\n")
        report.write(hourly_df.isna().sum().to_string())
        report.write("\n")

    print("\nMerge complete.")
    print(f"High-frequency merged rows: {len(highfreq_df)}")
    print(f"Hourly merged rows:         {len(hourly_df)}")

    print("\nHigh-frequency time range:")
    print(f"Start: {highfreq_df['timestamp'].min()}")
    print(f"End:   {highfreq_df['timestamp'].max()}")

    print("\nHourly time range:")
    print(f"Start: {hourly_df['timestamp'].min()}")
    print(f"End:   {hourly_df['timestamp'].max()}")

    print(f"\nHigh-frequency merged file saved to:\n{highfreq_output}")
    print(f"Hourly merged file saved to:\n{hourly_output}")
    print(f"Merge report saved to:\n{report_file}")

    print("\nDone.")


if __name__ == "__main__":
    main()