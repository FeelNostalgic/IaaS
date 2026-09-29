"""Centralized application configuration.

All environment-specific values are resolved here, at import time, so that no
credential, account identifier or infrastructure name is ever hardcoded in the
rest of the codebase.

Values are read from the process environment. As a convenience for local
development, a ``.env`` file sitting next to ``app.py`` is loaded first and only
fills in variables that are not already exported, so real environment variables
always take precedence over the file.

Required variables (the app refuses to start without them):

    AWS_KMS_KEY_ID    Key ID of an asymmetric KMS key used to generate user
                      key pairs and to unwrap their encrypted private keys.
    S3_BUCKET_NAME    Name of the S3 bucket that stores every user's objects.
                      S3 bucket names are globally unique across all AWS
                      accounts, so this cannot have a sensible default.

Copy ``.env.example`` to ``.env`` to get started.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"


def _load_env_file(path: Path) -> None:
    """Populate ``os.environ`` from a ``.env`` file, without overriding it.

    Supports ``KEY=value`` lines, ``#`` comments, blank lines and optional
    single or double quotes around the value. This intentionally avoids a third
    party dependency for a feature that needs only a handful of scalars.

    :param path: Absolute path of the ``.env`` file to read.
    """
    if not path.is_file():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        key, _, value = line.partition("=")
        key = key.strip()

        if not key or key in os.environ:
            continue

        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]

        os.environ[key] = value


def _required(name: str) -> str:
    """Return an environment variable, failing fast when it is missing.

    :param name: Variable name to read.
    :return: The variable value.
    :raises RuntimeError: If the variable is unset or empty.
    """
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(
            f"Missing required environment variable '{name}'. "
            f"Copy .env.example to .env and set it there, or export it in your shell."
        )
    return value


def _optional(name: str, default: str) -> str:
    """Return an environment variable, falling back to a default.

    :param name: Variable name to read.
    :param default: Value used when the variable is unset or empty.
    :return: The variable value or the default.
    """
    value = os.environ.get(name, "").strip()
    return value or default


_load_env_file(ENV_FILE)

# --- AWS -------------------------------------------------------------------

AWS_REGION = _optional("AWS_REGION", "eu-central-1")
AWS_KMS_KEY_ID = _required("AWS_KMS_KEY_ID")

# Credentials are intentionally not read here. boto3 resolves them through its
# own provider chain: environment variables, ~/.aws/credentials, ~/.aws/config,
# container/instance metadata or an IAM role. That keeps secrets out of this
# repository entirely.

# --- S3 --------------------------------------------------------------------

# S3 bucket names must be lowercase, so normalize once here instead of relying
# on every call site to remember it.
S3_BUCKET_NAME = _required("S3_BUCKET_NAME").lower()

# --- MySQL -----------------------------------------------------------------

DB_HOST = _optional("DB_HOST", "127.0.0.1")
DB_PORT = int(_optional("DB_PORT", "3306"))
DB_USER = _optional("DB_USER", "root")
DB_PASSWORD = _optional("DB_PASSWORD", "")
DB_NAME = _optional("DB_NAME", "iaas")

# Shape expected by mysql.connector.connect(**config)
DB_CONFIG = {
    "host": DB_HOST,
    "port": DB_PORT,
    "user": DB_USER,
    "password": DB_PASSWORD,
    "database": DB_NAME,
}
