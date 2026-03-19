import sys
import asyncio
from pathlib import Path

# Fix for Windows asyncio loop issues with Streamlit on Python 3.10+
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

from streamlit.web import cli

def main():
    dashboard_script = str(Path(__file__).resolve().parent / "dashboard.py")
    sys.argv = ["streamlit", "run", dashboard_script, "--server.headless", "true"]
    sys.exit(cli.main())

if __name__ == "__main__":
    main()
