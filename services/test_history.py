import json
import os
from datetime import datetime

HISTORY_FILE = "test_history.json"


def load_test_history():
    if not os.path.exists(HISTORY_FILE):
        return []

    with open(HISTORY_FILE, "r") as f:
        return json.load(f)


def save_test_result(result):
    history = load_test_history()
    history.append(result)

    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)


def get_user_history(username):
    return [
        item for item in load_test_history()
        if item.get("username") == username
    ]


def get_leaderboard():
    history = load_test_history()
    scores = {}

    for item in history:
        user = item.get("username")
        if not user:
            continue

        percent = item.get("percentage", 0)

        if user not in scores:
            scores[user] = {
                "tests": 0,
                "best_score": 0,
                "average_score": 0,
                "total_score": 0
            }

        scores[user]["tests"] += 1
        scores[user]["total_score"] += percent
        scores[user]["best_score"] = max(scores[user]["best_score"], percent)

    leaderboard = []

    for user, data in scores.items():
        data["average_score"] = round(data["total_score"] / data["tests"], 2)
        leaderboard.append({
            "username": user,
            "tests": data["tests"],
            "best_score": data["best_score"],
            "average_score": data["average_score"]
        })

    return sorted(
        leaderboard,
        key=lambda x: x["average_score"],
        reverse=True
    )

def clear_test_history():
    with open(HISTORY_FILE, "w") as f:
        json.dump([], f, indent=4)


def clear_user_test_history(username):
    history = load_test_history()

    updated_history = [
        item for item in history
        if item.get("username") != username
    ]

    with open(HISTORY_FILE, "w") as f:
        json.dump(updated_history, f, indent=4)
