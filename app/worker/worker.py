"""
Taskiq worker entry point.

To start a worker, run from project root:
    worker worker app.worker.worker:broker

For multiple workers:
    worker worker app.worker.worker:broker --workers 4

For development with auto-reload:
    worker worker app.worker.worker:broker --reload
"""
from app.worker.broker import broker
# Import tasks to ensure they are registered
import app.worker.tasks  # noqa: F401

if __name__ == "__main__":
    print("Please use: worker worker app.worker.worker:broker")