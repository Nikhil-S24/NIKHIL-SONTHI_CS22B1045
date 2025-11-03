#!/usr/bin/env python3
"""
Single-command launcher for the Gemscap Quant Analytics App.

Usage:
    python app.py

This script starts:
 - backend data ingestion (python -m backend.data_ingestion)
 - streamlit frontend (streamlit run frontend/app.py)

It runs both as subprocesses and cleans up on exit.
"""
import subprocess
import sys
import os
import signal
import time

procs = []

def start_process(cmd, name):
    print(f"[launcher] starting: {name} -> {cmd}")
    # Use shell only for Windows compatibility with 'streamlit' in PATH; otherwise pass list
    return subprocess.Popen(cmd, shell=isinstance(cmd, str), stdout=None, stderr=None)

def main():
    root = os.path.dirname(os.path.abspath(__file__))
    # Ensure working dir is project root
    os.chdir(root)

    try:
        # 1) Start ingestion (module form so imports work)
        ingest_cmd = [sys.executable, "-m", "backend.data_ingestion"]
        p1 = start_process(ingest_cmd, "data_ingestion")
        procs.append(p1)

        # small delay to let ingestion connect first
        time.sleep(1.5)

        # 2) Start streamlit UI
        # Use streamlit CLI normally available in venv PATH
        streamlit_cmd = f"streamlit run frontend/app.py"
        p2 = start_process(streamlit_cmd, "streamlit")
        procs.append(p2)

        print("[launcher] App started. Press CTRL+C to stop both processes.")
        # Wait until child terminates or user interrupts
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n[launcher] KeyboardInterrupt received — shutting down children...")

    finally:
        for p in procs:
            if p.poll() is None:
                print(f"[launcher] terminating pid {p.pid}")
                try:
                    p.send_signal(signal.SIGINT)
                    time.sleep(0.5)
                    p.terminate()
                except Exception:
                    pass
        print("[launcher] Done. Exiting.")

if __name__ == "__main__":
    main()
