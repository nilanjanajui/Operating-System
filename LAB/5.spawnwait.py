import sys
import os

def error_exit(code, message):
    print(f"ERROR: {code}: {message}", file=sys.stderr)
    sys.exit(1)

def main():
    # 1. Parse Arguments
    args = sys.argv[1:]
    cmd = None
    cmd_args = []
    repeat = 1

    i = 0
    while i < len(args):
        if args[i] == "--cmd":
            if i + 1 < len(args):
                cmd = args[i+1]
                i += 2
            else:
                error_exit("E_USAGE", "missing value for --cmd")
        elif args[i] == "--args":
            if i + 1 < len(args):
                # Split comma-separated arguments
                cmd_args = args[i+1].split(',')
                i += 2
            else:
                error_exit("E_USAGE", "missing value for --args")
        elif args[i] == "--repeat":
            if i + 1 < len(args):
                try:
                    repeat = int(args[i+1])
                    if repeat < 1: raise ValueError
                except ValueError:
                    error_exit("E_RANGE", "repeat must be >= 1")
                i += 2
            else:
                error_exit("E_USAGE", "missing value for --repeat")
        else:
            error_exit("E_USAGE", f"unrecognized argument: {args[i]}")

    if cmd is None:
        error_exit("E_USAGE", "missing required --cmd")

    # 2. Sequential Spawning Loop
    for k in range(1, repeat + 1):
        try:
            # Step 1: Fork
            pid = os.fork()
        except OSError:
            error_exit("E_FORK", "failed to fork process")

        if pid == 0:
            # --- CHILD PROCESS ---
            try:
                # Step 2: Exec
                # os.execvp(file, args_list) - first arg must be the program name
                os.execvp(cmd, [cmd] + cmd_args)
            except OSError:
                # If exec fails, the child must exit immediately
                # We exit with a special code so parent knows it's an exec failure
                os._exit(127) 
        else:
            # --- PARENT PROCESS ---
            print(f"CHILD {k} PID {pid} START")

            # Step 3: Wait for termination
            try:
                # waitpid(pid, options)
                _, status = os.waitpid(pid, 0)
                
                # Interpret status
                if os.WIFEXITED(status):
                    exit_code = os.WEXITSTATUS(status)
                    # Check if the exit was actually an exec failure
                    if exit_code == 127:
                        error_exit("E_EXEC", "cannot exec program")
                    print(f"CHILD {k} PID {pid} EXIT {exit_code}")
                
                elif os.WIFSIGNALED(status):
                    signum = os.WTERMSIG(status)
                    print(f"CHILD {k} PID {pid} SIG {signum}")
                
            except OSError:
                error_exit("E_WAIT", "waitpid failed")

    print(f"OK: COMPLETED {repeat}")

if __name__ == "__main__":
    main()