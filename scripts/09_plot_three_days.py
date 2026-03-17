from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


SELECTED_DAYS = [
    "2025-02-21",
    "2025-02-22",
    "2025-02-23",
]


def plot_single_day(day_df: pd.DataFrame, day_str: str, output_path: Path):
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

    sunrise = day_df["sunrise_local"].dropna().iloc[0] if day_df["sunrise_local"].notna().any() else None
    sunset = day_df["sunset_local"].dropna().iloc[0] if day_df["sunset_local"].notna().any() else None

    # Azimuth
    axes[0].plot(day_df["timestamp"], day_df["azimuth_deg"], linewidth=1.0)
    axes[0].set_ylabel("Azimuth [deg]")
    axes[0].set_title(f"Polarization and Surface Pressure on {day_str}")

    # Ellipticity
    axes[1].plot(day_df["timestamp"], day_df["ellipticity_deg"], linewidth=1.0)
    axes[1].set_ylabel("Ellipticity [deg]")

    # Pressure
    axes[2].plot(day_df["timestamp"], day_df["surface_pressure_hpa"], linewidth=1.0)
    axes[2].set_ylabel("Pressure [hPa]")
    axes[2].set_xlabel("Time")

    # Sunrise / sunset markers
    if sunrise is not None:
        for ax in axes:
            ax.axvline(sunrise, linestyle="--", linewidth=1.0)
    if sunset is not None:
        for ax in axes:
            ax.axvline(sunset, linestyle="--", linewidth=1.0)

    # Small labels
    if sunrise is not None:
        axes[0].text(sunrise, axes[0].get_ylim()[1], " Sunrise", va="top")
    if sunset is not None:
        axes[0].text(sunset, axes[0].get_ylim()[1], " Sunset", va="top")

    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def main():
    project_root = Path(__file__).resolve().parents[1]

    input_file = project_root / "data" / "processed" / "polarization_weather_merged_hourly.csv"
    figures_dir = project_root / "outputs" / "figures"
    logs_dir = project_root / "outputs" / "logs"

    figures_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    if not input_file.exists():
        print(f"ERROR: Input file not found:\n{input_file}")
        print("Run 06_merge_datasets.py first.")
        return

    print("=" * 80)
    print("STEP 9: PLOT THREE SELECTED DAYS")
    print("=" * 80)

    df = pd.read_csv(
        input_file,
        parse_dates=["timestamp", "sunrise_local", "sunset_local"]
    )

    df["date_str"] = df["timestamp"].dt.strftime("%Y-%m-%d")

    created_files = []
    missing_days = []

    for day_str in SELECTED_DAYS:
        day_df = df[df["date_str"] == day_str].copy()

        if day_df.empty:
            missing_days.append(day_str)
            continue

        output_path = figures_dir / f"day_detail_{day_str}.png"
        plot_single_day(day_df, day_str, output_path)
        created_files.append(output_path)

    report_file = logs_dir / "three_day_plot_report.txt"
    with report_file.open("w", encoding="utf-8") as report:
        report.write("THREE-DAY PLOT REPORT\n")
        report.write("=" * 80 + "\n\n")
        report.write("Selected days:\n")
        for d in SELECTED_DAYS:
            report.write(f"- {d}\n")
        report.write("\nGenerated files:\n")
        for f in created_files:
            report.write(f"- {f}\n")
        if missing_days:
            report.write("\nMissing days:\n")
            for d in missing_days:
                report.write(f"- {d}\n")

    print("\nGenerated figures:")
    for f in created_files:
        print(f"  {f}")

    if missing_days:
        print("\nMissing days:")
        for d in missing_days:
            print(f"  {d}")

    print(f"\nReport saved to:\n{report_file}")
    print("\nDone.")


if __name__ == "__main__":
    main()
    