import getpass
import json
import os
import sys
from pathlib import Path

from src.teacher_auth import hash_password


TEACHERS_FILE = Path(__file__).with_name("teachers.json")


def main() -> None:
    if len(sys.argv) != 3 or sys.argv[1] != "add":
        raise SystemExit("Usage: python -m src.manage_teachers add USERNAME")

    username = sys.argv[2].strip()
    if not username:
        raise SystemExit("Username cannot be empty")

    password = getpass.getpass("New teacher password: ")
    if not password:
        raise SystemExit("Password cannot be empty")
    if password != getpass.getpass("Confirm password: "):
        raise SystemExit("Passwords do not match")

    if TEACHERS_FILE.exists():
        data = json.loads(TEACHERS_FILE.read_text(encoding="utf-8"))
    else:
        data = {"teachers": {}}

    data.setdefault("teachers", {})[username] = hash_password(password)
    TEACHERS_FILE.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    if os.name == "posix":
        TEACHERS_FILE.chmod(0o600)
    print(f"Updated credentials for teacher '{username}'.")


if __name__ == "__main__":
    main()