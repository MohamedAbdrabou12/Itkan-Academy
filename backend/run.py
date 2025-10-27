import platform
import subprocess
import sys

# Base uvicorn command
cmd = [
    sys.executable,
    "-m",
    "uvicorn",
    "app.main:app",
    "--reload",
    "--reload-dir",
    "app",
]

# Add asyncio loop option for Windows
if platform.system() == "Windows":
    cmd += ["--loop", "asyncio"]

# Run the command
subprocess.run(cmd)
