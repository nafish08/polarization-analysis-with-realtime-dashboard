from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter


SELECTED_DAY = "2025-02-22"
TIME_WINDOW_MINUTES = 10
ANIMATION_STEP = 200        # higher = faster, fewer frames
ANIMATION_MAX_FRAMES = 120  # safety limit for GIF size


def build_ellipse_points(azimuth_deg: float, ellipticity_deg: float, n_points: int = 400):
    """
    Build x,y points for a qualitative polarization ellipse.
    """
    psi = np.deg2rad(azimuth_deg)
    chi = np.deg2rad(ellipticity_deg)

    a = 1.0
    b = np.tan(chi)
    b = np.clip(b, -1.0, 1.0)

    t = np.linspace(0, 2 * np.pi, n_points)

    x0 = a * np.cos(t)
    y0 = b * np.sin(t)

    x = x0 * np.cos(psi) - y0 * np.sin(psi)
    y = x0 * np.sin(psi) + y0 * np.cos(psi)

    return x, y


def make_time_colored_trajectory(day_df: pd.DataFrame, output_path: Path):
    valid_df = day_df[["azimuth_deg", "ellipticity_deg", "timestamp"]].dropna().copy()
    valid_df = valid_df.sort_values("timestamp").reset_index(drop=True)
    valid_df["time_index"] = np.arange(len(valid_df))

    plt.figure(figsize=(8, 6))

    scatter = plt.scatter(
        valid_df["azimuth_deg"],
        valid_df["ellipticity_deg"],
        c=valid_df["time_index"],
        s=8
    )
    plt.colorbar(scatter, label="Time progression")

    plt.scatter(
        valid_df["azimuth_deg"].iloc[0],
        valid_df["ellipticity_deg"].iloc[0],
        marker="o",
        s=100,
        label="Start"
    )
    plt.scatter(
        valid_df["azimuth_deg"].iloc[-1],
        valid_df["ellipticity_deg"].iloc[-1],
        marker="X",
        s=100,
        label="End"
    )

    step = max(len(valid_df) // 50, 1)
    for i in range(0, len(valid_df) - step, step):
        plt.arrow(
            valid_df["azimuth_deg"].iloc[i],
            valid_df["ellipticity_deg"].iloc[i],
            valid_df["azimuth_deg"].iloc[i + step] - valid_df["azimuth_deg"].iloc[i],
            valid_df["ellipticity_deg"].iloc[i + step] - valid_df["ellipticity_deg"].iloc[i],
            head_width=1.0,
            length_includes_head=True,
            alpha=0.3
        )

    plt.title(f"Polarization Drift Trajectory on {SELECTED_DAY}")
    plt.xlabel("Azimuth [deg]")
    plt.ylabel("Ellipticity [deg]")
    plt.tight_layout()
    plt.legend()
    plt.savefig(output_path, dpi=200)
    plt.close()


def make_sliding_window_trajectory(day_df: pd.DataFrame, output_path: Path, window_minutes: int = 10):
    valid_df = day_df[["azimuth_deg", "ellipticity_deg", "timestamp"]].dropna().copy()
    valid_df = valid_df.sort_values("timestamp").reset_index(drop=True)

    start_time = valid_df["timestamp"].min()
    end_time = start_time + pd.Timedelta(minutes=window_minutes)

    window_df = valid_df[
        (valid_df["timestamp"] >= start_time) &
        (valid_df["timestamp"] <= end_time)
    ].copy()

    window_df["time_index"] = np.arange(len(window_df))

    plt.figure(figsize=(8, 6))

    scatter = plt.scatter(
        window_df["azimuth_deg"],
        window_df["ellipticity_deg"],
        c=window_df["time_index"],
        s=12
    )
    plt.colorbar(scatter, label="Time progression within window")

    plt.plot(window_df["azimuth_deg"], window_df["ellipticity_deg"], linewidth=1.0)

    plt.scatter(
        window_df["azimuth_deg"].iloc[0],
        window_df["ellipticity_deg"].iloc[0],
        marker="o",
        s=100,
        label="Window start"
    )
    plt.scatter(
        window_df["azimuth_deg"].iloc[-1],
        window_df["ellipticity_deg"].iloc[-1],
        marker="X",
        s=100,
        label="Window end"
    )

    plt.title(f"Sliding-Window Drift ({window_minutes} min) on {SELECTED_DAY}")
    plt.xlabel("Azimuth [deg]")
    plt.ylabel("Ellipticity [deg]")
    plt.tight_layout()
    plt.legend()
    plt.savefig(output_path, dpi=200)
    plt.close()


def make_animated_ellipse(day_df: pd.DataFrame, output_path: Path, step: int = 200, max_frames: int = 120):
    valid_df = day_df[["azimuth_deg", "ellipticity_deg", "timestamp"]].dropna().copy()
    valid_df = valid_df.sort_values("timestamp").reset_index(drop=True)

    frame_indices = list(range(0, len(valid_df), step))
    frame_indices = frame_indices[:max_frames]

    fig, ax = plt.subplots(figsize=(6, 6))
    line, = ax.plot([], [])
    title = ax.set_title("")
    ax.axhline(0, linewidth=0.8)
    ax.axvline(0, linewidth=0.8)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.2, 1.2)
    ax.set_xlabel("Ex")
    ax.set_ylabel("Ey")

    def init():
        line.set_data([], [])
        title.set_text("")
        return line, title

    def update(frame_number):
        idx = frame_indices[frame_number]
        row = valid_df.iloc[idx]

        x, y = build_ellipse_points(row["azimuth_deg"], row["ellipticity_deg"])
        line.set_data(x, y)
        title.set_text(
            f"{SELECTED_DAY} | {row['timestamp']} | "
            f"Az={row['azimuth_deg']:.2f}°, El={row['ellipticity_deg']:.2f}°"
        )
        return line, title

    anim = FuncAnimation(
        fig,
        update,
        frames=len(frame_indices),
        init_func=init,
        interval=200,
        blit=True
    )

    writer = PillowWriter(fps=5)
    anim.save(output_path, writer=writer)
    plt.close()


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
    print("STEP 11: BONUS VISUALIZATIONS")
    print("=" * 80)

    df = pd.read_csv(input_file, parse_dates=["timestamp"])
    df["date_str"] = df["timestamp"].dt.strftime("%Y-%m-%d")

    day_df = df[df["date_str"] == SELECTED_DAY].copy()

    if day_df.empty:
        print(f"ERROR: No data found for selected day: {SELECTED_DAY}")
        return

    day_df = day_df.sort_values("timestamp").reset_index(drop=True)

    trajectory_output = figures_dir / "ellipse_drift_trajectory.png"
    sliding_output = figures_dir / "ellipse_drift_sliding_window.png"
    animation_output = figures_dir / "ellipse_evolution.gif"

    make_time_colored_trajectory(day_df, trajectory_output)
    make_sliding_window_trajectory(day_df, sliding_output, TIME_WINDOW_MINUTES)
    make_animated_ellipse(day_df, animation_output, ANIMATION_STEP, ANIMATION_MAX_FRAMES)

    report_file = logs_dir / "bonus_visualization_report.txt"
    with report_file.open("w", encoding="utf-8") as report:
        report.write("BONUS VISUALIZATION REPORT\n")
        report.write("=" * 80 + "\n\n")
        report.write(f"Selected day: {SELECTED_DAY}\n")
        report.write(f"Sliding window length: {TIME_WINDOW_MINUTES} minutes\n")
        report.write(f"Animation step: {ANIMATION_STEP}\n")
        report.write(f"Animation max frames: {ANIMATION_MAX_FRAMES}\n\n")
        report.write("Generated files:\n")
        report.write(f"- {trajectory_output}\n")
        report.write(f"- {sliding_output}\n")
        report.write(f"- {animation_output}\n")

    print("\nGenerated files:")
    print(f"  {trajectory_output}")
    print(f"  {sliding_output}")
    print(f"  {animation_output}")
    print(f"\nReport saved to:\n{report_file}")
    print("\nDone.")


if __name__ == "__main__":
    main()