# 3
import sys
import os
import stat

# Error codes
E_USAGE = "E_USAGE"
E_NOTDIR = "E_NOTDIR"
E_OPEN_DIR = "E_OPEN_DIR"
E_READ_DIR = "E_READ_DIR"
E_STAT = "E_STAT"

def error_exit(code, message):
    """Print error message and exit with non-zero status."""
    print(f"ERROR: {code}: {message}", file=sys.stderr)
    sys.exit(1)

def parse_arguments(args):
    """Parse command line arguments."""
    path = None
    sort_by = "name"  # default
    
    i = 0
    while i < len(args):
        if args[i] == "--path":
            if i + 1 >= len(args):
                error_exit(E_USAGE, "missing value for --path")
            path = args[i + 1]
            i += 2
        elif args[i] == "--sort":
            if i + 1 >= len(args):
                error_exit(E_USAGE, "missing value for --sort")
            sort_by = args[i + 1]
            if sort_by not in ["name", "size"]:
                error_exit(E_USAGE, "sort must be 'name' or 'size'")
            i += 2
        else:
            error_exit(E_USAGE, f"unrecognized argument: {args[i]}")
    
    if path is None:
        error_exit(E_USAGE, "missing required --path")
    
    return path, sort_by

def get_entry_type(mode):
    """Determine entry type character from stat mode."""
    if stat.S_ISREG(mode):
        return 'F'  # Regular file
    elif stat.S_ISDIR(mode):
        return 'D'  # Directory
    elif stat.S_ISLNK(mode):
        return 'L'  # Symbolic link
    else:
        return 'O'  # Other (device, pipe, socket, etc.)

def list_directory(path, sort_by):
    """
    List directory entries and return list of (name, type, size) tuples.
    """
    entries = []
    
    # Check if path exists and is a directory
    try:
        if not os.path.exists(path):
            error_exit(E_NOTDIR, "path does not exist")
        
        if not os.path.isdir(path):
            error_exit(E_NOTDIR, "path is not a directory")
    except OSError as e:
        error_exit(E_NOTDIR, f"cannot access path: {e.strerror}")
    
    # Open and read directory
    try:
        # Using scandir() which is more efficient than listdir()
        with os.scandir(path) as it:
            for entry in it:
                name = entry.name
                
                # Skip . and ..
                if name in ['.', '..']:
                    continue
                
                # Get file info using lstat() (doesn't follow symlinks)
                try:
                    stat_info = entry.stat(follow_symlinks=False)
                except OSError as e:
                    error_exit(E_STAT, f"cannot stat '{name}': {e.strerror}")
                
                # Determine type
                entry_type = get_entry_type(stat_info.st_mode)
                
                # Get size
                size = stat_info.st_size
                
                entries.append((name, entry_type, size))
    
    except PermissionError as e:
        error_exit(E_OPEN_DIR, f"permission denied: {e.strerror}")
    except OSError as e:
        error_exit(E_OPEN_DIR, f"cannot open directory: {e.strerror}")
    
    # Sort entries
    if sort_by == "name":
        entries.sort(key=lambda x: x[0])  # Sort by name
    elif sort_by == "size":
        # Sort by size, then by name for ties
        entries.sort(key=lambda x: (x[2], x[0]))
    
    return entries

def main():
    # Parse arguments
    path, sort_by = parse_arguments(sys.argv[1:])
    
    # Get directory entries
    entries = list_directory(path, sort_by)
    
    # Counters for summary
    total = len(entries)
    files = 0
    dirs = 0
    links = 0
    other = 0
    
    # Output each entry
    for name, entry_type, size in entries:
        print(f"ENTRY {entry_type} {size} {name}")
        
        # Update counters
        if entry_type == 'F':
            files += 1
        elif entry_type == 'D':
            dirs += 1
        elif entry_type == 'L':
            links += 1
        elif entry_type == 'O':
            other += 1
    
    # Output summary
    print(f"OK: TOTAL {total} FILES {files} DIRS {dirs} LINKS {links} OTHER {other}")
    
    sys.exit(0)

if __name__ == "__main__":
    main()


'''
Execution in CL:

# Create test directory
mkdir testdir
echo "Hello" > testdir/file1.txt
echo "World" > testdir/file2.txt
mkdir testdir/subdir
ln -s file1.txt testdir/link1

$ python dirreport.py --path testdir

'''