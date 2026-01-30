# 13. Priority Scheduling with Aging (Non-Preemptive)

import sys

def error(code, msg):
    print(f"ERROR: {code}: {msg}")
    sys.exit(1)

# ---------- INPUT ----------
try:
    n = int(input("Enter number of processes: ").strip())
except:
    error("E_INPUT", "invalid number of processes")

processes = []
seen_pid = set()

print("Enter processes as: pid,arrival,burst,priority")

for i in range(n):
    line = input().strip()
    parts = line.split(",")

    if len(parts) != 4:
        error("E_INPUT", "invalid input format")

    pid = parts[0].strip()

    if pid in seen_pid:
        error("E_DUPPID", "duplicate pid")
    seen_pid.add(pid)

    try:
        arrival = int(parts[1])
        burst = int(parts[2])
        priority = int(parts[3])
    except:
        error("E_INPUT", "non-integer field")

    if arrival < 0:
        error("E_RANGE", "arrival must be >= 0")
    if burst <= 0:
        error("E_RANGE", "burst must be > 0")
    if not (0 <= priority <= 99):
        error("E_RANGE", "priority must be in 0..99")

    processes.append({
        "pid": pid,
        "arrival": arrival,
        "burst": burst,
        "priority": priority
    })

# ---------- SCHEDULING ----------
time = 0
ready = []
todo = processes[:]
completed = {}
gantt = []

while todo or ready:
    for p in todo[:]:
        if p["arrival"] <= time:
            ready.append(p)
            todo.remove(p)

    if not ready:
        next_time = min(p["arrival"] for p in todo)
        gantt.append(f"IDLE@{time}-{next_time}")
        time = next_time
        continue

    # Aging at dispatch
    for p in ready:
        waiting = time - p["arrival"]
        p["eff_prio"] = max(0, p["priority"] - waiting)

    ready.sort(key=lambda x: (x["eff_prio"], x["arrival"], x["pid"]))
    cur = ready.pop(0)

    start = time
    time += cur["burst"]
    gantt.append(f"{cur['pid']}@{start}-{time}")
    completed[cur["pid"]] = time

# ---------- METRICS ----------
total_wait = 0
total_tat = 0
n = len(processes)

for p in processes:
    ct = completed[p["pid"]]
    tat = ct - p["arrival"]
    wt = tat - p["burst"]
    total_wait += wt
    total_tat += tat

# ---------- OUTPUT ----------
print("\nALG PRIO_AGING")
print("GANTT", " ".join(gantt))
print(f"OK: AVG_WAIT {total_wait/n:.2f} AVG_TAT {total_tat/n:.2f}")
