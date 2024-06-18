import os
import toml
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass
class Config:
    migrations_path: str
    url: str


def __load_config():
    try:
        conf_file = toml.load("pgmigrate.conf")
    except FileNotFoundError:
        conf_file = {}

    migrations_path = Path.cwd() / conf_file.get("migrations_path", "migrations")
    url = conf_file.get("url")

    if not url:
        load_dotenv()
        env_key = conf_file.get("env_key", "DATABASE_URL")
        url = os.environ.get(env_key)

    if not url:
        raise ValueError("Can't find url in pgmigrate.conf or environment variable")

    return Config(migrations_path, url)


config = __load_config()
