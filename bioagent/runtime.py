"""Small explicit runtime: budget, registry, paths, events and DAG validation."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable
import inspect
import json


class BudgetExceeded(RuntimeError):
    pass


@dataclass
class Budget:
    limit: int = 30
    used: int = 0

    def __post_init__(self):
        if type(self.limit) is not int or type(self.used) is not int or not 0 <= self.used <= self.limit:
            raise ValueError("Invalid integer budget")

    def consume(self, units: int = 1):
        if type(units) is not int or units < 0:
            raise ValueError("Invalid budget units")
        if self.used + units > self.limit:
            raise BudgetExceeded("Action budget exhausted")
        self.used += units


@dataclass(frozen=True)
class Tool:
    name: str
    handler: Callable
    validator: Callable[[dict], None]
    approval_required: bool = False


class ToolRegistry:
    def __init__(self):
        self.tools: dict[str, Tool] = {}

    def register(self, tool: Tool):
        if not tool.name or tool.name in self.tools:
            raise ValueError("Missing or duplicate tool name")
        if not callable(tool.handler) or not callable(tool.validator):
            raise ValueError("Tool requires handler and validator")
        self.tools[tool.name] = tool

    def call(self, name: str, arguments: dict, *, budget: Budget, approved=False):
        if name not in self.tools:
            raise ValueError("Unknown tool")
        if not isinstance(arguments, dict):
            raise ValueError("Arguments must be a dictionary")
        tool = self.tools[name]
        inspect.signature(tool.handler).bind(**arguments)
        tool.validator(arguments)
        if tool.approval_required and approved is not True:
            raise PermissionError("Explicit approval required")
        budget.consume()
        return tool.handler(**arguments)


def safe_path(root: Path, relative: str) -> Path:
    root = root.resolve()
    path = (root / relative).resolve()
    if path != root and root not in path.parents:
        raise PermissionError("Path escapes workspace")
    return path


class EventLog:
    """Single-process append-only JSONL; do not put secrets in event fields."""
    def __init__(self, path: Path):
        self.path = Path(path)
        self.sequence = 0

    def write(self, action: str, **fields):
        self.sequence += 1
        row = {"sequence": self.sequence,
               "time": datetime.now(timezone.utc).isoformat(),
               "action": action, "details": fields}
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")


def topological_order(dependencies: dict[str, set[str]]) -> list[str]:
    known = set(dependencies)
    if any(not parents <= known for parents in dependencies.values()):
        raise ValueError("Unknown dependency")
    done = set()
    order = []
    while len(done) < len(known):
        ready = sorted(k for k, parents in dependencies.items() if k not in done and parents <= done)
        if not ready:
            raise ValueError("Dependency cycle")
        order.extend(ready)
        done.update(ready)
    return order
