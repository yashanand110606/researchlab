"""Tests for scientific correctness of experiments."""
from __future__ import annotations

import math

import numpy as np
import pytest

from app.experiments.numerical_integration import NumericalIntegrationBenchmark
from app.experiments.monte_carlo import MonteCarloSimulation
from app.experiments.parameter_sweep import ParameterSweepExperiment
from app.experiments.base import ExperimentContext


def _ctx(config: dict, seed: int = 42, run_id: str = "test-run") -> ExperimentContext:
    return ExperimentContext(config=config, random_seed=seed, experiment_id="exp-1", run_id=run_id)


# ── Numerical Integration ─────────────────────────────────────────

class TestNumericalIntegration:
    def test_validate_valid_config(self):
        cfg = {
            "experiment": {
                "type": "numerical_integration",
                "parameters": {"equation": "exponential_decay", "initial_value": 1.0,
                               "decay_constant": 0.5, "time_start": 0.0, "time_end": 10.0, "step_size": 0.1},
                "execution": {"timeout_seconds": 120, "max_iterations": 100000},
            }
        }
        assert NumericalIntegrationBenchmark().validate_config(cfg["experiment"]) == []

    def test_validate_rejects_bad_equation(self):
        cfg = {"experiment": {"type": "numerical_integration", "parameters": {"equation": "unknown"}, "execution": {}}}
        errs = NumericalIntegrationBenchmark().validate_config(cfg["experiment"])
        assert any("equation" in e.lower() for e in errs)

    def test_validate_rejects_negative_decay(self):
        cfg = {"experiment": {"type": "numerical_integration", "parameters": {"decay_constant": -1.0}, "execution": {}}}
        errs = NumericalIntegrationBenchmark().validate_config(cfg["experiment"])
        assert any("decay" in e.lower() for e in errs)

    @pytest.mark.slow
    def test_exponential_decay_accuracy(self):
        """RK4 and SciPy should both be more accurate than Euler for y'=-0.5y."""
        cfg = {
            "type": "numerical_integration",
            "parameters": {"equation": "exponential_decay", "initial_value": 1.0,
                           "decay_constant": 0.5, "time_start": 0.0, "time_end": 10.0, "step_size": 0.01},
            "execution": {"timeout_seconds": 60},
        }
        results = NumericalIntegrationBenchmark().execute(_ctx(cfg))
        euler_err = results["euler"]["max_abs_error"]
        rk4_err = results["rk4"]["max_abs_error"]
        scipy_err = results["scipy_rk45"]["max_abs_error"]
        assert rk4_err < euler_err, "RK4 must beat Euler"
        assert scipy_err < euler_err, "SciPy RK45 must beat Euler"
        assert scipy_err < 1e-6, "SciPy should be very accurate"

    def test_reproducibility(self):
        cfg = {
            "type": "numerical_integration",
            "parameters": {"equation": "exponential_decay", "initial_value": 1.0,
                           "decay_constant": 0.5, "time_start": 0.0, "time_end": 5.0, "step_size": 0.1},
            "execution": {"timeout_seconds": 30},
        }
        r1 = NumericalIntegrationBenchmark().execute(_ctx(cfg, seed=123))
        r2 = NumericalIntegrationBenchmark().execute(_ctx(cfg, seed=123))
        assert r1["euler"]["max_abs_error"] == r2["euler"]["max_abs_error"]
        assert r1["rk4"]["max_abs_error"] == r2["rk4"]["max_abs_error"]


# ── Monte Carlo ────────────────────────────────────────────────────

class TestMonteCarlo:
    def test_estimate_pi_close(self):
        cfg = {
            "type": "monte_carlo",
            "parameters": {"num_samples": 50000, "algorithm": "basic", "tolerance": 0.05},
            "execution": {"timeout_seconds": 60},
        }
        results = MonteCarloSimulation().execute(_ctx(cfg))
        assert abs(results["estimated_pi"] - math.pi) < 0.05, "PI estimate should be within 0.05"
        assert results["num_samples"] == 50000

    def test_reproducibility(self):
        cfg = {
            "type": "monte_carlo",
            "parameters": {"num_samples": 10000, "algorithm": "basic", "tolerance": 0.1},
            "execution": {"timeout_seconds": 30},
        }
        r1 = MonteCarloSimulation().execute(_ctx(cfg, seed=99))
        r2 = MonteCarloSimulation().execute(_ctx(cfg, seed=99))
        assert r1["estimated_pi"] == r2["estimated_pi"]

    def test_stratified_vs_basic(self):
        """Stratified sampling should generally have lower variance."""
        cfg_common = {
            "type": "monte_carlo",
            "parameters": {"num_samples": 20000, "tolerance": 0.1},
            "execution": {"timeout_seconds": 60},
        }
        basic = MonteCarloSimulation().execute(_ctx(cfg_common | {"parameters": {**cfg_common["parameters"], "algorithm": "basic"}}, seed=1))
        strat = MonteCarloSimulation().execute(_ctx(cfg_common | {"parameters": {**cfg_common["parameters"], "algorithm": "stratified"}}, seed=1))
        # Both should be reasonably close; check convergence data exists
        assert len(basic["convergence"]) > 0
        assert len(strat["convergence"]) > 0


# ── Parameter Sweep ────────────────────────────────────────────────

class TestParameterSweep:
    def test_quadratic_minimum_at_origin(self):
        cfg = {
            "type": "parameter_sweep",
            "parameters": {
                "function": "quadratic",
                "parametric_definitions": [
                    {"name": "x", "lower": -5.0, "upper": 5.0, "steps": 21},
                    {"name": "y", "lower": -5.0, "upper": 5.0, "steps": 21},
                ],
            },
            "execution": {"timeout_seconds": 60},
        }
        results = ParameterSweepExperiment().execute(_ctx(cfg))
        assert results["best"]["parameters"] == {"x": 0.0, "y": 0.0}
        assert results["best"]["value"] == pytest.approx(0.0, abs=1e-9)

    def test_sphere_function(self):
        cfg = {
            "type": "parameter_sweep",
            "parameters": {
                "function": "sphere",
                "parametric_definitions": [{"name": "a", "lower": 0.0, "upper": 3.0, "steps": 7}],
            },
            "execution": {"timeout_seconds": 30},
        }
        results = ParameterSweepExperiment().execute(_ctx(cfg))
        assert results["best"]["value"] == pytest.approx(0.0, abs=1e-9)

    def test_validate_too_many_combinations(self):
        cfg = {
            "type": "parameter_sweep",
            "parameters": {
                "function": "quadratic",
                "parametric_definitions": [
                    {"name": "x", "lower": 0, "upper": 1, "steps": 200},
                    {"name": "y", "lower": 0, "upper": 1, "steps": 200},
                ],
            },
            "execution": {"timeout_seconds": 30},
        }
        errs = ParameterSweepExperiment().validate_config(cfg)
        assert any("combinations" in e.lower() for e in errs)
