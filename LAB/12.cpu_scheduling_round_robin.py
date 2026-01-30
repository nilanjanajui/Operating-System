
import sys
import csv
import argparse

def error(code, msg):
    print(f"ERROR: {code}: {msg}")
    sys.exit(1)

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("--q", type=int, required=True)
args = parser.parse_args()

quantum = args.q
if not (1 <= quantum <= 1000):
    error("E_RANGE", "quantum must be in 1..1000")

# Read CSV from stdin
try:
    reader = csv.DictReader(sys.stdin)
    processes = []
    pids_set = set()
    for row in reader:
        pid = row["pid"]
        if pid in pids_set:
            error("E_DUPPID", f"duplicate pid {pid}")
        pids_set.add(pid)
        try:
            arrival = int(row["arrival"])
            burst = int(row["burst"])
            if burst <= 0:
                error("E_RANGE", "burst must be positive")
        except:
            error("E_INPUT", "invalid arrival or burst")
        processes.append({
            "pid": pid,
            "arrival": arrival,
            "burst": burst,
            "remaining": burst,
            "completion": 0
        })
except Exception:
    error("E_INPUT", "malformed CSV")

# Sort by arrival time, then PID lexicographically
processes.sort(key=lambda x: (x["arrival"], x["pid"]))

time = 0
ready_queue = []
gantt = []

# Keep track of processes left
remaining_processes = processes.copy()

while remaining_processes or ready_queue:
    # Add new arrivals at current time
    arrivals = [p for p in remaining_processes if p["arrival"] <= time]
    arrivals.sort(key=lambda x: x["pid"])  # tie-breaker
    for p in arrivals:
        ready_queue.append(p)
        remaining_processes.remove(p)

    if not ready_queue:
        # CPU idle → jump to next arrival
        if remaining_processes:
            next_arrival = min(remaining_processes, key=lambda x: x["arrival"])
            gantt.append(f"IDLE@{time}-{next_arrival['arrival']}")
            time = next_arrival["arrival"]
            continue
        else:
            break

    # Pick first process in ready queue
    current = ready_queue.pop(0)
    run_time = min(current["remaining"], quantum)
    gantt.append(f"{current['pid']}@{time}-{time + run_time}")
    time += run_time
    current["remaining"] -= run_time

    # Check if current finished
    if current["remaining"] == 0:
        current["completion"] = time
    else:
        # Requeue unfinished process
        ready_queue.append(current)

# Compute metrics
total_wt = 0
total_tat = 0
for p in processes:
    tat = p["completion"] - p["arrival"]
    wt = tat - p["burst"]
    total_wt += wt
    total_tat += tat

avg_wt = total_wt / len(processes)
avg_tat = total_tat / len(processes)

# Output
print("ALG RR")
print("GANTT", " ".join(gantt))
print(f"OK: AVG_WAIT {avg_wt:.2f} AVG_TAT {avg_tat:.2f}")


#run in terminal; 
# printf 'pid,arrival,burst\nP1,0,5\nP2,0,3\nP3,2,2\n' | python3 "/home/nilanjana/5th Semester/Operating System/LAB/12.cpu_scheduling_round_robin.py" --q 2