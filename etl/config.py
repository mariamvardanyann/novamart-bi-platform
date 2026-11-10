import os


PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
    )
)

RAW_DIR = os.path.join(
    PROJECT_ROOT,
    "data",
    "raw",
)

PROCESSED_DIR = os.path.join(
    PROJECT_ROOT,
    "data",
    "processed",
)

QUARANTINE_DIR = os.path.join(
    PROJECT_ROOT,
    "data",
    "quarantine",
)

# SQL Server connection settings are configurable so the repository does not
# expose or depend on one developer machine name.
SQL_SERVER = os.getenv(
    "NOVAMART_SQL_SERVER",
    r"localhost\SQLEXPRESS",
)
SQL_DATABASE = os.getenv(
    "NOVAMART_SQL_DATABASE",
    "novamart",
)
