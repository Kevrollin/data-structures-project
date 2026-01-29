"""Mini Campus Funding Manager - CLI

Run: python main.py

This small CLI demonstrates the use of several ADTs:
- Set (built-in) for unique users
- Dicts for mappings
- BST for sorting by amount
- heapq for urgency-priority
- deque for approved queue
"""
from collections import deque
import sys

from models import User, FundingRequest
from structures import RequestBST, push_heap, pop_heap, make_queue, enqueue, dequeue
from storage import save_state, load_state


def input_nonempty(prompt: str) -> str:
    while True:
        v = input(prompt).strip()
        if v:
            return v


def main():
    # ---- Data structures used by the CLI ----
    # `users_set` (Set ADT): store unique user ids/emails to prevent duplicate registration.
    # `users_map` (dict/hash map): maps user_id -> User object for O(1) lookup.
    # `requests_map` (dict/hash map): maps request_id -> FundingRequest for direct access.
    # `bst` (RequestBST): binary search tree keyed by `amount` to obtain requests
    #     in ascending order (used for option 5).
    # `heap` (list used with heapq via helpers): priority queue ordered by `urgency`
    #     (higher urgency reviewed first by admin via option 3).
    # `approved_q` (deque): FIFO queue of approved requests waiting to be funded.
    users_set = set()
    users_map = {}  # user_id -> User
    requests_map = {}  # request_id -> FundingRequest

    bst = RequestBST()
    heap = []
    approved_q = make_queue()

    # load persisted state (if any)
    loaded_users, loaded_requests = load_state()
    if loaded_users:
        users_map.update(loaded_users)
        users_set.update(loaded_users.keys())
    if loaded_requests:
        requests_map.update(loaded_requests)
        for r in requests_map.values():
            bst.insert(r)
            if r.status == "submitted":
                push_heap(heap, r)
            elif r.status == "approved":
                enqueue(approved_q, r)
    req_counter = 1
    # set req_counter after loading
    if requests_map:
        maxn = 0
        for rid in requests_map.keys():
            if rid.startswith("R") and rid[1:].isdigit():
                n = int(rid[1:])
                if n > maxn:
                    maxn = n
        req_counter = maxn + 1

    print("Mini Campus Funding Manager")

    while True:
        print("\nOptions:\n1.Register user\n2.Submit funding request\n3.Admin review highest-priority request\n4.Donate to approved request\n5.View all requests (sorted by amount)\n6.Exit")
        choice = input_nonempty("Select option (1-6): ")

        if choice == "1":
            uid = input_nonempty("User ID (email or unique string): ")
            if uid in users_set:
                print("User already registered.")
                continue
            name = input_nonempty("Name: ")
            role = input_nonempty("Role (student/admin/donor): ").lower()
            if role not in ("student", "admin", "donor"):
                print("Invalid role. Use student/admin/donor.")
                continue
            user = User(id=uid, name=name, role=role)
            users_set.add(uid)
            users_map[uid] = user
            print(f"Registered {role}: {name} ({uid})")
            # persist registration
            save_state(users_map, requests_map)

        elif choice == "2":
            sid = input_nonempty("Student ID: ")
            if sid not in users_map or users_map[sid].role != "student":
                print("Student not found or not a student role.")
                continue
            try:
                amount = float(input_nonempty("Requested amount (e.g., 150.0): "))
            except ValueError:
                print("Invalid amount.")
                continue
            try:
                urgency = int(input_nonempty("Urgency (1-10, 10 highest): "))
            except ValueError:
                print("Invalid urgency.")
                continue
            rid = f"R{req_counter}"
            req_counter += 1
            fr = FundingRequest(id=rid, student_id=sid, amount=amount, urgency=urgency)
            requests_map[rid] = fr
            bst.insert(fr)
            push_heap(heap, fr)
            print(f"Submitted request {rid} for {amount} (urgency {urgency})")
            save_state(users_map, requests_map)

        elif choice == "3":
            # Admin reviews highest-priority request (by urgency)
            aid = input_nonempty("Admin ID: ")
            if aid not in users_map or users_map[aid].role != "admin":
                print("Admin not found or not an admin.")
                continue
            req = pop_heap(heap)
            if not req:
                print("No pending requests to review.")
                continue
            # If the request was already processed elsewhere, skip
            if requests_map.get(req.id) is None or requests_map[req.id].status != "submitted":
                print("Request already handled, pulling next if available.")
                continue
            print(f"Reviewing {req.id}: student={req.student_id}, amount={req.amount}, urgency={req.urgency}")
            dec = input_nonempty("Approve? (y/n): ").lower()
            if dec == "y":
                req.status = "approved"
                enqueue(approved_q, req)
                print(f"Request {req.id} approved and queued for funding.")
                save_state(users_map, requests_map)
            else:
                req.status = "rejected"
                print(f"Request {req.id} rejected.")
                save_state(users_map, requests_map)

        elif choice == "4":
            donor = input_nonempty("Donor ID: ")
            if donor not in users_map or users_map[donor].role != "donor":
                print("Donor not found or not a donor.")
                continue
            if not approved_q:
                print("No approved requests awaiting funding.")
                continue
            print("Approved requests awaiting funding:")
            for r in list(approved_q):
                print(f"- {r.id}: student={r.student_id}, amount={r.amount}")
            rid = input_nonempty("Request ID to fund: ")
            if rid not in requests_map or requests_map[rid].status != "approved":
                print("Request not found or not approved.")
                continue
            try:
                amt = float(input_nonempty("Donation amount: "))
            except ValueError:
                print("Invalid donation amount.")
                continue
            req = requests_map[rid]
            if amt >= req.amount:
                req.status = "funded"
                # remove from queue
                approved_q = deque([x for x in approved_q if x.id != rid])
                print(f"Request {rid} fully funded. Thank you, {users_map[donor].name}!")
                save_state(users_map, requests_map)
            else:
                print("Donation insufficient to fully fund the request. Try again with full amount.")

        elif choice == "5":
            print("All requests sorted by amount (ascending):")
            all_sorted = bst.inorder()
            if not all_sorted:
                print("No requests submitted yet.")
            else:
                for r in all_sorted:
                    print(f"{r.id}: student={r.student_id}, amount={r.amount}, urgency={r.urgency}, status={r.status}")

        elif choice == "6":
            print("Exiting. Goodbye.")
            sys.exit(0)

        else:
            print("Unknown option. Enter 1-6.")


if __name__ == "__main__":
    main()
