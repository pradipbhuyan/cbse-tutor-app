import json
import os

PROGRESS_FILE = "student_progress.json"

def load_progress():
    if not os.path.exists(PROGRESS_FILE):
        return {}
    with open(PROGRESS_FILE, "r") as f:
        return json.load(f)

def save_progress(progress):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=4)

def get_topic_key(username, mode, subject, chapter):
    return f"{username}|{mode}|{subject}|{chapter}"

def get_current_step(username, mode, subject, chapter):
    progress = load_progress()
    key = get_topic_key(username, mode, subject, chapter)
    return progress.get(key, {}).get("current_step", 0)

def save_current_step(username, mode, subject, chapter, step):
    progress = load_progress()
    key = get_topic_key(username, mode, subject, chapter)

    if key not in progress:
        progress[key] = {}

    progress[key]["current_step"] = step
    save_progress(progress)

def mark_completed(username, mode, subject, chapter):
    progress = load_progress()
    key = get_topic_key(username, mode, subject, chapter)

    if key not in progress:
        progress[key] = {}

    progress[key]["completed"] = True
    save_progress(progress)
