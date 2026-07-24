import os
from pathlib import Path

from dotenv import load_dotenv


project_root = Path(__file__).resolve().parents[1]
load_dotenv(project_root / ".env")


def get_required_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or not value.strip():
        raise RuntimeError(
            f"Required environment variable {name!r} is not set. "
            "Copy .env.example to .env and fill in the value."
        )
    return value
