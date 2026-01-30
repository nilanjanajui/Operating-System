import threading

def error(code, message):
    print(f"ERROR: {code}: {message}")
    exit(1)

def producer(next_item, next_item_lock, total_items, buffer, buf_lock, empty_sem, full_sem):
    while True:
        with next_item_lock:
            if next_item[0] > total_items:
                break
            item = next_item[0]
            next_item[0] += 1

        empty_sem.acquire()
        with buf_lock:
            buffer.append(item)
        full_sem.release()

def consumer(total_sum, sum_lock, buffer, buf_lock, empty_sem, full_sem):
    while True:
        full_sem.acquire()
        with buf_lock:
            item = buffer.pop(0)
        empty_sem.release()

        if item is None:  # sentinel value
            break

        with sum_lock:
            total_sum[0] += item

def main():
    try:
        B = int(input("Enter buffer size (1-1024): "))
        p = int(input("Enter number of producers (1-16): "))
        c = int(input("Enter number of consumers (1-16): "))
        m = int(input("Enter total number of items (1-100000): "))
    except ValueError:
        error("E_USAGE", "invalid input, must be integers")

    if not (1 <= B <= 1024):
        error("E_RANGE", "buf must be in 1..1024")
    if not (1 <= p <= 16):
        error("E_RANGE", "producers must be in 1..16")
    if not (1 <= c <= 16):
        error("E_RANGE", "consumers must be in 1..16")
    if not (1 <= m <= 100000):
        error("E_RANGE", "items must be in 1..100000")

    buffer = []
    buf_lock = threading.Lock()
    empty_sem = threading.Semaphore(B)
    full_sem = threading.Semaphore(0)

    next_item = [1]
    next_item_lock = threading.Lock()

    total_sum = [0]
    sum_lock = threading.Lock()

    # start producers
    producers = []
    for _ in range(p):
        t = threading.Thread(target=producer, args=(next_item, next_item_lock, m, buffer, buf_lock, empty_sem, full_sem))
        t.start()
        producers.append(t)

    # start consumers
    consumers = []
    for _ in range(c):
        t = threading.Thread(target=consumer, args=(total_sum, sum_lock, buffer, buf_lock, empty_sem, full_sem))
        t.start()
        consumers.append(t)

    # wait for all producers
    for t in producers:
        t.join()

    # push sentinel values so consumers know when to stop
    for _ in range(c):
        empty_sem.acquire()
        with buf_lock:
            buffer.append(None)
        full_sem.release()

    # wait for all consumers
    for t in consumers:
        t.join()

    print(f"OK: PRODUCED {m}")
    print(f"OK: CONSUMED {m}")
    print(f"OK: SUM {m*(m+1)//2}")

if __name__ == "__main__":
    main()
