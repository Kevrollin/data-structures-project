"""Simple JSON file persistence for in-memory state.

This keeps the project small (no DB) but preserves users and requests
across server restarts by writing a `data.json` file in the app folder.
"""
import json
import os
from typing import Tuple, Dict

from models import User, FundingRequest


DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")


def save_state(users_map: Dict[str, User], requests_map: Dict[str, FundingRequest], path: str = DATA_FILE):
    payload = {
        "users": [
            {"id": u.id, "name": u.name, "role": u.role} for u in users_map.values()
        ],
        "requests": [
            {"id": r.id, "student_id": r.student_id, "amount": r.amount, "urgency": r.urgency, "status": r.status}
            for r in requests_map.values()
        ],
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def load_state(path: str = DATA_FILE) -> Tuple[Dict[str, User], Dict[str, FundingRequest]]:
    users_map = {}
    requests_map = {}
    if not os.path.exists(path):
        return users_map, requests_map
    try:
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)
    except Exception:
        return users_map, requests_map

    for u in payload.get("users", []):
        users_map[u["id"]] = User(id=u["id"], name=u.get("name", ""), role=u.get("role", "student"))

    for r in payload.get("requests", []):
        try:
            amt = float(r.get("amount", 0))
        except Exception:
            amt = 0.0
        try:
            urg = int(r.get("urgency", 1))
        except Exception:
            urg = 1
        requests_map[r["id"]] = FundingRequest(id=r["id"], student_id=r.get("student_id", ""), amount=amt, urgency=urg, status=r.get("status", "submitted"))

    return users_map, requests_map
