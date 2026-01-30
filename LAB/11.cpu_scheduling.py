
import sys
from collections import namedtuple

Process = namedtuple("Process", ["pid", "arrival", "burst"])

def parse_input():
    lines = [line.strip() for line in sys.stdin if line.strip()]
    if not lines:
        print("ERROR: E_INPUT: empty input", file=sys.stderr)
        sys.exit(1)
    if lines[0] != "pid,arrival,burst":
        print("ERROR: E_INPUT: missing or incorrect header", file=sys.stderr)
        sys.exit(1)
    
    processes = []
    seen_pids = set()
    for i, line in enumerate(lines[1:], start=2):
        parts = line.split(",")
        if len(parts) != 3:
            print(f"ERROR: E_INPUT: line {i} malformed", file=sys.stderr)
            sys.exit(1)
        pid = parts[0].strip()
        if pid in seen_pids:
            print(f"ERROR: E_DUPPID: duplicate pid {pid}", file=sys.stderr)
            sys.exit(1)
        seen_pids.add(pid)
        try:
            arrival = int(parts[1].strip())
            burst = int(parts[2].strip())
        except ValueError:
            print(f"ERROR: E_INPUT: arrival and burst must be integers on line {i}", file=sys.stderr)
            sys.exit(1)
        if arrival < 0 or burst <= 0:
            print("ERROR: E_RANGE: arrival and burst must be non-negative; burst must be > 0", file=sys.stderr)
            sys.exit(1)
        processes.append(Process(pid, arrival, burst))
    return processes

def fcfs(processes):
    processes.sort(key=lambda p: p.arrival)
    time = 0
    gantt = []
    wait_times = []
    tat_times = []

    for p in processes:
        if time < p.arrival:
            gantt.append(f"IDLE@{time}-{p.arrival}")
            time = p.arrival
        start = time
        end = start + p.burst
        gantt.append(f"{p.pid}@{start}-{end}")
        wait_times.append(start - p.arrival)
        tat_times.append(end - p.arrival)
        time = end

    avg_wait = round(sum(wait_times)/len(wait_times), 2)
    avg_tat = round(sum(tat_times)/len(tat_times), 2)

    print("ALG FCFS")
    print("GANTT " + " ".join(gantt))
    print(f"OK: AVG_WAIT {avg_wait:.2f} AVG_TAT {avg_tat:.2f}")

def sjf(processes):
    time = 0
    gantt = []
    wait_times = []
    tat_times = []
    remaining = processes.copy()

    while remaining:
        available = [p for p in remaining if p.arrival <= time]
        if not available:
            next_arrival = min(remaining, key=lambda p: p.arrival)
            gantt.append(f"IDLE@{time}-{next_arrival.arrival}")
            time = next_arrival.arrival
            available = [p for p in remaining if p.arrival <= time]
        available.sort(key=lambda p: (p.burst, p.arrival, p.pid))
        p = available[0]
        start = time
        end = start + p.burst
        gantt.append(f"{p.pid}@{start}-{end}")
        wait_times.append(start - p.arrival)
        tat_times.append(end - p.arrival)
        time = end
        remaining.remove(p)

    avg_wait = round(sum(wait_times)/len(wait_times), 2)
    avg_tat = round(sum(tat_times)/len(tat_times), 2)

    print("ALG SJF")
    print("GANTT " + " ".join(gantt))
    print(f"OK: AVG_WAIT {avg_wait:.2f} AVG_TAT {avg_tat:.2f}")

def main():
    processes = parse_input()
    fcfs(processes)
    sjf(processes)

if __name__ == "__main__":
    main()
    


# Run in terminal:

# printf 'pid,arrival,burst\nP1,0,5\nP2,2,2\nP3,4,1\n' | python3 "/home/nilanjana/5th Semester/Operating System/LAB/11.cpu_scheduling.py"
