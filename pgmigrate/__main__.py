import click
from pgmigrate.migrate import apply_migration, apply_all_migrations, initialize_db
from pgmigrate.config import config

@click.group(invoke_without_command=False)
def main():
    pass


@main.command()
@click.argument('version')
def apply(version):
    apply_migration(version)

@main.command()
def apply_all():
    apply_all_migrations()

if __name__ == "__main__":
    from pathlib import Path
    Path(config.migrations_path).mkdir(parents=True, exist_ok=True)
    initialize_db()
    main()
