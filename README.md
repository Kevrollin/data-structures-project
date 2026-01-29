# Mini Campus Funding Manager

Small command-line application simulating a campus funding system.

Run:

```
python main.py
```

From project root (`dsa-mini-project`) run:

```bash
./run.sh
```

Or run directly (from project root):

```bash
python3 campus_funding/main.py
```

Web mode:

Install Flask if needed:

```bash
pip install flask
```

Then run the web UI from project root:

```bash
./run_web.sh
```

Open http://127.0.0.1:5000/ in your browser.

Data structures used:
- Set (Python built-in): store unique user IDs to prevent duplicate registration.
- Dict (hash map): map `user_id -> User` and `request_id -> FundingRequest`.
- Binary Search Tree (BST): store funding requests sorted by `amount` and provide inorder traversal for viewing sorted requests.
- Heap (`heapq`): priority queue storing requests by `urgency` (higher urgency = higher priority) used during admin review.
- Queue (`collections.deque`): queue for approved requests waiting to be funded.

Files:
- `main.py` - CLI and application flow
- `models.py` - `User` and `FundingRequest` dataclasses
- `structures.py` - BST, heap helpers, queue helpers
- `README.md` - this file

Persistence / seed data
- The app uses a small JSON file at `campus_funding/data.json` to persist users and requests.
- A sample seed file is included as `campus_funding/data.example.json`.
- To start with the seeded demo data (recommended for demo), copy the example:

```bash
cp campus_funding/data.example.json campus_funding/data.json
```

Sharing with teammates
- If you want teammates to get the seeded data when they clone the repo, either commit `campus_funding/data.json` (quick) or commit only `data.example.json` and instruct them to copy it locally (safer).

Virtual environment (recommended)
```bash
python3 -m venv .venv
source .venv/bin/activate
# Mini Campus Funding Manager

A concise, educational demo application that simulates a small campus funding workflow. The project demonstrates core abstract data types (ADTs) applied in a small, self-contained Python project with both a CLI and a minimal Flask web UI.

Why this project
- Intended as a teaching/demo tool for engineers and students to see simple ADTs mapped to common application patterns.
- Keeps dependencies minimal and code small so team members can quickly inspect the implementation and run the demo locally.

Quick start

1. (Recommended) Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r campus_funding/requirements.txt  # if present, otherwise `pip install flask`
```

2. Run the web UI (recommended for demos):

```bash
./run_web.sh
# or
python3 campus_funding/app.py
```

Open: http://127.0.0.1:5000/

3. Or run the CLI:

```bash
python3 campus_funding/main.py
```

Persistence and seed data
- Live state is stored in `campus_funding/data.json`.
- A seeded example is provided at `campus_funding/data.example.json` — to use it:

```bash
cp campus_funding/data.example.json campus_funding/data.json
```

ADT usage (where each structure appears)
- `Set` (`set`): Used to enforce unique student IDs at registration. See `campus_funding/main.py` and `campus_funding/app.py` for checks around registration.
- `Dict` (hash map): The primary in-memory storage is implemented as Python dictionaries mapping `user_id -> User` and `request_id -> FundingRequest` for O(1) lookup. Found in `campus_funding/storage.py`, `main.py`, and `app.py`.
- `Binary Search Tree` (`campus_funding/structures.py`): `RequestBST` stores requests keyed by `amount` to provide an ordered (sorted-by-amount) view via inorder traversal used by the "view sorted requests" feature.
- `Heap` (`heapq` wrapper in `campus_funding/structures.py`): The admin review flow uses a priority heap keyed by `urgency` so the highest-urgency requests are reviewed first. Internals: items pushed as tuples (−urgency, request_id, request_obj) to ensure correct ordering.
- `Queue` (`collections.deque` in `campus_funding/structures.py`): Approved requests are enqueued into a FIFO queue representing the funding pipeline.

Files & responsibilities
- `campus_funding/models.py` — `User` and `FundingRequest` dataclasses and lightweight helpers.
- `campus_funding/structures.py` — Implementations and small helpers for BST, heap, and queue.
- `campus_funding/storage.py` — JSON-based save/load for `users` and `requests` maps.
- `campus_funding/main.py` — CLI entrypoint and interactive menu.
- `campus_funding/app.py` — Flask web app; routes for register, submit, admin review, donor actions.
- `campus_funding/templates/` & `campus_funding/static/` — Jinja2 templates and small CSS/JS used by the web UI.
- `campus_funding/data.example.json` — Example/demo data.
- `campus_funding/data.json` — Live persisted state (can be added to `.gitignore` if you prefer not to commit it).

Workflow summary
- Students register (unique ID enforced via `set`).
- Students submit funding requests (`amount`, `urgency`). Requests are stored in the `requests` dict and also pushed into the admin `heap` for prioritized review.
- Admin pops requests from the `heap` for review; approved requests are pushed into the `approved` `deque` (queue).
- Donors view approved requests and can donate; donations decrement the outstanding amount. When fully funded, requests are removed and state is saved.

Design trade-offs and limitations
- Persistence: Uses a simple JSON file for clarity. This approach is not safe for concurrent writers and not recommended for production environments. Replace with a database for real deployments.
- Authentication: There is no authentication; actions are performed by numeric IDs for simplicity. Add auth if you extend the app.
- Atomic updates: Save operations are simple writes to `data.json`. For improved safety use atomic file replace or a transactional data store.

Developer notes
- Testing: Add unit tests for `structures.py` and `storage.py` when adding features. Currently no automated tests are included.
- Formatting & linting: Follow PEP8; run `black` and `flake8` during development.

Contributing
- Fork, implement changes on a topic branch, and open a PR. Include a short description of ADT or file changes.
- Suggested first commit message for a polished demo:

```
feat: add Mini Campus Funding Manager demo with CLI, Flask UI, persistence, and ADT examples
```

Common commands
- Re-seed demo data:

```bash
cp campus_funding/data.example.json campus_funding/data.json
```
- Start web UI:

```bash
./run_web.sh
```
- Start CLI:

```bash
python3 campus_funding/main.py
```

Contact & next steps
- If the team wants: add DB-backed persistence, authentication, automated tests, and CI. Open an issue or submit a PR describing desired features.

License
- None included. Add a license when you publish or share externally.

Thank you — this project is intentionally small and focused so you can read the code quickly and see concrete ADT usage patterns.
