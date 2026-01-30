import sys
import os
import signal
import time

# Error codes
E_USAGE = "E_USAGE"
E_RANGE = "E_RANGE"
E_FORK = "E_FORK"
E_EXEC = "E_EXEC"
E_WAIT = "E_WAIT"
E_SIGNAL = "E_SIGNAL"

def error_exit(code, message):
    print(f"ERROR: {code}: {message}", file=sys.stderr)
    sys.exit(1)

# Global variable to track the child PID
child_pid = -1

def alarm_handler(signum, frame):
    """This function runs when the alarm timer reaches zero."""
    global child_pid
    if child_pid > 0:
        try:
            # Send SIGKILL to the child
            os.kill(child_pid, signal.SIGKILL)
        except OSError:
            pass # Child might have just finished

def main():
    global child_pid
    
    # 1. Parse Arguments
    args = sys.argv[1:]
    seconds = None
    cmd = None
    cmd_args = []

    i = 0
    while i < len(args):
        if args[i] == "--seconds":
            if i + 1 < len(args):
                try:
                    seconds = int(args[i+1])
                    if not (1 <= seconds <= 60): raise ValueError
                except ValueError:
                    error_exit(E_RANGE, "seconds must be in 1..60")
                i += 2
            else:
                error_exit(E_USAGE, "missing value for --seconds")
        elif args[i] == "--cmd":
            if i + 1 < len(args):
                cmd = args[i+1]
                i += 2
            else:
                error_exit(E_USAGE, "missing value for --cmd")
        elif args[i] == "--args":
            if i + 1 < len(args):
                cmd_args = args[i+1].split(',')
                i += 2
            else:
                error_exit(E_USAGE, "missing value for --args")
        else:
            error_exit(E_USAGE, f"unrecognized argument: {args[i]}")

    if seconds is None or cmd is None:
        error_exit(E_USAGE, "--seconds and --cmd are required")

    # 2. Setup Signal Handler
    # signal.signal is the Python equivalent to sigaction()
    signal.signal(signal.SIGALRM, alarm_handler)

    # 3. Fork and Exec
    try:
        child_pid = os.fork()
    except OSError:
        error_exit(E_FORK, "fork failed")

    if child_pid == 0:
        # --- CHILD PROCESS ---
        try:
            os.execvp(cmd, [cmd] + cmd_args)
        except OSError:
            os._exit(127) # Exec failure
    else:
        # --- PARENT PROCESS ---
        # Arm the alarm
        signal.alarm(seconds)
        
        try:
            # Wait for the child to change state
            pid, status = os.waitpid(child_pid, 0)
            
            # Cancel the alarm because the child finished
            signal.alarm(0)

            # Analyze how the child died
            if os.WIFEXITED(status):
                code = os.WEXITSTATUS(status)
                if code == 127:
                    error_exit(E_EXEC, "cannot exec program")
                print(f"OK: EXIT {code}")
            
            elif os.WIFSIGNALED(status):
                sig = os.WTERMSIG(status)
                if sig == signal.SIGKILL:
                    # This means our alarm_handler killed it
                    print("OK: TIMEOUT KILLED")
                else:
                    # Child died by some other signal (e.g. SIGINT)
                    print(f"OK: SIG {sig}")

        except OSError:
            error_exit(E_WAIT, "waitpid failed")

if __name__ == "__main__":
    main()