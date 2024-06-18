from operator import itemgetter
import os
import psycopg2
from dotenv import load_dotenv
import click
from pgmigrate.config import config

load_dotenv()


def get_all_migrations():
    files = os.listdir(config.migrations_path)
    return sorted(
        (
            (
                int(f.split("__")[0][1:]),
                f,
            )
            for f in files
        ), key=itemgetter(0)
    )


def get_db_connection():
    conn = psycopg2.connect(config.url)
    return conn


def initialize_db():
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS migrations (
                id SERIAL PRIMARY KEY,
                version INT NOT NULL UNIQUE,
                applied_at TIMESTAMP
            )
        """
        )
        conn.commit()
    conn.close()


def get_applied_migrations():
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT version FROM migrations;")
        applied_migrations = {row[0] for row in cur.fetchall()}
    conn.close()
    return applied_migrations


def get_migration_from_version(version):
    migrations = get_all_migrations()
    for migration in migrations:
        if migration[0] == version:
            return migration

    return None


def apply_migration(version):
    conn = get_db_connection()
    migration = get_migration_from_version(version)

    if not migration:
        click.echo(f"Migration version {version} does not exist.")
        conn.close()
        return

    with conn.cursor() as cur:
        migration_filename = config.migrations_path / migration[1]

        if not os.path.exists(migration_filename):
            click.echo(f"Migration file {migration_filename} does not exist.")
            conn.close()
            return

        with open(migration_filename, "r") as f:
            sql = f.read()
            cur.execute(sql)
            cur.execute(
                """
                INSERT INTO migrations (version, applied_at) 
                VALUES (%s, CURRENT_TIMESTAMP) 
                ON CONFLICT (version) 
                DO UPDATE 
                SET applied_at = CURRENT_TIMESTAMP;""",
                (version,),
            )
            conn.commit()
    conn.close()
    click.echo(f"Applied migration: {version}")


def apply_all_migrations():
    all_migrations = get_all_migrations()
    applied_migrations = get_applied_migrations()

    unapplied_migrations = [
        (version, name)
        for version, name in all_migrations
        if version not in applied_migrations
    ]

    for version, name in unapplied_migrations:
        apply_migration(version)
