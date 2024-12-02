import fnmatch
import importlib
import os
from pathlib import Path

from loguru import logger


def load_models_files():
    """Loads all models files so changes are picked up by alembic"""
    start_dir = str(Path(os.path.dirname(__file__)).parent)
    for root, _, filenames in os.walk(start_dir):
        for filename in fnmatch.filter(filenames, "models.py"):
            path = Path(os.path.join(root, filename))
            relative_path = path.relative_to(path.cwd())
            if "app/common" not in str(path):
                dotted_path = str(relative_path).replace("/", ".")[:-3]
                importlib.import_module(dotted_path)
                logger.debug(f"Found models file: {dotted_path}")


load_models_files()
