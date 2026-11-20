"""Parameter Sweep Experiment — systematic exploration of parameter space."""
from __future__ import annotations

import logging
import time

import numpy as np

from app.experiments.base import BaseExperiment, ExperimentContext

logger = logging.getLogger(__name__)


class ParameterSweepExperiment(BaseExperiment):
    """Explore a configurable objective function across a grid of parameters.

    The experiment evaluates f(p₁, p₂, ...) for each combination and records
    the output, enabling sensitivity and response-surface analysis.
    """

    type_name = "parameter_sweep"

    MAX_COMBINATIONS = 10_000

    def validate_config(self, config: dict) -> list[str]:
        errors = []
        params = config.get("parameters", {})
        func_name = params.get("function", "quadratic")
        valid_funcs = {"quadratic", "rastrigin", "ackley", "sphere", "custom_expression"}
        if func_name not in valid_funcs:
            errors.append(f"function must be one of {sorted(valid_funcs)}")

        param_defs = params.get("parametric_definitions", [])
        if not param_defs:
            errors.append("At least one parameter definition is required")
        else:
            total = 1
            for pd in param_defs:
                name = pd.get("name", "")
                if not name:
                    errors.append("Each parameter must have a name")
                lo = pd.get("lower", 0.0)
                hi = pd.get("upper", 1.0)
                steps = pd.get("steps", 10)
                if not isinstance(steps, int) or steps < 1:
                    errors.append(f"Parameter '{name}': steps must be a positive integer")
                if not isinstance(lo, (int, float)) or not isinstance(hi, (int, float)):
                    errors.append(f"Parameter '{name}': lower/upper must be numeric")
                if lo >= hi:
                    errors.append(f"Parameter '{name}': lower must be < upper")
                if steps > 100:
                    errors.append(f"Parameter '{name}': steps must be <= 100")
                total *= steps
            if total > self.MAX_COMBINATIONS:
                errors.append(f"Total combinations ({total}) exceed limit of {self.MAX_COMBINATIONS}")

        execution = config.get("execution", {})
        timeout = execution.get("timeout_seconds", 300)
        if timeout <= 0:
            errors.append("timeout_seconds must be positive")
        return errors

    def execute(self, ctx: ExperimentContext) -> dict:
        params = ctx.config.get("parameters", {})
        func_name = params.get("function", "quadratic")
        param_defs = params.get("parametric_definitions", [])
        parallel = params.get("parallel", False)

        ctx.log("INFO", f"Starting parameter sweep: function={func_name}, params={len(param_defs)}")

        # Generate grid
        ranges = []
        for pd in param_defs:
            lo = float(pd["lower"])
            hi = float(pd["upper"])
            n = int(pd["steps"])
            ranges.append(np.linspace(lo, hi, n))

        names = [pd["name"] for pd in param_defs]
        grids = np.meshgrid(*ranges, indexing="ij")
        flat_grids = [g.flatten() for g in grids]
        combos = list(zip(*flat_grids))

        ctx.log("INFO", f"Total combinations: {len(combos)}")
        ctx.record_metric("sweep_num_combinations", len(combos), unit="count")
        ctx.record_metric("sweep_num_parameters", len(param_defs), unit="count")

        # Evaluate
        results = []
        start = time.perf_counter()
        for idx, point in enumerate(combos):
            val = self._evaluate(func_name, point, names)
            results.append({"parameters": dict(zip(names, point)), "value": float(val)})
            if (idx + 1) % 100 == 0 or idx == len(combos) - 1:
                ctx.log("INFO", f"  Progress: {idx + 1}/{len(combos)}")
                ctx.record_metric("sweep_progress", (idx + 1) / len(combos) * 100, unit="%", step=idx)

        duration = time.perf_counter() - start
        values = [r["value"] for r in results]
        best = min(results, key=lambda r: r["value"])
        worst = max(results, key=lambda r: r["value"])

        ctx.log("INFO", f"Sweep completed: best={best['value']:.6e}, worst={worst['value']:.6e}, dur={duration:.3f}s")
        ctx.record_metric("sweep_best_value", best["value"], unit="")
        ctx.record_metric("sweep_worst_value", worst["value"], unit="")
        ctx.record_metric("sweep_duration_seconds", duration, unit="s")
        ctx.record_metric("sweep_mean", float(np.mean(values)), unit="")
        ctx.record_metric("sweep_std", float(np.std(values)), unit="")

        return {
            "function": func_name,
            "parameters": param_defs,
            "total_combinations": len(combos),
            "duration_seconds": duration,
            "best": best,
            "worst": worst,
            "statistics": {
                "mean": float(np.mean(values)),
                "std": float(np.std(values)),
                "min": float(np.min(values)),
                "max": float(np.max(values)),
            },
            "results_sample": results[:100],
        }

    @staticmethod
    def _evaluate(func_name: str, point: tuple, names: list[str]) -> float:
        """Evaluate the objective function at the given parameter point."""
        args = {n: float(v) for n, v in zip(names, point)}
        if func_name == "quadratic":
            return sum(v ** 2 for v in args.values())
        elif func_name == "sphere":
            return sum(v ** 2 for v in args.values())
        elif func_name == "rastrigin":
            A = 10
            return A * len(args) + sum(v ** 2 - A * np.cos(2 * np.pi * v) for v in args.values())
        elif func_name == "ackley":
            n = len(args)
            first = -20 * np.exp(-0.2 * np.sqrt(0.5 * sum(v ** 2 for v in args.values())))
            second = -np.exp(0.5 * sum(np.cos(2 * np.pi * v) for v in args.values()))
            return first + second + 20 + np.e
        raise ValueError(f"Unknown function: {func_name}")
