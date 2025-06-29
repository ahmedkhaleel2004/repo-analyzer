"""SQLite cache for GitHub API responses."""

import aiosqlite
import json
from typing import Optional, Any
from datetime import datetime, timezone, timedelta


class Cache:
    """Async SQLite cache for API responses."""

    def __init__(self, db_path: str = "cache.db", ttl_hours: int = 1):
        self.db_path = db_path
        self.ttl = timedelta(hours=ttl_hours)

    async def _init_db(self):
        """Initialize the database schema."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL
                )
            """
            )
            await db.commit()

    def _make_key(self, prefix: str, identifier: str) -> str:
        """Create a cache key from prefix and identifier."""
        return f"{prefix}:{identifier}"

    async def get(self, prefix: str, identifier: str) -> Optional[Any]:
        """Get value from cache if not expired."""
        await self._init_db()
        key = self._make_key(prefix, identifier)

        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT value, expires_at FROM cache WHERE key = ?", (key,)
            )
            row = await cursor.fetchone()

            if not row:
                return None

            value_json, expires_at_str = row
            expires_at = datetime.fromisoformat(expires_at_str)

            # Check if expired
            if datetime.now(timezone.utc) > expires_at:
                # Clean up expired entry
                await db.execute("DELETE FROM cache WHERE key = ?", (key,))
                await db.commit()
                return None

            return json.loads(value_json)

    async def set(self, prefix: str, identifier: str, value: Any) -> None:
        """Store value in cache with TTL."""
        await self._init_db()
        key = self._make_key(prefix, identifier)

        now = datetime.now(timezone.utc)
        expires_at = now + self.ttl

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT OR REPLACE INTO cache (key, value, created_at, expires_at)
                VALUES (?, ?, ?, ?)
            """,
                (key, json.dumps(value), now.isoformat(), expires_at.isoformat()),
            )
            await db.commit()

    async def clear_expired(self) -> None:
        """Remove all expired entries."""
        await self._init_db()

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "DELETE FROM cache WHERE expires_at < ?",
                (datetime.now(timezone.utc).isoformat(),),
            )
            await db.commit()

    async def clear_all(self) -> None:
        """Clear entire cache."""
        await self._init_db()

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM cache")
            await db.commit()
