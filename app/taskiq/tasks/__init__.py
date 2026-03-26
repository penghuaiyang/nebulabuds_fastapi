"""
Tasks package.

Each task is defined in its own file for better organization.
All Python files in this directory are automatically imported to register tasks with the broker.
"""
import importlib
import pkgutil
from pathlib import Path

# Automatically import all modules in this package
__all__ = []

# Get the current package path
package_dir = Path(__file__).parent

# Import all Python files in this directory (except __init__.py)
for (_, module_name, _) in pkgutil.iter_modules([str(package_dir)]):
    # Import the module
    module = importlib.import_module(f".{module_name}", package=__name__)
    
    # Add all public attributes (not starting with _) to __all__
    for attr_name in dir(module):
        if not attr_name.startswith("_"):
            attr = getattr(module, attr_name)
            # Only export callable objects (functions/tasks)
            if callable(attr):
                globals()[attr_name] = attr
                __all__.append(attr_name)
