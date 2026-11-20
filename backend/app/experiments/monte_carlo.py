"""Monte Carlo Simulation — estimate π using random point sampling."""
from __future__ import annotations

import logging
import math
import time

import numpy as np

from app.experiments.base import BaseExperiment, ExperimentContext

logger = logging.getLogger(__name__)


class MonteCarloSimulation(BaseExperiment):
    """Estimate π by sampling random points in a square and counting those
    that fall inside the inscribed circle.

    Mathematical basis:
        Area of circle = πr²
        Area of square  = (2r)² = 4r²
        Ratio = π/4 ≈ fraction of points inside circle

    Reference result: π (to machine precision for validation)
    """

    type_name = "monte_carlo"

    def validate_config(self, config: dict) -> list[str]:
        errors = []
        params = config.get("parameters", {})
        samples = params.get("num_samples", 100000)
        if not isinstance(samples, int) or samples <= 0:
            errors.append("num_samples must be a positive integer")
        if samples > 10_000_000:
            errors.append("num_samples exceeds maximum of 10,000,000")
        algorithm = params.get("algorithm", "basic")
        if algorithm not in ("basic", "stratified"):
            errors.append("algorithm must be 'basic' or 'stratified'")
        tolerance = params.get("tolerance", 0.01)
        if not isinstance(tolerance, (int, float)) or tolerance <= 0:
            errors.append("tolerance must be positive")
        execution = config.get("execution", {})
        timeout = execution.get("timeout_seconds", 120)
        if timeout <= 0:
            errors.append("timeout_seconds must be positive")
        return errors

    def execute(self, ctx: ExperimentContext) -> dict:
        params = ctx.config.get("parameters", {})
        num_samples = params.get("num_samples", 100000)
        algorithm = params.get("algorithm", "basic")
        target_tolerance = params.get("tolerance", 0.01)

        rng = np.random.default_rng(ctx.random_seed)
        ctx.log("INFO", f"Starting Monte Carlo π estimation: N={num_samples}, algo={algorithm}")

        pi_estimate: float
        convergence_data: list[dict] = []

        if algorithm == "basic":
            pi_estimate, convergence_data = self._basic_mc(rng, num_samples, ctx)
        else:
            pi_estimate, convergence_data = self._stratified_mc(rng, num_samples, ctx)

        # Statistical measures
        abs_error = abs(pi_estimate - math.pi)
        rel_error = abs_error / math.pi
        se = 4 * math.sqrt(1 / num_samples)  # standard error approximation
        ci_95_lower = pi_estimate - 1.96 * se
        ci_95_upper = pi_estimate + 1.96 * se

        ctx.log("INFO", f"π estimate = {pi_estimate:.8f} (true = {math.pi:.8f}), abs_error = {abs_error:.8f}")
        ctx.log("INFO", f"95% CI: [{ci_95_lower:.8f}, {ci_95_upper:.8f}]")

        results = {
            "estimated_pi": pi_estimate,
            "true_pi": math.pi,
            "absolute_error": abs_error,
            "relative_error": rel_error,
            "standard_error": se,
            "confidence_interval_95": [float(ci_95_lower), float(ci_95_upper)],
            "algorithm": algorithm,
            "num_samples": num_samples,
            "convergence": convergence_data[-10:] if len(convergence_data) > 10 else convergence_data,
            "within_tolerance": abs_error < target_tolerance,
        }
        ctx.record_metric("pi_estimate", pi_estimate, unit="")
        ctx.record_metric("pi_absolute_error", abs_error, unit="")
        ctx.record_metric("pi_relative_error", rel_error, unit="")
        ctx.record_metric("ci_lower_95", ci_95_lower, unit="")
        ctx.record_metric("ci_upper_95", ci_95_upper, unit="")
        ctx.record_metric("standard_error", se, unit="")
        return results

    def _basic_mc(self, rng: np.Generator, n: int, ctx: ExperimentContext) -> tuple[float, list[dict]]:
        n_rounds = max(1, n // 1000)
        batch = 1000
        inside = 0
        total = 0
        convergence = []
        start = time.perf_counter()

        for i in range(n_rounds):
            x = rng.uniform(-1, 1, size=batch)
            y = rng.uniform(-1, 1, size=batch)
            hits = np.sum(x * x + y * y <= 1.0)
            inside += int(hits)
            total += batch
            est = 4.0 * inside / total
            convergence.append({"sample_count": total, "pi_estimate": float(est)})
            if (i + 1) % 10 == 0:
                ctx.log("INFO", f"  Progress: {total}/{n} samples, π≈{est:.6f}")

        duration = time.perf_counter() - start
        ctx.record_metric("mc_duration_seconds", duration, unit="s")
        ctx.record_metric("mc_total_samples", total, unit="count")
        return 4.0 * inside / total, convergence

    def _stratified_mc(self, rng: np.Generator, n: int, ctx: ExperimentContext) -> tuple[float, list[dict]]:
        """Stratified sampling: divide square into sub-regions for lower variance."""
        n_strata = int(math.ceil(math.sqrt(n / 100)))
        stratum_size = 100
        n_total = n_strata * stratum_size
        inside = 0
        convergence = []
        start = time.perf_counter()

        x = rng.uniform(-1, 1, size=(n_strata, stratum_size))
        y = rng.uniform(-1, 1, size=(n_strata, stratum_size))
        hits = np.sum(x * x + y * y <= 1.0, axis=1)
        running_inside = int(np.cumsum(hits)[-1])
        running_total = n_total
        est = 4.0 * running_inside / running_total
        convergence.append({"sample_count": running_total, "pi_estimate": float(est)})

        duration = time.perf_counter() - start
        ctx.record_metric("mc_duration_seconds", duration, unit="s")
        ctx.record_metric("mc_total_samples", running_total, unit="count")
        ctx.log("INFO", f"Stratified MC: π≈{est:.8f} with {running_total} samples")
        return 4.0 * running_inside / running_total, convergence
