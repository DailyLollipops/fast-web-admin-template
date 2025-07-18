import os
import importlib
from .base import BaseFactory

# Get the directory containing this __init__.py
current_dir = os.path.dirname(__file__)

# Discover all .py files in the current directory, excluding __init__.py and base.py
modules = [
    os.path.splitext(filename)[0]
    for filename in os.listdir(current_dir)
    if filename.endswith(".py") and filename != "__init__.py" and filename != "base.py"
]

# Import and expose specific classes or attributes
for module_name in modules:
    module = importlib.import_module(f".{module_name}", package=__name__)
    for attr in dir(module):  # Iterate over attributes in the module
        if not attr.startswith("_"):  # Exclude private attributes
            globals()[attr] = getattr(module, attr)

# Optional: Define __all__ for clarity
__all__ = [attr for attr in globals() if not attr.startswith("_")]
