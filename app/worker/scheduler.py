"""
Taskiq scheduler entry point.

To start the scheduler, run from project root:
    worker scheduler app.worker.scheduler:scheduler

Options:
    --skip-first-run    Skip executing tasks that should have run before startup

Important:
    - Only run ONE scheduler instance to avoid duplicate task executions
    - The scheduler must run as a separate process from your FastAPI app and workers
    - Ensure Redis is running before starting the scheduler
"""
from app.worker.broker import scheduler
# Import tasks to ensure they are registered
import app.worker.tasks  # noqa: F401

if __name__ == "__main__":
    print("Please use: worker scheduler app.worker.scheduler:scheduler")
