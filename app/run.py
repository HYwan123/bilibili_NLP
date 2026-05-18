import subprocess
import sys
import signal
import time
import atexit

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
                # Check if process is still running
                if p.poll() is None:  # Process is still running
                    p.terminate()
                    try:
                        # Wait for process to terminate gracefully
                        p.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        # If process didn't terminate gracefully, force kill it
                        print(f"Process {p.pid} didn't terminate gracefully, killing...")
                        p.kill()
                        try:
                            p.wait(timeout=2)  # Wait a bit more for the kill to complete
                        except subprocess.TimeoutExpired:
                            print(f"Process {p.pid} still not terminated after kill")
            except ProcessLookupError:
                # Process already terminated
                pass
            except Exception as e:
                print(f"Error terminating process {p.pid}: {e}")

    def signal_handler(signum, frame):
        print(f"\nReceived signal {signum}, shutting down...")
        cleanup_processes()
        sys.exit(0)

    # Register signal handlers for clean shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Also register cleanup function to run at exit
    atexit.register(cleanup_processes)

    try:
        # Wait for any of the processes to exit
        for p in processes:
            p.wait()
    except KeyboardInterrupt:
        cleanup_processes()
    except Exception as e:
        print(f"Unexpected error: {e}")
        cleanup_processes()

if __name__ == "__main__":
    main()
