"""Abstract base class for all scientific experiment types."""
from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ExperimentContext:
    """Mutable context passed through the experiment lifecycle."""
    config: dict[str, Any]
    random_seed: int
    experiment_id: str
    run_id: str
    logs: list[dict[str, Any]] = field(default_factory=list)
    metrics: list[dict[str, Any]] = field(default_factory=list)
    start_time: float = field(default_factory=time.monotonic)
    errors: list[str] = field(default_factory=list)

    def log(self, level: str, message: str, metadata: dict | None = None) -> None:
        entry = {
            "timestamp": time.time(),
            "level": level,
            "message": message,
            "metadata": metadata or {},
        }
        self.logs.append(entry)
        logger.info("[run=%s] %s: %s", self.run_id[:8], level, message)

    def record_metric(self, name: str, value: float, unit: str | None = None, step: int | None = None, extra: dict | None = None) -> None:
        self.metrics.append({
            "name": name,
            "value": value,
            "unit": unit,
            "step": step,
            "extra": extra or {},
        })

    @property
    def duration(self) -> float:
        return time.monotonic() - self.start_time


class BaseExperiment(ABC):
    """All experiment implementations must inherit from this class."""

    type_name: str = ""

    @classmethod
    def get_type_name(cls) -> str:
        return cls.type_name

    @abstractmethod
    def validate_config(self, config: dict[str, Any]) -> list[str]:
        """Return a list of validation error messages. Empty means valid."""
        ...

    @abstractmethod
    def execute(self, ctx: ExperimentContext) -> dict[str, Any]:
        """Run the experiment and return results."""
        ...

    def describe(self) -> dict[str, str]:
        return {"type": self.type_name, "description": getattr(self, "__doc__", "") or ""}
