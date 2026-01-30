# 1
import sys
import re

# Error codes
E_USAGE = "E_USAGE"
E_OCTAL = "E_OCTAL"
E_RANGE = "E_RANGE"

def error_exit(code, message):
    """Print error message and exit with non-zero status."""
    print(f"ERROR: {code}: {message}", file=sys.stderr)
    sys.exit(1)

def parse_arguments(args):
    """Parse command line arguments."""
    mode = None
    umask = "0000"  # Default umask
    
    i = 0
    while i < len(args):
        if args[i] == "--mode":
            if i + 1 >= len(args):
                error_exit(E_USAGE, "missing value for --mode")
            mode = args[i + 1]
            i += 2
        elif args[i] == "--umask":
            if i + 1 >= len(args):
                error_exit(E_USAGE, "missing value for --umask")
            umask = args[i + 1]
            i += 2
        else:
            error_exit(E_USAGE, f"unrecognized argument: {args[i]}")
    
    if mode is None:
        error_exit(E_USAGE, "missing required --mode")
    
    return mode, umask

def validate_octal(value, name):
    """Validate that value is exactly 4 octal digits (0000-0777)."""
    # Check length
    if len(value) != 4:
        return False, f"{name} must be exactly 4 digits"
    
    # Check each character is octal digit
    if not re.match(r'^[0-7]{4}$', value):
        return False, f"{name} must be 4-digit octal (0000-0777)"
    
    # Convert to integer and check range
    try:
        int_val = int(value, 8)
        if int_val < 0 or int_val > 0o777:
            return False, f"{name} must be in range 0000-0777"
    except ValueError:
        return False, f"{name} must be 4-digit octal (0000-0777)"
    
    return True, None

def octal_to_symbolic(octal_str):
    """Convert 4-digit octal string to symbolic rwxrwxrwx format."""
    # We only care about last 3 digits (permissions)
    # First digit is special permissions (sticky bit, setuid, setgid)
    perm_str = octal_str[-3:] if len(octal_str) == 4 else octal_str
    
    symbolic = ""
    for digit in perm_str:
        oct_val = int(digit)
        
        # Build rwx for this digit
        r = 'r' if oct_val & 4 else '-'
        w = 'w' if oct_val & 2 else '-'
        x = 'x' if oct_val & 1 else '-'
        
        symbolic += r + w + x
    
    return symbolic

def calculate_effective(mode_str, umask_str):
    """Calculate effective mode = mode & (~umask)."""
    mode_int = int(mode_str, 8)
    umask_int = int(umask_str, 8)
    
    # Apply umask: effective = mode AND (NOT umask)
    # Mask with 0o777 to ensure we only get 9 permission bits
    effective_int = mode_int & (~umask_int) & 0o777
    
    # Format back to 4-digit octal with leading zeros
    return f"{effective_int:04o}"

def main():
    # Parse arguments (skip program name)
    mode_str, umask_str = parse_arguments(sys.argv[1:])
    
    # Validate inputs
    valid, msg = validate_octal(mode_str, "mode")
    if not valid:
        error_exit(E_OCTAL, msg)
    
    valid, msg = validate_octal(umask_str, "umask")
    if not valid:
        error_exit(E_OCTAL, msg)
    
    # Calculate effective mode
    effective_str = calculate_effective(mode_str, umask_str)
    
    # Generate symbolic representation
    symbolic_str = octal_to_symbolic(effective_str)
    
    # Output results
    print(f"OK: EFFECTIVE {effective_str}")
    print(f"OK: SYMBOLIC {symbolic_str}")
    
    sys.exit(0)

if __name__ == "__main__":
    main()