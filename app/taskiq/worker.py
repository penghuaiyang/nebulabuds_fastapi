"""
Taskiq worker entry point.

To start a worker, run from project root:
    taskiq worker app.taskiq.worker:broker

For multiple workers:
    taskiq worker app.taskiq.worker:broker --workers 4

For development with auto-reload:
    taskiq worker app.taskiq.worker:broker --reload
"""
from app.taskiq.broker import broker
# Import tasks to ensure they are registered
import app.taskiq.tasks  # noqa: F401

if __name__ == "__main__":
    print("Please use: taskiq worker app.taskiq.worker:broker")