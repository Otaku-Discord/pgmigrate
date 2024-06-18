import os
import click
from .migrate import create_migration, apply_migration, apply_all_migrations, initialize_db

@click.group(invoke_without_command=False)
def main():
    pass

@main.command()
@click.argument('name')
def create(name):
    create_migration(name)

@main.command()
@click.argument('version')
def apply(version):
    apply_migration(version)

@main.command()
def apply_all():
    apply_all_migrations()

if __name__ == "__main__":
    from pathlib import Path
    Path("./db/migrations").mkdir(parents=True, exist_ok=True)
    initialize_db()
    main()
