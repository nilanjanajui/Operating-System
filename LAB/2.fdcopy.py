# 2
import sys
import os
import zlib

# Error codes
E_USAGE = "E_USAGE"
E_OPEN_SRC = "E_OPEN_SRC"
E_OPEN_DST = "E_OPEN_DST"
E_EXISTS = "E_EXISTS"
E_READ = "E_READ"
E_WRITE = "E_WRITE"
E_CLOSE = "E_CLOSE"
E_RANGE = "E_RANGE"

def error_exit(code, message):
    """Print error message and exit with non-zero status."""
    print(f"ERROR: {code}: {message}", file=sys.stderr)
    sys.exit(1)

def parse_arguments(args):
    """Parse command line arguments."""
    src = None
    dst = None
    buffer_size = 4096  # Default buffer size
    force = False
    
    i = 0
    while i < len(args):
        if args[i] == "--src":
            if i + 1 >= len(args):
                error_exit(E_USAGE, "missing value for --src")
            src = args[i + 1]
            i += 2
        elif args[i] == "--dst":
            if i + 1 >= len(args):
                error_exit(E_USAGE, "missing value for --dst")
            dst = args[i + 1]
            i += 2
        elif args[i] == "--buf":
            if i + 1 >= len(args):
                error_exit(E_USAGE, "missing value for --buf")
            try:
                buffer_size = int(args[i + 1])
            except ValueError:
                error_exit(E_USAGE, "buffer size must be an integer")
            i += 2
        elif args[i] == "--force":
            force = True
            i += 1
        else:
            error_exit(E_USAGE, f"unrecognized argument: {args[i]}")
    
    if src is None:
        error_exit(E_USAGE, "missing required --src")
    if dst is None:
        error_exit(E_USAGE, "missing required --dst")
    
    # Validate buffer size
    if buffer_size < 1 or buffer_size > 1048576:  # 1..1048576 bytes
        error_exit(E_RANGE, "buffer size must be 1..1048576 bytes")
    
    return src, dst, buffer_size, force

def open_source(src_path):
    """Open source file or stdin."""
    if src_path == "-":
        # Use stdin (file descriptor 0)
        return 0  # STDIN_FILENO
    else:
        try:
            # O_RDONLY: read only, no create
            fd = os.open(src_path, os.O_RDONLY)
            return fd
        except OSError as e:
            error_exit(E_OPEN_SRC, f"cannot open source: {e.strerror}")

def open_destination(dst_path, force):
    """Open destination file with appropriate flags."""
    # Default flags: write only, create, exclusive (fail if exists)
    flags = os.O_WRONLY | os.O_CREAT
    
    if not force:
        flags |= os.O_EXCL  # Fail if file exists
    
    # Default permissions: rw-r--r-- (0644)
    mode = 0o644
    
    try:
        fd = os.open(dst_path, flags, mode)
        return fd
    except OSError as e:
        if e.errno == 17:  # EEXIST: File exists
            error_exit(E_EXISTS, "destination already exists (use --force)")
        else:
            error_exit(E_OPEN_DST, f"cannot open destination: {e.strerror}")

def copy_file(fd_src, fd_dst, buffer_size):
    """
    Copy from fd_src to fd_dst using buffer_size chunks.
    Returns (bytes_copied, crc32_value)
    """
    bytes_copied = 0
    crc32 = 0
    
    while True:
        # Read chunk from source
        try:
            chunk = os.read(fd_src, buffer_size)
        except OSError as e:
            error_exit(E_READ, f"read error: {e.strerror}")
        
        # EOF reached
        if not chunk:
            break
        
        # Write chunk to destination (handle partial writes)
        bytes_written = 0
        while bytes_written < len(chunk):
            try:
                written = os.write(fd_dst, chunk[bytes_written:])
            except OSError as e:
                error_exit(E_WRITE, f"write error: {e.strerror}")
            
            if written == 0:
                error_exit(E_WRITE, "write returned 0 bytes")
            
            bytes_written += written
        
        # Update CRC32 and byte count
        crc32 = zlib.crc32(chunk, crc32)
        bytes_copied += len(chunk)
    
    return bytes_copied, crc32

def close_file(fd, fd_name):
    """Close file descriptor with error handling."""
    if fd > 0:  # Don't close stdin (fd=0) if we didn't open it
        try:
            os.close(fd)
        except OSError as e:
            error_exit(E_CLOSE, f"cannot close {fd_name}: {e.strerror}")

def main():
    # Parse arguments
    src_path, dst_path, buffer_size, force = parse_arguments(sys.argv[1:])
    
    # Open source
    fd_src = open_source(src_path)
    
    # Open destination
    fd_dst = open_destination(dst_path, force)
    
    try:
        # Copy data
        bytes_copied, crc32_value = copy_file(fd_src, fd_dst, buffer_size)
        
        # Ensure CRC32 is 32-bit unsigned
        crc32_value = crc32_value & 0xffffffff
        
        # Output results
        print(f"OK: COPIED {bytes_copied} BYTES")
        print(f"OK: CRC32 {crc32_value:08x}")
        
    finally:
        # Always close files
        close_file(fd_src, "source")
        close_file(fd_dst, "destination")
    
    sys.exit(0)

if __name__ == "__main__":
    main()