import threading
import sys

def error(code, message):
    print(f"ERROR: {code}: {message}")
    sys.exit(1)

def worker(start, end, total, lock):
    local_sum = 0
    for i in range(start, end + 1):
        local_sum += i

    # protect shared total
    with lock:
        total[0] += local_sum

def main():
    # very simple argument parsing
    if "--threads" not in sys.argv or "--n" not in sys.argv:
        error("E_USAGE", "missing required arguments")

    try:
        t = int(sys.argv[sys.argv.index("--threads") + 1])
        n = int(sys.argv[sys.argv.index("--n") + 1])
    except (ValueError, IndexError):
        error("E_USAGE", "invalid arguments")

    if t < 1 or t > 32:
        error("E_RANGE", "threads must be in 1..32")

    if n < 1 or n > 1_000_000:
        error("E_RANGE", "n must be in 1..1000000")

    threads = []
    lock = threading.Lock()
    total = [0]  # mutable container for shared sum

    chunk = n // t
    remainder = n % t
    start = 1

    for i in range(t):
        end = start + chunk - 1
        if i < remainder:
            end += 1

        th = threading.Thread(
            target=worker,
            args=(start, end, total, lock)
        )
        threads.append(th)
        th.start()

        start = end + 1

    for th in threads:
        th.join()

    print(f"OK: SUM {total[0]}")

if __name__ == "__main__":
    main()

# run in terminal:
# python threadsum.py --threads 4 --n 10

