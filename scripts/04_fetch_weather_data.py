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
    print("STEP 4: FETCH WEATHER DATA (SURFACE PRESSURE)")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # Load polarization dataset to get the observation window
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
    print(f"Weather request date range: {start_date} to {end_date}")

    # -------------------------------------------------------------------------
    # Coordinates near Sundhausen / Nordhausen
    # You can later change these if your instructor gives exact fiber coordinates.
    # -------------------------------------------------------------------------
    latitude = 51.4689
    longitude = 10.8078
    timezone = "Europe/Berlin"

    # -------------------------------------------------------------------------
    # Open-Meteo Historical Weather API request
    # -------------------------------------------------------------------------
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": "surface_pressure",
        "timezone": timezone
    }

    print("\nRequesting weather data from Open-Meteo...")
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()

    if "hourly" not in data or "time" not in data["hourly"] or "surface_pressure" not in data["hourly"]:
        print("ERROR: Unexpected API response format.")
        print(data)
        return

    weather_df = pd.DataFrame({
        "timestamp": pd.to_datetime(data["hourly"]["time"]),
        "surface_pressure_hpa": data["hourly"]["surface_pressure"]
    })

    # Keep some metadata columns for traceability
    weather_df["weather_latitude"] = latitude
    weather_df["weather_longitude"] = longitude
    weather_df["timezone"] = timezone

    # -------------------------------------------------------------------------
    # Save CSV
    # -------------------------------------------------------------------------
    output_file = output_dir / "weather_surface_pressure.csv"
    weather_df.to_csv(output_file, index=False)

    # -------------------------------------------------------------------------
    # Save log report
    # -------------------------------------------------------------------------
    report_file = logs_dir / "weather_fetch_report.txt"
    with report_file.open("w", encoding="utf-8") as report:
        report.write("WEATHER FETCH REPORT\n")
        report.write("=" * 80 + "\n\n")
        report.write(f"Input polarization file: {input_file}\n")
        report.write(f"Polarization start: {start_time}\n")
        report.write(f"Polarization end:   {end_time}\n")
        report.write(f"Requested weather date range: {start_date} to {end_date}\n\n")

        report.write("REQUEST PARAMETERS\n")
        report.write("-" * 80 + "\n")
        report.write(f"Latitude:  {latitude}\n")
        report.write(f"Longitude: {longitude}\n")
        report.write(f"Timezone:  {timezone}\n")
        report.write("Hourly variable: surface_pressure\n\n")

        report.write("OUTPUT SUMMARY\n")
        report.write("-" * 80 + "\n")
        report.write(f"Rows downloaded: {len(weather_df)}\n")
        report.write(f"Weather timestamp start: {weather_df['timestamp'].min()}\n")
        report.write(f"Weather timestamp end:   {weather_df['timestamp'].max()}\n")
        report.write(f"Surface pressure min:    {weather_df['surface_pressure_hpa'].min()}\n")
        report.write(f"Surface pressure max:    {weather_df['surface_pressure_hpa'].max()}\n")
        report.write(f"Surface pressure mean:   {weather_df['surface_pressure_hpa'].mean()}\n")

    # -------------------------------------------------------------------------
    # Console summary
    # -------------------------------------------------------------------------
    print("\nDownloaded weather data successfully.")
    print(f"Rows: {len(weather_df)}")
    print(f"Weather timestamp start: {weather_df['timestamp'].min()}")
    print(f"Weather timestamp end:   {weather_df['timestamp'].max()}")
    print(f"Surface pressure min:    {weather_df['surface_pressure_hpa'].min()}")
    print(f"Surface pressure max:    {weather_df['surface_pressure_hpa'].max()}")
    print(f"Surface pressure mean:   {weather_df['surface_pressure_hpa'].mean()}")

    print(f"\nWeather data saved to:\n{output_file}")
    print(f"Weather fetch report saved to:\n{report_file}")
    print("\nDone.")


if __name__ == "__main__":
    main()