import subprocess
import sys

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

    try:
        for p in processes:
            p.wait()
    except KeyboardInterrupt:
        print("Shutting down...")
        for p in processes:
            p.terminate()

if __name__ == "__main__":
    main()