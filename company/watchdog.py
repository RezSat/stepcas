from __future__ import annotations

import json
import os
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TASK_FILE = ROOT / "company" / "tasks.json"
LOG_DIR = ROOT / "company" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
ATTACH_URL = os.environ.get("STEPCAS_OPENCODE_ATTACH", "http://localhost:4027")
POLL_SECONDS = int(os.environ.get("STEPCAS_COMPANY_POLL_SECONDS", "5"))

PLANNER_TASKS = [
    {
        "id": "PM-AUTO",
        "title": "Maintain backlog health automatically",
        "agent": "project-manager",
        "command": (
            "Read TASK.md, AGENTS.md, program.md, docs, source, tests, "
            "recent completed tasks, and current backlog. If backlog is low, empty, "
            "too repetitive, or missing strategic coverage, add a balanced set of small "
            "implementation, bugfix, test, docs, cleanup, and architecture tasks using "
            ".\\scripts\\add-task.ps1. Never manually edit company/tasks.json."
        ),
        "priority": 1,
        "branch": "chore/backlog-health-auto",
    },
    {
        "id": "ARCH-AUTO",
        "title": "Review architecture and add strategic tasks automatically",
        "agent": "chief-architect",
        "command": (
            "Inspect the full StepCAS repository, architecture docs, roadmap, source, "
            "tests, and recent progress. Identify missing capabilities, fragile design, "
            "neglected subsystems, and strategic next steps. Add small actionable tasks "
            "using .\\scripts\\add-task.ps1. Never manually edit company/tasks.json."
        ),
        "priority": 2,
        "branch": "chore/architecture-review-auto",
    },
]

@dataclass
class Task:
    id: str
    title: str
    agent: str
    command: str
    status: str
    priority: int = 100
    branch: str | None = None
    notes: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Task":
        return cls(**data)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "agent": self.agent,
            "command": self.command,
            "status": self.status,
            "priority": self.priority,
            "branch": self.branch,
            "notes": self.notes,
        }


def load_tasks() -> list[Task]:
    items = json.loads(TASK_FILE.read_text(encoding="utf-8"))
    return [Task.from_dict(item) for item in items]


def save_tasks(tasks: list[Task]) -> None:
    TASK_FILE.write_text(
        json.dumps([task.to_dict() for task in tasks], indent=2) + "\n",
        encoding="utf-8",
    )


def pick_next(tasks: list[Task]) -> Task | None:
    queued = [task for task in tasks if task.status == "queued"]
    if not queued:
        return None
    queued.sort(key=lambda t: (t.priority, t.id))
    return queued[0]


def add_task(task):
    cmd = [
        "powershell",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(ROOT / "scripts" / "add-task.ps1"),
        "-Id",
        task["id"],
        "-Title",
        task["title"],
        "-Agent",
        task["agent"],
        "-Command",
        task["command"],
        "-Priority",
        str(task["priority"]),
        "-Branch",
        task["branch"],
    ]
    result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)

def main() -> int:
    print("StepCAS - Watchdog is watching the task list...")
    print(f"Attach URL: {ATTACH_URL}")
    print(f"Task file: {TASK_FILE}")
    while True:
        tasks = load_tasks()
        active = [t for t in tasks if t.status == "running"]
        if active:
            print("A task is already marked running. Waiting.")
            time.sleep(POLL_SECONDS)
            continue
        task = pick_next(tasks)
        if task is None:
            print("No queued tasks. Adding Planner Tasks.")
            for task in PLANNER_TASKS:
                add_task(task)
        time.sleep(1)


if __name__ == "__main__":
    raise SystemExit(main())
