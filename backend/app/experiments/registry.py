"""Registry pattern for discovering and managing experiment types."""
from __future__ import annotations

from typing import Type

from app.experiments.base import BaseExperiment


_registry: dict[str, Type[BaseExperiment]] = {}


def register_experimentaliment_class(experiment_cls: Type[BaseExperiment]) -> None:
    name = experiment_cls.get_type_name()
    _registry[name] = experiment_cls


def get_experiment_class(type_name: str) -> Type[BaseExperiment]:
    cls = _registry.get(type_name)
    if cls is None:
        raise KeyError(f"Unknown experiment type: {type_name!r}. Available: {sorted(_registry)}")
    return cls


def list_experiment_types() -> list[str]:
    return sorted(_registry.keys())


# Import all experiment modules to trigger registration at startup
from app.experiments.numerical_integration import NumericalIntegrationBenchmark  # noqa: E402
from app.experiments.monte_carlo import MonteCarloSimulation  # noqa: E402
from app.experiments.parameter_sweep import ParameterSweepExperiment  # noqa: E402

# Register all experiment types
register_experimentaliment_class(NumericalIntegrationBenchmark)
register_experimentaliment_class(MonteCarloSimulation)
register_experimentaliment_class(ParameterSweepExperiment)
