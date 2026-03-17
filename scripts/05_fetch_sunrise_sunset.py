from pathlib import Path
import pandas as pd
import requests


def main():
    project_root = Path(__file__).resolve().parents[1]

    input_file = project_root / "data" / "processed" / "polarization_filtered.csv"
    output_dir = project_root / "data" / "external"
    logs_dir = project_root / "outputs" / "logs"

    output_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    if not input_file.exists():
        print(f"ERROR: Input file not found:\n{input_file}")
        print("Run 03b_filter_data.py first.")
        return

    print("=" * 80)
    print("STEP 5: FETCH SUNRISE / SUNSET DATA (OPEN-METEO)")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # Load polarization dataset to determine date range
    # -------------------------------------------------------------------------
    df = pd.read_csv(input_file, parse_dates=["timestamp"])

    start_time = df["timestamp"].min()
    end_time = df["timestamp"].max()

    if pd.isna(start_time) or pd.isna(end_time):
        print("ERROR: Could not determine time range from polarization data.")
        return

    start_date = start_time.date().isoformat()
    end_date = end_time.date().isoformat()

    print(f"Polarization data start: {start_time}")
    print(f"Polarization data end:   {end_time}")
    print(f"Sunrise/sunset request date range: {start_date} to {end_date}")

    # Coordinates near Sundhausen / Nordhausen
    latitude = 51.4689
    longitude = 10.8078
    timezone = "Europe/Berlin"

    # -------------------------------------------------------------------------
    # Open-Meteo request for daily sunrise / sunset
    # -------------------------------------------------------------------------
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "daily": "sunrise,sunset",
        "timezone": timezone
    }

    print("\nRequesting sunrise/sunset data from Open-Meteo...")
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()

    if "daily" not in data or "time" not in data["daily"]:
        print("ERROR: Unexpected API response format.")
        print(data)
        return

    daily = data["daily"]

    required_keys = ["time", "sunrise", "sunset"]
    for key in required_keys:
        if key not in daily:
            print(f"ERROR: Missing key in API response: daily['{key}']")
            print(data)
            return

    sunrise_df = pd.DataFrame({
        "date": pd.to_datetime(daily["time"]).date,
        "sunrise_local": pd.to_datetime(daily["sunrise"], errors="coerce"),
        "sunset_local": pd.to_datetime(daily["sunset"], errors="coerce"),
    })

    # Derived columns
    sunrise_df["day_length_hours"] = (
        (sunrise_df["sunset_local"] - sunrise_df["sunrise_local"]).dt.total_seconds() / 3600.0
    )
    sunrise_df["latitude"] = latitude
    sunrise_df["longitude"] = longitude
    sunrise_df["timezone"] = timezone

    output_file = output_dir / "sunrise_sunset.csv"
    sunrise_df.to_csv(output_file, index=False)

    report_file = logs_dir / "sunrise_sunset_fetch_report.txt"
    with report_file.open("w", encoding="utf-8") as report:
        report.write("SUNRISE / SUNSET FETCH REPORT\n")
        report.write("=" * 80 + "\n\n")

        report.write("INPUT / DATE RANGE\n")
        report.write("-" * 80 + "\n")
        report.write(f"Input polarization file: {input_file}\n")
        report.write(f"Polarization start: {start_time}\n")
        report.write(f"Polarization end:   {end_time}\n")
        report.write(f"Requested date range: {start_date} to {end_date}\n\n")

        report.write("LOCATION\n")
        report.write("-" * 80 + "\n")
        report.write(f"Latitude:  {latitude}\n")
        report.write(f"Longitude: {longitude}\n")
        report.write(f"Timezone:  {timezone}\n\n")

        report.write("OUTPUT SUMMARY\n")
        report.write("-" * 80 + "\n")
        report.write(f"Rows downloaded: {len(sunrise_df)}\n")
        report.write(f"First date: {sunrise_df['date'].min()}\n")
        report.write(f"Last date:  {sunrise_df['date'].max()}\n")
        report.write(f"Shortest day length [h]: {sunrise_df['day_length_hours'].min():.3f}\n")
        report.write(f"Longest day length [h]:  {sunrise_df['day_length_hours'].max():.3f}\n\n")

        report.write("DATA PREVIEW\n")
        report.write("-" * 80 + "\n")
        report.write(sunrise_df.to_string(index=False))
        report.write("\n")

    print("\nDownloaded sunrise/sunset data successfully.")
    print(f"Rows: {len(sunrise_df)}")
    print(f"First date: {sunrise_df['date'].min()}")
    print(f"Last date:  {sunrise_df['date'].max()}")
    print(f"Shortest day length [h]: {sunrise_df['day_length_hours'].min():.3f}")
    print(f"Longest day length [h]:  {sunrise_df['day_length_hours'].max():.3f}")

    print(f"\nSunrise/sunset data saved to:\n{output_file}")
    print(f"Report saved to:\n{report_file}")
    print("\nDone.")


if __name__ == "__main__":
    main()