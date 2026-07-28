import os

from dotenv import load_dotenv
from project_paths import PROJECT_ROOT


load_dotenv(PROJECT_ROOT / ".env")


def get_required_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or not value.strip():
        raise RuntimeError(
            f"Required environment variable {name!r} is not set. "
            "Copy .env.example to .env and fill in the value."
        )
    return value
