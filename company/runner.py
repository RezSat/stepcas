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


def run_task(task: Task) -> int:
    log_path = LOG_DIR / f"{task.id}.log"
    title = f"{task.id} {task.title}"

    raw_cmd = [
        "opencode",
        "run",
        "--attach",
        ATTACH_URL,
        "--agent",
        task.agent,
        "--title",
        title,
        task.command,
    ]

    # Run through cmd because manual cmd execution works on your machine
    cmd = ["cmd", "/c", *raw_cmd]

    with log_path.open("a", encoding="utf-8", errors="replace") as log_file:
        start_line = f"\n\n===== START {time.ctime()} =====\n"
        command_line = "COMMAND: " + " ".join(cmd) + "\n"

        print(start_line, end="")
        print(command_line, end="")

        log_file.write(start_line)
        log_file.write(command_line)
        log_file.flush()

        env = os.environ.copy()
        env["CI"] = "1"
        env["TERM"] = "dumb"
        env["NO_COLOR"] = "1"

        proc = subprocess.Popen(
            cmd,
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=False,
            bufsize=1,
            env=env,
        )

        assert proc.stdout is not None

        for line in proc.stdout:
            print(line, end="")
            log_file.write(line)
            log_file.flush()

        proc.wait()

        end_line = f"===== END exit={proc.returncode} {time.ctime()} =====\n"
        print(end_line, end="")
        log_file.write(end_line)
        log_file.flush()

        return proc.returncode
    
def main() -> int:
    print("StepCAS company runner started")
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
            print("No queued tasks. Sleeping.")
            time.sleep(POLL_SECONDS)
            continue
        print(f"Dispatching {task.id}: {task.title}")
        for item in tasks:
            if item.id == task.id:
                item.status = "running"
        save_tasks(tasks)
        code = run_task(task)
        tasks = load_tasks()
        for item in tasks:
            if item.id == task.id:
                item.status = "done" if code == 0 else "failed"
        save_tasks(tasks)
        print(f"Finished {task.id} with exit code {code}")
        time.sleep(1)


if __name__ == "__main__":
    raise SystemExit(main())
