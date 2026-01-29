"""Simple data structures required by the mini project.

This module provides minimal, well-commented implementations/wrappers
for the ADTs required by the assignment:

- A Binary Search Tree (BST) storing requests keyed by `amount`.
  The BST supports insert and inorder traversal to obtain requests
  sorted by amount (ascending).

- Heap helper functions (wrapping Python's `heapq`) to treat funding
  requests as a priority queue ordered by `urgency` (higher urgency
  = higher priority). We push a tuple with negative urgency so the
  highest urgency becomes the smallest tuple from heapq's perspective.

- Queue helpers built on `collections.deque` to hold approved requests
  waiting to be funded.

The implementations are intentionally minimal and documented so their
roles are explicit when used from the CLI or web handlers.
"""

from collections import deque
import heapq
from typing import List, Optional

from models import FundingRequest


class BSTNode:
    """Node of the BST holding a `FundingRequest`.

    Each node has `left` and `right` children. The BST ordering is
    defined by the `amount` field of `FundingRequest`.
    """

    def __init__(self, req: FundingRequest):
        self.req = req
        self.left: Optional['BSTNode'] = None
        self.right: Optional['BSTNode'] = None


class RequestBST:
    """Binary Search Tree storing FundingRequest nodes sorted by amount.

    Usage notes:
    - Call `insert(req)` to add a request. The tree is keyed on `req.amount`.
    - Call `inorder()` to get a list of `FundingRequest` objects sorted by amount.
    - Duplicate amounts are placed to the right subtree to preserve insertion order
      for equal keys and keep the implementation simple.
    """

    def __init__(self):
        self.root: Optional[BSTNode] = None

    def insert(self, req: FundingRequest):
        """Insert a request into the BST by amount.

        Complexity: average O(log n), worst-case O(n) for unbalanced tree.
        This minimal BST is chosen for clarity to demonstrate ordered traversal
        without depending on external libraries.
        """

        def _insert(node: Optional[BSTNode], r: FundingRequest) -> BSTNode:
            if node is None:
                return BSTNode(r)
            # Keep duplicates to the right to allow equal amounts
            if r.amount < node.req.amount:
                node.left = _insert(node.left, r)
            else:
                node.right = _insert(node.right, r)
            return node

        self.root = _insert(self.root, req)

    def inorder(self) -> List[FundingRequest]:
        """Return list of requests sorted by amount (ascending)."""
        out: List[FundingRequest] = []

        def _in(node: Optional[BSTNode]):
            if not node:
                return
            _in(node.left)
            out.append(node.req)
            _in(node.right)

        _in(self.root)
        return out


# Heap (priority queue) wrapper
def push_heap(heap: list, req: FundingRequest):
    """Push request into heap: higher urgency => higher priority.

    Implementation detail: Python's `heapq` implements a min-heap. To treat
    higher urgency as higher priority, we push a tuple `(-urgency, id, req)`.
    The extra `id` field provides a deterministic tie-breaker for requests
    that share the same urgency value.
    """
    heapq.heappush(heap, (-req.urgency, req.id, req))


def pop_heap(heap: list) -> Optional[FundingRequest]:
    """Pop the highest-priority (highest urgency) request from the heap.

    Returns the `FundingRequest` or `None` if the heap is empty.
    """
    if not heap:
        return None
    _, _, req = heapq.heappop(heap)
    return req


# Approved requests queue
def make_queue():
    """Create a new queue (deque) for approved requests waiting to be funded."""
    return deque()


def enqueue(q: deque, req: FundingRequest):
    """Add a request to the end of the approved queue."""
    q.append(req)


def dequeue(q: deque) -> Optional[FundingRequest]:
    """Remove and return the request at the front of the queue, or None if empty."""
    if not q:
        return None
    return q.popleft()
