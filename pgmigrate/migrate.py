import os
import psycopg2
from dotenv import load_dotenv
import click

load_dotenv()
DB_URL = os.getenv('DATABASE_URL')

def get_db_connection():
    conn = psycopg2.connect(DB_URL)
    return conn

def initialize_db():
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS migrations (
                id SERIAL PRIMARY KEY,
                version VARCHAR(255) NOT NULL UNIQUE,
                name VARCHAR(255) NOT NULL,
                applied_at TIMESTAMP
            )
        """)
        conn.commit()
    conn.close()



def create_migration(name):
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT COALESCE(MAX(CAST(SUBSTR(version, 2) AS INTEGER)), 0) FROM migrations")
        last_version = cur.fetchone()[0]
        new_version = f"v{last_version + 1}"
        
    migration_filename = f'db/migrations/{new_version}_{name}.sql'
    
    with open(migration_filename, 'w') as f:
        f.write("-- Write your SQL migration script here\n")
    
    click.echo(f"Created migration: {migration_filename}")
    
    with conn.cursor() as cur:
        cur.execute("INSERT INTO migrations (version, name) VALUES (%s, %s)", (new_version, name))
        conn.commit()
    conn.close()

def get_applied_migrations():
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT version FROM migrations WHERE applied_at IS NOT NULL")
        applied_migrations = {row[0] for row in cur.fetchall()}
    conn.close()
    return applied_migrations

def apply_migration(version):
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT name FROM migrations WHERE version = %s", (version,))
        result = cur.fetchone()
        if not result:
            click.echo(f"Migration version {version} does not exist.")
            conn.close()
            return
        
        migration_name = result[0]
        migration_filename = f'db/migrations/{version}_{migration_name}.sql'
        
        if not os.path.exists(migration_filename):
            click.echo(f"Migration file {migration_filename} does not exist.")
            conn.close()
            return
        
        with open(migration_filename, 'r') as f:
            sql = f.read()
            cur.execute(sql)
            cur.execute("UPDATE migrations SET applied_at = CURRENT_TIMESTAMP WHERE version = %s", (version,))
            conn.commit()
    conn.close()
    click.echo(f"Applied migration: {version}")

def apply_all_migrations():
    applied_migrations = get_applied_migrations()
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT version, name FROM migrations ORDER BY version")
        all_migrations = cur.fetchall()
    
    unapplied_migrations = [(version, name) for version, name in all_migrations if version not in applied_migrations]
    
    for version, name in unapplied_migrations:
        apply_migration(version)
    
    conn.close()

