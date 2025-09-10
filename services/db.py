import os
import ssl
from contextlib import contextmanager
from typing import Iterator, Optional

import psycopg2
import psycopg2.extras


def _build_conn_kwargs_from_env() -> dict:
    database_url: Optional[str] = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set in environment")
    # psycopg2 can take the full DSN string
    return {"dsn": database_url}


@contextmanager
def get_connection() -> Iterator[psycopg2.extensions.connection]:
    kwargs = _build_conn_kwargs_from_env()
    conn = psycopg2.connect(**kwargs)
    try:
        yield conn
    finally:
        conn.close()


@contextmanager
def get_cursor(commit: bool = True) -> Iterator[psycopg2.extras.RealDictCursor]:
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            try:
                yield cur
                if commit:
                    conn.commit()
            except Exception:
                conn.rollback()
                raise


def fetch_one(query: str, params: tuple | dict | None = None):
    with get_cursor(commit=False) as cur:
        cur.execute(query, params or ())
        return cur.fetchone()


def fetch_one_commit(query: str, params: tuple | dict | None = None):
    with get_cursor(commit=True) as cur:
        cur.execute(query, params or ())
        return cur.fetchone()


def fetch_all(query: str, params: tuple | dict | None = None):
    with get_cursor(commit=False) as cur:
        cur.execute(query, params or ())
        return cur.fetchall()


def execute(query: str, params: tuple | dict | None = None) -> None:
    with get_cursor(commit=True) as cur:
        cur.execute(query, params or ())


def execute_many(query: str, seq_of_params: list[tuple] | list[dict]) -> None:
    with get_cursor(commit=True) as cur:
        psycopg2.extras.execute_batch(cur, query, seq_of_params)

