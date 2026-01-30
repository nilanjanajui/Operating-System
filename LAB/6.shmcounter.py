import sys
import os
import argparse
import mmap
import struct
import posix_ipc # Note: 'pip install posix_ipc' is usually required for POSIX semaphores
import time

# Error codes
E_USAGE = "E_USAGE"
E_RANGE = "E_RANGE"
E_SHM   = "E_SHM"
E_MMAP  = "E_MMAP"
E_SEM   = "E_SEM"
E_FORK  = "E_FORK"
E_WAIT  = "E_WAIT"

def error_exit(code, message):
    print(f"ERROR: {code}: {message}")
    sys.exit(1)

def main():
    # 1. Parse and Validate Arguments
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--procs', type=int)
    parser.add_argument('--iters', type=int)
    parser.add_argument('--name')
    args, _ = parser.parse_known_args()

    if args.procs is None or args.iters is None or args.name is None:
        error_exit(E_USAGE, "missing required arguments")
    
    if not (2 <= args.procs <= 16):
        error_exit(E_RANGE, "procs must be in 2..16")
    if not (1 <= args.iters <= 100000):
        error_exit(E_RANGE, "iters must be in 1..100000")
    if not args.name.isalnum():
        error_exit(E_RANGE, "name must be alphanumeric only")

    shm_name = f"/shm_{args.name}"
    sem_name = f"/sem_{args.name}"

    shm = None
    sem = None

    try:
        # 2. Create and Map Shared Memory
        try:
            # Create a 8-byte shared memory object (for 64-bit int)
            shm = posix_ipc.SharedMemory(shm_name, flags=posix_ipc.O_CREAT | posix_ipc.O_TRUNC, size=8)
            map_file = mmap.mmap(shm.fd, 8)
            # Initialize counter to 0
            map_file.seek(0)
            map_file.write(struct.pack('q', 0))
        except Exception as e:
            error_exit(E_SHM, f"could not create shm: {e}")

        # 3. Create Semaphore
        try:
            sem = posix_ipc.Semaphore(sem_name, flags=posix_ipc.O_CREAT | posix_ipc.O_TRUNC, initial_value=1)
        except Exception as e:
            error_exit(E_SEM, f"could not create semaphore: {e}")

        # 4. Fork Processes
        pids = []
        for i in range(args.procs):
            try:
                pid = os.fork()
                if pid == 0: # CHILD
                    child_shm = posix_ipc.SharedMemory(shm_name)
                    child_map = mmap.mmap(child_shm.fd, 8)
                    child_sem = posix_ipc.Semaphore(sem_name)
                    
                    for _ in range(args.iters):
                        child_sem.acquire()
                        # Read 64-bit int, increment, and write back
                        child_map.seek(0)
                        val = struct.unpack('q', child_map.read(8))[0]
                        child_map.seek(0)
                        child_map.write(struct.pack('q', val + 1))
                        child_sem.release()
                    
                    child_map.close()
                    os._exit(0)
                else:
                    pids.append(pid)
            except OSError:
                error_exit(E_FORK, "fork failed")

        # 5. Parent Wait
        for pid in pids:
            try:
                os.waitpid(pid, 0)
            except OSError:
                error_exit(E_WAIT, "waitpid failed")

        # 6. Read Final Value
        map_file.seek(0)
        final_val = struct.unpack('q', map_file.read(8))[0]
        print(f"OK: FINAL {final_val}")

    finally:
        # 7. Cleanup (Unlink)
        if shm:
            shm.close_fd()
            try: posix_ipc.unlink_shared_memory(shm_name)
            except: pass
        if sem:
            sem.close()
            try: posix_ipc.unlink_semaphore(sem_name)
            except: pass

if __name__ == "__main__":
    main()