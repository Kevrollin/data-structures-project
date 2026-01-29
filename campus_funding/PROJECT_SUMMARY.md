# Mini Campus Funding Manager — Project Summary

Title
-----

Mini Campus Funding Manager

Introduction
------------

The Mini Campus Funding Manager is a compact, educational Python project that demonstrates how fundamental abstract data types (ADTs) can be applied to a real-world inspired workflow: managing student funding requests, prioritizing reviews, and processing donations. The project intentionally keeps dependencies and scope small so team members can easily read, run, and modify the codebase.

Objective
---------

- Provide a runnable demo (CLI + minimal Flask web UI) that models a campus funding workflow.
- Illustrate concrete uses of five ADTs: Set, Hash Map (dict), Binary Search Tree, Heap (priority queue), and Queue.
- Persist small datasets locally to allow continued experimentation without a full database.

Body — Key Concepts and Architecture
-----------------------------------

1. Core workflow

- Students register with a unique numeric ID and can submit funding requests describing an amount and an urgency level.
- Requests are reviewed by an admin who prioritizes by urgency and either approves or rejects requests.
- Approved requests are enqueued for funding; donors can view approved requests and donate until the amount is fully funded.
- All operations persist to a local JSON file to survive restarts.

2. Data model

- `User` — Represents a student or donor (stored in a `dict` keyed by `user_id`).
- `FundingRequest` — Holds `id`, `student_id`, `amount`, `urgency`, and `status`.

3. ADT mapping (where each structure is used)

- `Set` (`set`): Enforces unique student IDs during registration, preventing duplicates.
- `Dict` (`dict`): Primary in-memory storage mapping `user_id -> User` and `request_id -> FundingRequest` for fast O(1) lookup.
- `Binary Search Tree` (in `campus_funding/structures.py`): Maintains requests keyed by `amount` to support an ordered view (in-order traversal) for reporting and inspection.
- `Heap` (`heapq` wrapper in `campus_funding/structures.py`): Priority queue for admin review ordered by `urgency` (higher urgency first). Uses tuple keys to break ties deterministically.
- `Queue` (`collections.deque` in `campus_funding/structures.py`): FIFO queue for approved requests awaiting funding, modeling a simple funding pipeline.

4. Persistence

- Implemented in `campus_funding/storage.py` using a simple JSON format at `campus_funding/data.json`.
- The app loads persisted state on startup and writes state after every mutation (register/submit/approve/reject/donate).
- Trade-off: easy to inspect and seed, but not safe for concurrent writers — use a DB for production.

5. Interfaces

- CLI: `python3 campus_funding/main.py` — interactive menu-driven demo.
- Web: `./run_web.sh` to start a minimal Flask app (`campus_funding/app.py`) with templates in `campus_funding/templates/` and assets in `campus_funding/static/`.

6. File map (high level)

- `campus_funding/models.py` — data classes for `User` and `FundingRequest`.
- `campus_funding/structures.py` — BST, heap, and queue helpers.
- `campus_funding/storage.py` — JSON persistence.
- `campus_funding/main.py` — CLI entrypoint and example flows.
- `campus_funding/app.py` — Flask web UI with register/submit/admin/donor routes.
- `campus_funding/data.example.json` — seed data for demos.

Short notes (practical points for teammates)
-----------------------------------------

- To seed a fresh demo: `cp campus_funding/data.example.json campus_funding/data.json`.
- Run the web UI at http://127.0.0.1:5000 using `./run_web.sh`.
- The project deliberately avoids external DBs or auth to focus on ADT patterns — do not use it as-is for production workloads.

Conclusion
----------

The Mini Campus Funding Manager is a targeted learning tool: it solves a compact practical problem (managing prioritized funding requests and donations) while simultaneously providing a clear, hands-on demonstration of how common ADTs (Set, dict, BST, Heap, Queue) map to application responsibilities. The codebase is intentionally small to make design decisions visible and editable by team members. For production or multi-user environments, replace JSON persistence with a database and add authentication and concurrency control.

----

File location: `campus_funding/PROJECT_SUMMARY.md`
