import sys
import os

def error_exit(msg):
    print(f"ERROR: {msg}")
    sys.exit(1)

def main():
    # 1. Argument Parsing
    args_raw = sys.argv[1:]
    params = {}
    i = 0
    while i < len(args_raw):
        key = args_raw[i].lstrip('-')
        if i + 1 < len(args_raw):
            params[key] = args_raw[i+1]
            i += 2
        else:
            error_exit("E_USAGE: Missing value for argument")

    # Required check
    for req in ['producer', 'filter', 'consumer']:
        if req not in params:
            error_exit("E_USAGE: Missing required stage")

    # Prepare command lists
    stages = [
        ("producer", params['producer'], params.get('producer-args', '').split(',') if params.get('producer-args') else []),
        ("filter", params['filter'], params.get('filter-args', '').split(',') if params.get('filter-args') else []),
        ("consumer", params['consumer'], params.get('consumer-args', '').split(',') if params.get('consumer-args') else [])
    ]

    # 2. Create Pipes
    # pipe1: Producer -> Filter | pipe2: Filter -> Consumer
    p1_read, p1_write = os.pipe()
    p2_read, p2_write = os.pipe()

    pids = {}

    # 3. Spawn Stages
    for name, cmd, cmd_args in stages:
        try:
            pid = os.fork()
            if pid == 0:  # CHILD
                # Redirect STDERR and STDOUT to /dev/null as per spec
                devnull = os.open(os.devnull, os.O_WRONLY)
                os.dup2(devnull, sys.stderr.fileno())

                if name == "producer":
                    os.dup2(p1_write, sys.stdout.fileno())
                elif name == "filter":
                    os.dup2(p1_read, sys.stdin.fileno())
                    os.dup2(p2_write, sys.stdout.fileno())
                elif name == "consumer":
                    os.dup2(p2_read, sys.stdin.fileno())
                    os.dup2(devnull, sys.stdout.fileno()) # Consumer output to devnull

                # Close all pipe fds in child
                for fd in [p1_read, p1_write, p2_read, p2_write, devnull]:
                    os.close(fd)

                os.execvp(cmd, [cmd] + cmd_args)
                os._exit(127) # Exec failed
            
            pids[name] = pid
        except OSError:
            error_exit("E_FORK: Fork failed")

    # 4. PARENT: Close all pipe ends
    for fd in [p1_read, p1_write, p2_read, p2_write]:
        os.close(fd)

    # 5. Wait and Report (Check in fixed order: producer, filter, consumer)
    final_error = None
    for name, _, _ in stages:
        _, status = os.waitpid(pids[name], 0)
        
        if final_error is None: # Only capture the first error found in order
            if os.WIFEXITED(status):
                code = os.WEXITSTATUS(status)
                if code != 0:
                    # code 127 is our custom exec failure
                    msg = "cannot exec" if code == 127 else f"exit {code}"
                    final_error = f"E_STAGE: stage {name} {msg}"
            elif os.WIFSIGNALED(status):
                signum = os.WTERMSIG(status)
                final_error = f"E_STAGE: stage {name} sig {signum}"

    if final_error:
        print(f"ERROR: {final_error}")
        sys.exit(1)
    else:
        print("OK: PIPELINE SUCCESS")

if __name__ == "__main__":
    main()