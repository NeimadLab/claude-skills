"""Database migrations for Loom."""

from pathlib import Path

MIGRATIONS_DIR = Path(__file__).parent


def get_migration(name: str) -> str:
    """Read a migration SQL file."""
    return (MIGRATIONS_DIR / name).read_text()
