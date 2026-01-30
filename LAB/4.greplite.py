#!/usr/bin/env python3
import sys

# Error codes
E_USAGE = "E_USAGE"
E_EMPTY_PATTERN = "E_EMPTY_PATTERN"
E_OPEN = "E_OPEN"
E_READ = "E_READ"

def error_exit(code, message):
    """Print error message and exit with non-zero status."""
    print(f"ERROR: {code}: {message}", file=sys.stderr)
    sys.exit(1)

def parse_arguments(args):
    """Parse command line arguments."""
    pattern = None
    files_str = None
    
    i = 0
    while i < len(args):
        if args[i] == "--pattern":
            if i + 1 >= len(args):
                error_exit(E_USAGE, "missing value for --pattern")
            pattern = args[i + 1]
            i += 2
        elif args[i] == "--files":
            if i + 1 >= len(args):
                error_exit(E_USAGE, "missing value for --files")
            files_str = args[i + 1]
            i += 2
        else:
            error_exit(E_USAGE, f"unrecognized argument: {args[i]}")
    
    if pattern is None:
        error_exit(E_USAGE, "missing required --pattern")
    if files_str is None:
        error_exit(E_USAGE, "missing required --files")
    
    # Validate pattern
    if pattern == "":
        error_exit(E_EMPTY_PATTERN, "pattern must be non-empty")
    
    # Parse file list
    if files_str.endswith(','):
        error_exit(E_USAGE, "invalid file list: trailing comma")
    
    files = [f.strip() for f in files_str.split(',') if f.strip()]
    
    if not files:
        error_exit(E_USAGE, "must provide at least one file")
    
    # Check for empty filenames in the middle
    if '' in [f.strip() for f in files_str.split(',')]:
        error_exit(E_USAGE, "file list contains empty entries")
    
    return pattern, files

def search_files(pattern, files):
    """Search for pattern in files and return results."""
    matches = []
    total_matches = 0
    files_processed = 0
    
    # Try to open all files first (all-or-nothing)
    file_handles = []
    try:
        for filename in files:
            try:
                f = open(filename, 'r')
                file_handles.append((filename, f))
            except OSError as e:
                # Close any files we successfully opened
                for _, f in file_handles:
                    f.close()
                error_exit(E_OPEN, f"cannot open '{filename}': {e.strerror}")
    except Exception as e:
        # Catch any other unexpected errors
        for _, f in file_handles:
            f.close()
        error_exit(E_OPEN, f"unexpected error opening files: {e}")
    
    # Now search each file
    for filename, f in file_handles:
        try:
            line_number = 0
            file_match_count = 0
            
            for line in f:
                line_number += 1
                # Remove trailing newline but keep other whitespace
                line_content = line.rstrip('\n')
                
                # Check for pattern (case-sensitive substring)
                if pattern in line_content:
                    matches.append(f"MATCH {filename}:{line_number}:{line_content}")
                    total_matches += 1
                    file_match_count += 1
            
            files_processed += 1
            
        except OSError as e:
            # Close all files before exiting
            for _, f in file_handles:
                f.close()
            error_exit(E_READ, f"error reading '{filename}': {e.strerror}")
        finally:
            f.close()
    
    return matches, total_matches, files_processed

def main():
    # Parse arguments
    pattern, files = parse_arguments(sys.argv[1:])
    
    # Search files
    matches, total_matches, files_processed = search_files(pattern, files)
    
    # Output matches
    for match in matches:
        print(match)
    
    # Output summary
    print(f"OK: MATCHES {total_matches} FILES {files_processed}")
    
    sys.exit(0)

if __name__ == "__main__":
    main()



'''
uses test1.txt and test2.txt

CL:
python greplite.py --pattern "TODO" --files "test1.txt, test2.txt"
python greplite.py --pattern "TODO" --files "test1.txt,, test2.txt" -> gives error: ERROR: E_USAGE: file list contains empty entries
'''