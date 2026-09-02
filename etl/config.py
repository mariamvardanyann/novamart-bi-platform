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