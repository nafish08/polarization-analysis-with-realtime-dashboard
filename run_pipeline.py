import subprocess
from pathlib import Path
import sys

def main():
    project_root = Path(__file__).resolve().parent
    scripts_dir = project_root / "scripts"
    
    # Define the execution order
    scripts_to_run = [
        "01_inspect_raw_data.py",
        "02_clean_polarization_data.py",
        "03_error_analysis.py",
        "03b_filter_data.py",
        "04_fetch_weather_data.py",
        "05_fetch_sunrise_sunset.py",
        "06_merge_datasets.py",
        "07_daily_correlation_analysis.py",
        "08_trend_analysis.py",
        "09_plot_three_days.py",
        "10_plot_polarization_ellipses.py",
        "11_bonus_visualizations.py"
    ]
    
    # Use python executable from active environment
    python_exec = sys.executable
    
    print("=" * 80)
    print("STARTING POLARIZATION ANALYSIS PIPELINE")
    print("=" * 80)
    
    successful_scripts = []
    failed_script = None
    
    for script_name in scripts_to_run:
        script_path = scripts_dir / script_name
        
        if not script_path.exists():
            print(f"\n[ERROR] Script not found: {script_name}")
            failed_script = script_name
            break
            
        print(f"\n>>> Running {script_name}...")
        
        try:
            # We use subprocess.run, it will print stdout/stderr straight to console
            result = subprocess.run(
                [python_exec, str(script_path)],
                check=True
            )
            successful_scripts.append(script_name)
        except subprocess.CalledProcessError as e:
            print(f"\n[ERROR] Pipeline failed at {script_name} (Exit code: {e.returncode})")
            failed_script = script_name
            break
            
    # Print execution summary
    print("\n" + "=" * 80)
    print("PIPELINE EXECUTION SUMMARY")
    print("=" * 80)
    
    print("Successfully ran:")
    for s in successful_scripts:
        print(f"  [OK] {s}")
        
    if failed_script:
        print(f"\nFAILED at:")
        print(f"  [XX] {failed_script}")
        print("\nPipeline aborted. Please check the logs/errors above to fix the issue before running again.")
        sys.exit(1)
    else:
        print("\nAll scripts executed successfully! Pipeline complete.")
        print("You can now start the dashboard to view the results.")

if __name__ == "__main__":
    main()
