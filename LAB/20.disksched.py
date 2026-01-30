
import sys
import argparse
from typing import List

def error_exit(code: str, message: str):
    print(f"ERROR: {code}: {message}", file=sys.stderr)
    sys.exit(1)

class DiskScheduler:
    def __init__(self, max_cylinder: int, start: int, direction: str):
        self.max_cylinder = max_cylinder
        self.start = start
        self.direction = direction  # 'left' or 'right'
    
    def fcfs(self, requests: List[int]) -> tuple[List[int], int]:
        """First-Come, First-Served."""
        order = requests.copy()
        moves = self._calculate_moves(order)
        return order, moves
    
    def sstf(self, requests: List[int]) -> tuple[List[int], int]:
        """Shortest Seek Time First."""
        order = []
        remaining = requests.copy()
        current = self.start
        
        while remaining:
            # Find closest request
            closest_idx = 0
            closest_dist = abs(remaining[0] - current)
            
            for i in range(1, len(remaining)):
                dist = abs(remaining[i] - current)
                if dist < closest_dist or (dist == closest_dist and remaining[i] < remaining[closest_idx]):
                    closest_dist = dist
                    closest_idx = i
            
            order.append(remaining[closest_idx])
            current = remaining[closest_idx]
            remaining.pop(closest_idx)
        
        moves = self._calculate_moves(order)
        return order, moves
    
    def scan(self, requests: List[int]) -> tuple[List[int], int]:
        """SCAN (Elevator) algorithm."""
        order = []
        current = self.start
        
        if self.direction == 'right':
            # Moving right first
            right_requests = [r for r in requests if r >= current]
            right_requests.sort()
            order.extend(right_requests)
            
            # Then move to max cylinder if needed
            if right_requests:
                order.append(self.max_cylinder)
            
            # Then serve left side
            left_requests = [r for r in requests if r < current]
            left_requests.sort(reverse=True)
            order.extend(left_requests)
        
        else:  # left
            # Moving left first
            left_requests = [r for r in requests if r <= current]
            left_requests.sort(reverse=True)
            order.extend(left_requests)
            
            # Then move to 0 if needed
            if left_requests:
                order.append(0)
            
            # Then serve right side
            right_requests = [r for r in requests if r > current]
            right_requests.sort()
            order.extend(right_requests)
        
        # Remove duplicates of end cylinders if they weren't in original requests
        # (We added them to simulate going to the end)
        final_order = []
        for cyl in order:
            if cyl in requests or cyl == 0 or cyl == self.max_cylinder:
                final_order.append(cyl)
                if cyl in requests:
                    # Remove one occurrence from requests list
                    idx = requests.index(cyl)
                    requests.pop(idx)
        
        moves = self._calculate_moves(final_order)
        return final_order, moves
    
    def cscan(self, requests: List[int]) -> tuple[List[int], int]:
        """C-SCAN (Circular SCAN) algorithm."""
        order = []
        current = self.start
        
        if self.direction == 'right':
            # Moving right first
            right_requests = [r for r in requests if r >= current]
            right_requests.sort()
            order.extend(right_requests)
            
            # Go to max cylinder
            if right_requests:
                order.append(self.max_cylinder)
            
            # Jump to 0 (counts as movement)
            order.append(0)
            
            # Then serve remaining left side
            left_requests = [r for r in requests if r < current]
            left_requests.sort()
            order.extend(left_requests)
        
        else:  # left
            # Moving left first
            left_requests = [r for r in requests if r <= current]
            left_requests.sort(reverse=True)
            order.extend(left_requests)
            
            # Go to 0
            if left_requests:
                order.append(0)
            
            # Jump to max cylinder (counts as movement)
            order.append(self.max_cylinder)
            
            # Then serve remaining right side
            right_requests = [r for r in requests if r > current]
            right_requests.sort(reverse=True)
            order.extend(right_requests)
        
        # Remove end cylinders if they weren't in original requests
        final_order = []
        temp_requests = requests.copy()
        for cyl in order:
            if cyl in temp_requests or cyl == 0 or cyl == self.max_cylinder:
                final_order.append(cyl)
                if cyl in temp_requests:
                    idx = temp_requests.index(cyl)
                    temp_requests.pop(idx)
        
        moves = self._calculate_moves(final_order)
        return final_order, moves
    
    def _calculate_moves(self, order: List[int]) -> int:
        """Calculate total head movement for service order."""
        total = 0
        current = self.start
        for cyl in order:
            total += abs(cyl - current)
            current = cyl
        return total

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--max', type=int, required=True)
    parser.add_argument('--start', type=int, required=True)
    parser.add_argument('--dir', choices=['left', 'right'], required=True)
    
    args = parser.parse_args()
    
    # Validate
    if args.max < 1:
        error_exit('E_RANGE', 'max cylinder must be >= 1')
    if not (0 <= args.start <= args.max):
        error_exit('E_RANGE', f'start must be 0..{args.max}')
    
    # Read input
    try:
        line = sys.stdin.readline()
        if not line:
            error_exit('E_INPUT', 'empty input')
        L = int(line.strip())
        
        line = sys.stdin.readline()
        if not line:
            error_exit('E_INPUT', 'missing requests')
        requests = list(map(int, line.strip().split()))
        
        if len(requests) != L:
            error_exit('E_INPUT', f'expected {L} requests, got {len(requests)}')
        
        for req in requests:
            if not (0 <= req <= args.max):
                error_exit('E_RANGE', f'request {req} out of range 0..{args.max}')
    
    except ValueError:
        error_exit('E_INPUT', 'invalid number format')
    
    # Create scheduler and run algorithms
    scheduler = DiskScheduler(args.max, args.start, args.dir)
    
    # FCFS
    order, moves = scheduler.fcfs(requests.copy())
    print("ALG FCFS")
    print(f"OK: ORDER {' '.join(map(str, order))}")
    print(f"OK: MOVES {moves}")
    
    # SSTF
    order, moves = scheduler.sstf(requests.copy())
    print("\nALG SSTF")
    print(f"OK: ORDER {' '.join(map(str, order))}")
    print(f"OK: MOVES {moves}")
    
    # SCAN
    order, moves = scheduler.scan(requests.copy())
    print("\nALG SCAN")
    print(f"OK: ORDER {' '.join(map(str, order))}")
    print(f"OK: MOVES {moves}")
    
    # C-SCAN
    order, moves = scheduler.cscan(requests.copy())
    print("\nALG C-SCAN")
    print(f"OK: ORDER {' '.join(map(str, order))}")
    print(f"OK: MOVES {moves}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())