from dataclasses import dataclass


# Data models used by the application.
# These simple dataclasses are stored in dictionaries (hash maps)
# so they remain lightweight and serializable in memory.
@dataclass
class User:
    """Simple user record.

    Fields:
    - id: unique identifier (used as key in a Set and user map)
    - name: human-friendly name
    - role: one of 'student', 'admin', or 'donor'

    The `id` values are kept in a Set ADT to prevent duplicate registrations
    and are also stored in a dict mapping `id -> User` for quick lookup.
    """
    id: str
    name: str
    role: str


@dataclass
class FundingRequest:
    """Funding request submitted by a student.

    Fields:
    - id: unique request id (used as key in the requests map)
    - student_id: id of the student who submitted the request
    - amount: numeric requested amount (used as BST key for sorting)
    - urgency: integer urgency (used by the priority heap)
    - status: current lifecycle state ('submitted', 'approved', 'funded', 'rejected')

    Instances are stored simultaneously in multiple ADTs:
    - a dict mapping `request_id -> FundingRequest` for direct access
    - a BST (sorted by `amount`) for viewing requests in amount order
    - a heap (priority queue) keyed by `urgency` for admin review
    - a queue for approved requests waiting to be funded
    """
    id: str
    student_id: str
    amount: float
    urgency: int
    status: str = "submitted"
