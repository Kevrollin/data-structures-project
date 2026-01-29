from flask import Flask, render_template, request, redirect, url_for, flash

from models import User, FundingRequest
from structures import RequestBST, push_heap, pop_heap, make_queue, enqueue
from storage import save_state, load_state

app = Flask(__name__)
app.secret_key = "dev-mode-key"

# In-memory data structures used by the web UI (matching the CLI):
# - `users_set` (Set): tracks unique user ids to prevent duplicate registrations.
# - `users_map` (dict): maps user_id -> User for quick lookup.
# - `requests_map` (dict): maps request_id -> FundingRequest for direct access.
# - `bst` (RequestBST): BST keyed by amount for sorted views.
# - `heap` (list used with heapq helpers): priority queue ordered by urgency.
# - `approved_q` (deque): FIFO queue of approved requests awaiting funding.
users_set = set()
users_map = {}
requests_map = {}
bst = RequestBST()
heap = []
approved_q = make_queue()
req_counter = 1

# Try to load persisted state from disk. If present, reconstruct in-memory ADTs.
loaded_users, loaded_requests = load_state()
if loaded_users:
    users_map.update(loaded_users)
    users_set.update(loaded_users.keys())

if loaded_requests:
    requests_map.update(loaded_requests)
    # rebuild BST, heap, and approved queue from the loaded requests
    for r in requests_map.values():
        bst.insert(r)
        if r.status == "submitted":
            push_heap(heap, r)
        elif r.status == "approved":
            enqueue(approved_q, r)
    # set next request counter based on highest existing R<number>
    maxn = 0
    for rid in requests_map.keys():
        if rid.startswith("R") and rid[1:].isdigit():
            n = int(rid[1:])
            if n > maxn:
                maxn = n
    req_counter = maxn + 1


def get_sorted_requests():
    return bst.inorder()


@app.route("/")
def index():
    return render_template(
        "index.html",
        users=list(users_map.values()),
        students=[u for u in users_map.values() if u.role == "student"],
        approved=list(approved_q),
        sorted_requests=get_sorted_requests(),
        heap_top=(heap[0][2] if heap else None),
    )


@app.route("/donor")
def donor_page():
    # show donors a view of students and approved requests; allow donations
    # prepare lists: students and approved requests
    students = [u for u in users_map.values() if u.role == "student"]
    # provide current pending approved requests
    return render_template("donor.html", students=students, approved=list(approved_q), requests=list(requests_map.values()))


@app.route("/admin")
def admin_page():
    # admin view: list all users and pending requests (by urgency)
    users = list(users_map.values())
    # build a view of pending requests sorted by urgency (highest first)
    heap_items = sorted([(-u, rid, req) for (u, rid, req) in [(item[0], item[1], item[2]) for item in heap]], reverse=True) if heap else []
    # easier: build list of pending requests with urgency
    pending = [r for r in requests_map.values() if r.status == "submitted"]
    pending_sorted = sorted(pending, key=lambda x: -x.urgency)
    return render_template("admin.html", users=users, pending=pending_sorted)


@app.route("/register", methods=["POST"])
def register():
    uid = request.form.get("user_id", "").strip()
    name = request.form.get("name", "").strip()
    role = request.form.get("role", "").strip().lower()
    if not uid or not name or role not in ("student", "admin", "donor"):
        flash("Invalid registration data", 'error')
        return redirect(url_for("index"))
    if uid in users_set:
        flash("User already registered", 'error')
        return redirect(url_for("index"))
    users_set.add(uid)
    users_map[uid] = User(id=uid, name=name, role=role)
    flash(f"Registered {role}: {name}", 'success')
    # persist
    save_state(users_map, requests_map)
    return redirect(url_for("index"))


@app.route("/submit", methods=["POST"])
def submit():
    global req_counter
    sid = request.form.get("student_id", "").strip()
    if sid not in users_map or users_map[sid].role != "student":
        flash("Student not found or invalid role", 'error')
        return redirect(url_for("index"))
    try:
        amount = float(request.form.get("amount", "0"))
        urgency = int(request.form.get("urgency", "1"))
    except ValueError:
        flash("Invalid amount or urgency", 'error')
        return redirect(url_for("index"))
    rid = f"R{req_counter}"
    req_counter += 1
    fr = FundingRequest(id=rid, student_id=sid, amount=amount, urgency=urgency)
    requests_map[rid] = fr
    bst.insert(fr)
    push_heap(heap, fr)
    flash(f"Submitted {rid} for {amount}", 'success')
    # persist
    save_state(users_map, requests_map)
    return redirect(url_for("index"))


@app.route("/admin/review", methods=["POST"])
def admin_review():
    admin_id = request.form.get("admin_id", "").strip()
    if admin_id not in users_map or users_map[admin_id].role != "admin":
        flash("Admin not found or invalid role", 'error')
        return redirect(url_for("index"))
    req = pop_heap(heap)
    if not req:
        flash("No pending requests to review", 'error')
        return redirect(url_for("index"))
    # keep request in map; show decision form
    return render_template("review.html", req=req)


@app.route("/admin/decide", methods=["POST"])
def admin_decide():
    rid = request.form.get("request_id", "").strip()
    decision = request.form.get("decision", "no")
    req = requests_map.get(rid)
    if not req:
        flash("Request not found", 'error')
        return redirect(url_for("index"))
    if decision == "approve":
        req.status = "approved"
        enqueue(approved_q, req)
        flash(f"Request {rid} approved", 'success')
    else:
        req.status = "rejected"
        flash(f"Request {rid} rejected", 'success')
    # persist changes
    save_state(users_map, requests_map)
    return redirect(url_for("index"))


@app.route("/donate", methods=["POST"])
def donate():
    donor = request.form.get("donor_id", "").strip()
    rid = request.form.get("request_id", "").strip()
    try:
        amt = float(request.form.get("donation", "0"))
    except ValueError:
        flash("Invalid donation amount", 'error')
        return redirect(url_for("index"))
    if donor not in users_map or users_map[donor].role != "donor":
        flash("Donor not found or invalid role", 'error')
        return redirect(url_for("index"))
    req = requests_map.get(rid)
    if not req or req.status != "approved":
        flash("Request not found or not approved", 'error')
        return redirect(url_for("index"))
    if amt >= req.amount:
        req.status = "funded"
        # remove from approved_q
        # rebuild to remove
        from collections import deque

        newq = deque([x for x in approved_q if x.id != rid])
        approved_q.clear()
        approved_q.extend(newq)
        flash(f"Request {rid} fully funded. Thank you!", 'success')
    else:
        flash("Donation insufficient to fully fund the request", 'error')
    # persist
    save_state(users_map, requests_map)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
