import psycopg2
import psycopg2.pool
import psycopg2.extras
import os
from contextlib import contextmanager

_pool = None


def get_pool():
    global _pool
    if _pool is None:
        db_url = os.environ.get('DATABASE_URL')
        if not db_url:
            raise RuntimeError('DATABASE_URL environment variable not set')
        _pool = psycopg2.pool.SimpleConnectionPool(1, 10, db_url)
    return _pool


@contextmanager
def get_connection():
    pool = get_pool()
    conn = pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        pool.putconn(conn)


def query_one(sql, params=None):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            row = cur.fetchone()
            return dict(row) if row else None


def query_all(sql, params=None):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
            return [dict(r) for r in rows]


def execute(sql, params=None):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.rowcount


def execute_returning(sql, params=None):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            row = cur.fetchone()
            return row[0] if row else None


def ensure_schema():
    """Run on startup to add any missing columns gracefully."""
    migrations = [
        # Users
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS display_name TEXT",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS position TEXT",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS work_phone TEXT",
        # Components
        "ALTER TABLE components ADD COLUMN IF NOT EXISTS company_id INTEGER DEFAULT 1",
        "ALTER TABLE components ADD COLUMN IF NOT EXISTS company_assignment TEXT DEFAULT 'Both'",
        # Finished products — net weight
        "ALTER TABLE finished_products ADD COLUMN IF NOT EXISTS net_weight_grams FLOAT",
        "ALTER TABLE finished_products ADD COLUMN IF NOT EXISTS net_weight_unit TEXT DEFAULT 'g'",
        # Finished products — explosion / circular ref
        "ALTER TABLE finished_products ADD COLUMN IF NOT EXISTS has_circular_ref BOOLEAN DEFAULT FALSE",
        "ALTER TABLE finished_products ADD COLUMN IF NOT EXISTS circular_ref_detail TEXT",
        # Explosion cache
        """CREATE TABLE IF NOT EXISTS finished_product_explosion_cache (
            finished_product_id INTEGER PRIMARY KEY
                REFERENCES finished_products(id) ON DELETE CASCADE,
            explosion_data JSONB,
            allergen_summary JSONB,
            calculated_at TIMESTAMPTZ DEFAULT NOW()
        )""",
        # FP-specific allergen overrides (separate from component_allergens to avoid FK clash)
        """CREATE TABLE IF NOT EXISTS finished_product_allergens (
            id SERIAL PRIMARY KEY,
            finished_product_id INTEGER
                REFERENCES finished_products(id) ON DELETE CASCADE,
            allergen_name TEXT NOT NULL,
            manual_status TEXT,
            notes TEXT,
            UNIQUE(finished_product_id, allergen_name)
        )""",
    ]
    for sql in migrations:
        try:
            execute(sql)
        except Exception:
            pass
