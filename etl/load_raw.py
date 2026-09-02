import os

import pandas as pd

from config import RAW_DIR


def load_csv(filename):
    path = os.path.join(
        RAW_DIR,
        filename,
    )

    return pd.read_csv(path)