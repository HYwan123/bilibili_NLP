import subprocess
import sys
import signal
import time

def main():
    processes = []

    commands = [
        ["start-api"],
        ["start-vector"],
        ["start-video"],
    ]

    for cmd in commands:
        p = subprocess.Popen(cmd)
        processes.append(p)

    def cleanup_processes():
        print("Shutting down processes...")
        for p in processes:
            try:
                p.terminate()
                # Wait a bit for graceful shutdown
                try:
                    p.wait(timeout=5)  # Wait up to 5 seconds for process to terminate
                except subprocess.TimeoutExpired:
                    # If process didn't terminate gracefully, force kill it
                    print(f"Process {p.pid} didn't terminate gracefully, killing...")
                    p.kill()
                    p.wait()  # Wait for the kill to complete
            except ProcessLookupError:
                # Process already terminated
                pass

    def signal_handler(signum, frame):
        cleanup_processes()
        sys.exit(0)

    # Register signal handlers for clean shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Wait for any of the processes to exit
        for p in processes:
            p.wait()
    except KeyboardInterrupt:
        cleanup_processes()
    except Exception:
        cleanup_processes()

if __name__ == "__main__":
    main()
