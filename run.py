"""
Bhashaverse - Unified Multi-Process Application Launcher
Enables running the FastAPI REST backend and Streamlit frontend either concurrently
or independently.

Usage:
    python run.py            # Starts both FastAPI (port 8000) and Streamlit (port 8501)
    python run.py backend    # Starts only FastAPI backend
    python run.py frontend   # Starts only Streamlit frontend
"""

import sys
import subprocess
import time
import signal
import os


def start_backend():
    """Start the FastAPI backend with uvicorn."""
    print("🚀 Starting Bhashaverse FastAPI Backend on http://127.0.0.1:8000 ...")
    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "Backend.main:app",
        "--host",
        "127.0.0.1",
        "--port",
        "8000",
        "--reload"
    ]
    return subprocess.Popen(cmd)


def start_frontend():
    """Start the Streamlit frontend."""
    print("🌿 Starting Bhashaverse Streamlit Frontend on http://127.0.0.1:8501 ...")
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "Frontend/app.py",
        "--server.port",
        "8501",
        "--server.headless",
        "false"
    ]
    return subprocess.Popen(cmd)


def main():
    mode = sys.argv[1].lower() if len(sys.argv) > 1 else "both"

    if mode == "backend":
        proc = start_backend()
        try:
            proc.wait()
        except KeyboardInterrupt:
            proc.terminate()
        return

    if mode == "frontend":
        proc = start_frontend()
        try:
            proc.wait()
        except KeyboardInterrupt:
            proc.terminate()
        return

    # Run both concurrently
    backend_proc = start_backend()
    time.sleep(1.5)  # Allow backend to bind socket and initialize DB
    frontend_proc = start_frontend()

    print("\n✅ Bhashaverse is live!")
    print("   • REST API & Docs: http://127.0.0.1:8000/docs")
    print("   • Web Frontend:    http://127.0.0.1:8501")
    print("\nPress Ctrl+C to terminate both servers.\n")

    try:
        while True:
            time.sleep(0.5)
            # If any process terminated prematurely, exit cleanly
            if backend_proc.poll() is not None or frontend_proc.poll() is not None:
                break
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Bhashaverse services...")
    finally:
        for proc in [backend_proc, frontend_proc]:
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    proc.kill()
        print("Done. Goodbye!")


if __name__ == "__main__":
    main()
