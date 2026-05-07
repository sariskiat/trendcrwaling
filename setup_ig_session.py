"""One-time script to save an Instagram login session for Instagrapi.

Run with a dedicated throwaway account — never the real Sukishi account.
Usage:
    IG_USER=user@example.com IG_PASS=yourpass uv run python setup_ig_session.py
"""

from __future__ import annotations

import os
import sys

from instagrapi import Client


def save_session(user: str, password: str, output_file: str) -> None:
    """Log into Instagram and dump session to a JSON file.

    Args:
        user: Instagram account email or username.
        password: Instagram account password.
        output_file: Path to write the session JSON.

    Raises:
        RuntimeError: If login fails.
    """
    cl: Client = Client()
    try:
        cl.login(user, password)
    except Exception as exc:
        raise RuntimeError(f"Instagram login failed for '{user}': {exc}") from exc
    cl.dump_settings(output_file)
    print(f"Session saved to {output_file}")


def main() -> None:
    """Read credentials from environment and save session.

    Raises:
        SystemExit: If IG_USER or IG_PASS env vars are missing.
    """
    ig_user: str = os.environ.get("IG_USER", "")
    ig_pass: str = os.environ.get("IG_PASS", "")
    if not ig_user or not ig_pass:
        print("Error: set IG_USER and IG_PASS environment variables", file=sys.stderr)
        sys.exit(1)
    output_file: str = os.environ.get("IG_SESSION_FILE", "ig_session.json")
    save_session(ig_user, ig_pass, output_file)


if __name__ == "__main__":
    main()
