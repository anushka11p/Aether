import subprocess
import sys
import tempfile
import os
import platform

TIMEOUT_SECONDS = 5
MAX_MEMORY_MB = 100

def _limit_resources():
    """Applied inside the subprocess before code runs, via preexec_fn.
    Memory limiting (RLIMIT_AS) is skipped on macOS — Darwin doesn't
    reliably support it. CPU time limiting still applies everywhere."""
    import resource
    resource.setrlimit(resource.RLIMIT_CPU, (TIMEOUT_SECONDS, TIMEOUT_SECONDS))
    if platform.system() == "Linux":
        mem_bytes = MAX_MEMORY_MB * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (mem_bytes, mem_bytes))

def execute_code(code: str) -> dict:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        script_path = f.name

    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
            preexec_fn=_limit_resources,
            env={"PATH": os.environ.get("PATH", "")},
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout[:2000],
            "stderr": result.stderr[:2000],
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "stdout": "", "stderr": f"Execution timed out after {TIMEOUT_SECONDS}s"}
    except Exception as e:
        return {"success": False, "stdout": "", "stderr": f"Execution failed: {e}"}
    finally:
        os.unlink(script_path)
