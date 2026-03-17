from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


SELECTED_DAY = "2025-02-22"
REFERENCE_TIME = "12:00:00"   # local timestamp within selected day


def build_ellipse_points(azimuth_deg: float, ellipticity_deg: float, n_points: int = 400):
    """
    Build x,y points for a polarization ellipse.

    We use:
    - azimuth angle psi = azimuth_deg
    - ellipticity angle chi = ellipticity_deg

    Semi-axis ratio is derived from tan(chi).
    Major axis is normalized to 1.

    This is a qualitative visualization suitable for presentation.
    """
    psi = np.deg2rad(azimuth_deg)
    chi = np.deg2rad(ellipticity_deg)

    # Major axis
    a = 1.0

    # Minor axis from ellipticity angle
    b = np.tan(chi)

    # avoid extreme numerical explosion if angle is close to +-90 deg
    b = np.clip(b, -1.0, 1.0)

    t = np.linspace(0, 2 * np.pi, n_points)

    # ellipse before rotation
    x0 = a * np.cos(t)
    y0 = b * np.sin(t)

    # rotate by azimuth
    x = x0 * np.cos(psi) - y0 * np.sin(psi)
    y = x0 * np.sin(psi) + y0 * np.cos(psi)

    return x, y


def find_nearest_row(df: pd.DataFrame, target_time: pd.Timestamp):
    """
    Return the row whose timestamp is nearest to target_time.
    """
    idx = (df["timestamp"] - target_time).abs().idxmin()
    return df.loc[idx]


def main():
    project_root = Path(__file__).resolve().parents[1]

    input_file = project_root / "data" / "processed" / "polarization_weather_merged_highfreq.csv"
    figures_dir = project_root / "outputs" / "figures"
    logs_dir = project_root / "outputs" / "logs"

    figures_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    if not input_file.exists():
        print(f"ERROR: Input file not found:\n{input_file}")
        print("Run 06_merge_datasets.py first.")
        return

    print("=" * 80)
    print("STEP 10: POLARIZATION ELLIPSE VISUALIZATION")
    print("=" * 80)

    df = pd.read_csv(input_file, parse_dates=["timestamp"])
    df["date_str"] = df["timestamp"].dt.strftime("%Y-%m-%d")

    day_df = df[df["date_str"] == SELECTED_DAY].copy()

    if day_df.empty:
        print(f"ERROR: No data found for selected day: {SELECTED_DAY}")
        return

    day_df = day_df.sort_values("timestamp").reset_index(drop=True)

    reference_timestamp = pd.Timestamp(f"{SELECTED_DAY} {REFERENCE_TIME}")

    # target times
    target_times = {
        "t": reference_timestamp,
        "t+1s": reference_timestamp + pd.Timedelta(seconds=1),
        "t+1min": reference_timestamp + pd.Timedelta(minutes=1),
        "t+1h": reference_timestamp + pd.Timedelta(hours=1),
    }

    selected_rows = {}
    for label, target_time in target_times.items():
        selected_rows[label] = find_nearest_row(day_df, target_time)

    # -------------------------------------------------------------------------
    # Plot 1: polarization ellipse comparison
    # -------------------------------------------------------------------------
    plt.figure(figsize=(8, 8))

    for label, row in selected_rows.items():
        azimuth = row["azimuth_deg"]
        ellipticity = row["ellipticity_deg"]

        x, y = build_ellipse_points(azimuth, ellipticity)
        plt.plot(x, y, label=f"{label}: {row['timestamp']}")

    plt.axhline(0, linewidth=0.8)
    plt.axvline(0, linewidth=0.8)
    plt.gca().set_aspect("equal", adjustable="box")
    plt.title(f"Polarization Ellipse Evolution on {SELECTED_DAY}")
    plt.xlabel("Ex")
    plt.ylabel("Ey")
    plt.legend(fontsize=8)
    plt.tight_layout()

    ellipse_output = figures_dir / "polarization_ellipse_comparison.png"
    plt.savefig(ellipse_output, dpi=200)
    plt.close()

    # -------------------------------------------------------------------------
    # Plot 2: bonus drift visualization in azimuth-ellipticity space
    # -------------------------------------------------------------------------
    plt.figure(figsize=(8, 6))

    valid_df = day_df[["azimuth_deg", "ellipticity_deg", "timestamp"]].dropna().copy()
    valid_df["time_index"] = np.arange(len(valid_df))

    scatter = plt.scatter(
        valid_df["azimuth_deg"],
        valid_df["ellipticity_deg"],
        c=valid_df["time_index"],
        s=8
    )
    plt.colorbar(scatter, label="Time progression")
    plt.title(f"Polarization Drift in Azimuth-Ellipticity Space on {SELECTED_DAY}")
    plt.xlabel("Azimuth [deg]")
    plt.ylabel("Ellipticity [deg]")
    plt.tight_layout()

    bonus_output = figures_dir / "ellipse_drift_parameter_space.png"
    plt.savefig(bonus_output, dpi=200)
    plt.close()

    # -------------------------------------------------------------------------
    # Report
    # -------------------------------------------------------------------------
    report_file = logs_dir / "ellipse_plot_report.txt"
    with report_file.open("w", encoding="utf-8") as report:
        report.write("POLARIZATION ELLIPSE PLOT REPORT\n")
        report.write("=" * 80 + "\n\n")
        report.write(f"Input file: {input_file}\n")
        report.write(f"Selected day: {SELECTED_DAY}\n")
        report.write(f"Reference time: {REFERENCE_TIME}\n\n")

        report.write("SELECTED TIME POINTS\n")
        report.write("-" * 80 + "\n")
        for label, row in selected_rows.items():
            report.write(
                f"{label}: timestamp={row['timestamp']}, "
                f"azimuth_deg={row['azimuth_deg']:.6f}, "
                f"ellipticity_deg={row['ellipticity_deg']:.6f}\n"
            )

        report.write("\nOUTPUT FILES\n")
        report.write("-" * 80 + "\n")
        report.write(f"{ellipse_output}\n")
        report.write(f"{bonus_output}\n")

    print("\nSelected ellipse time points:")
    for label, row in selected_rows.items():
        print(
            f"{label}: timestamp={row['timestamp']}, "
            f"azimuth_deg={row['azimuth_deg']:.6f}, "
            f"ellipticity_deg={row['ellipticity_deg']:.6f}"
        )

    print(f"\nEllipse comparison plot saved to:\n{ellipse_output}")
    print(f"Bonus drift plot saved to:\n{bonus_output}")
    print(f"Report saved to:\n{report_file}")

    print("\nDone.")


if __name__ == "__main__":
    main()