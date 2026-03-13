import json
import os

USER_LIST_FILE = "users.json"


def load_users():
    """Load the list of users from a JSON file using the 'contacts' key."""
    if os.path.exists(USER_LIST_FILE):
        try:
            with open(USER_LIST_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("contacts", [])
        except Exception:
            return []
    return []


def save_users(users):
    """Save the list of users to a JSON file under the 'contacts' key."""
    data = {"contacts": sorted(list(set(users)))}
    with open(USER_LIST_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def add_user(username):
    """Add a user to the persistent list."""
    users = load_users()
    if username not in users:
        users.append(username)
        save_users(users)
        return True
    return False


def remove_user(username):
    """Remove a user from the persistent list."""
    users = load_users()
    if username in users:
        users.remove(username)
        save_users(users)
        return True
    return False
