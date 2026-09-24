#!/usr/bin/env python3
"""
auto_push.py — Watches the project folder for any changes, and when it
detects something changed, prompts you for a commit message and then
runs add + commit + push automatically.

Usage:
    python3 auto_push.py

Must be run from inside the git repo folder itself (a .git folder must
already exist there). Press Ctrl+C at any time to stop watching.
"""

import subprocess
import sys
import time
from pathlib import Path

CHECK_INTERVAL_SECONDS = 5  # how often to check for changes


def run(cmd: list[str]) -> tuple[int, str, str]:
    """Runs a command and returns (return code, stdout, stderr)."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def ensure_git_repo() -> None:
    if not Path(".git").exists():
        print("Current folder is not a git repo. Run this script inside the project folder.")
        sys.exit(1)


def has_changes() -> bool:
    """Checks whether there are any changes (staged, unstaged, or untracked)."""
    code, out, _ = run(["git", "status", "--porcelain"])
    return bool(out.strip())


def show_changed_files() -> None:
    _, out, _ = run(["git", "status", "--porcelain"])
    print("Changed files:")
    for line in out.splitlines():
        print(f"   {line}")


def commit_and_push(message: str) -> bool:
    steps = [
        (["git", "add", "."], "Staging changes"),
        (["git", "commit", "-m", message], "Creating commit"),
        (["git", "push"], "Pushing to GitHub"),
    ]
    for cmd, description in steps:
        print(f"-> {description} ...")
        code, out, err = run(cmd)
        if out:
            print(out)
        if code != 0:
            # "nothing to commit" isn't a real error, but stop for anything else
            if "nothing to commit" in (out + err).lower():
                continue
            print(f"Step failed: {description}")
            if err:
                print(err)
            return False
    return True


def main() -> None:
    ensure_git_repo()
    print("Watching started... (Ctrl+C to exit)")
    print(f"Checking every {CHECK_INTERVAL_SECONDS} seconds for changes.\n")

    try:
        while True:
            if has_changes():
                show_changed_files()
                message = input("\nEnter commit message (leave empty to skip this time): ").strip()

                if not message:
                    print("Skipped, will check again shortly.\n")
                    time.sleep(CHECK_INTERVAL_SECONDS)
                    continue

                success = commit_and_push(message)
                if success:
                    print("Pushed successfully!\n")
                else:
                    print("Something went wrong, check the messages above.\n")

            time.sleep(CHECK_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\nWatching stopped.")
        sys.exit(0)


if __name__ == "__main__":
    main()
