import subprocess


def run_command(cmd: str, description: str = "") -> bool:
    """Run a command and handle errors."""
    if description:
        print(f"Running: {description}")
    else:
        print(f"Running: {cmd}")

    try:
        result = subprocess.run(cmd, check=True, shell=True, capture_output=False)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {cmd}")
        print(f"Error message: {e}")
        return False
