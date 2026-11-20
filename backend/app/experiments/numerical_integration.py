"""Numerical Integration Benchmark — compare Euler, RK4, and SciPy RK45 methods."""
from __future__ import annotations

import logging
import time

import numpy as np
from scipy.integrate import solve_ivp

from app.experiments.base import BaseExperiment, ExperimentContext

logger = logging.getLogger(__name__)


class NumericalIntegrationBenchmark(BaseExperiment):
    """Compare numerical ODE solvers against an analytical solution.

    Uses y' = -λy, y(0) = y₀ → y(t) = y₀·exp(-λt).
    Compares Euler, RK4 (custom), and SciPy's solve_ivp (RK45).
    """

    type_name = "numerical_integration"

    VALID_EQUATIONS = {"exponential_decay", "sinusoidal", "linear"}

    def validate_config(self, config: dict) -> list[str]:
        errors = []
        params = config.get("parameters", {})

        if config.get("type") != self.type_name:
            errors.append(f"Configuration type must be {self.type_name!r}")

        eq = params.get("equation", "exponential_decay")
        if eq not in self.VALID_EQUATIONS:
            errors.append(f"equation must be one of {sorted(self.VALID_EQUATIONS)}")
        ivalue = params.get("initial_value", 1.0)
        if not isinstance(ivalue, (int, float)):
            errors.append("initial_value must be a number")
        decay = params.get("decay_constant", 0.5)
        if not isinstance(decay, (int, float)) or decay <= 0:
            errors.append("decay_constant must be a positive number")
        t_start = params.get("time_start", 0.0)
        t_end = params.get("time_end", 10.0)
        if t_start >= t_end:
            errors.append("time_start must be less than time_end")
        step = params.get("step_size", 0.1)
        if not isinstance(step, (int, float)) or step <= 0:
            errors.append("step_size must be a positive number")

        execution = config.get("execution", {})
        timeout = execution.get("timeout_seconds", 120)
        max_iter = execution.get("max_iterations", 100000)
        if timeout <= 0:
            errors.append("timeout_seconds must be positive")
        if max_iter <= 0:
            errors.append("max_iterations must be positive")

        return errors

    def execute(self, ctx: ExperimentContext) -> dict:
        params = ctx.config.get("parameters", {})
        equation = params.get("equation", "exponential_decay")
        y0 = params.get("initial_value", 1.0)
        lam = params.get("decay_constant", 0.5)
        t0 = params.get("time_start", 0.0)
        t1 = params.get("time_end", 10.0)
        step = params.get("step_size", 0.1)

        ctx.log("INFO", f"Starting integration benchmark: equation={equation}, λ={lam}")

        # --- Analytical solution for error comparison ---
        def analytical(t: np.ndarray) -> np.ndarray:
            if equation == "exponential_decay":
                return y0 * np.exp(-lam * t)
            elif equation == "sinusoidal":
                return y0 * np.sin(lam * t) * np.exp(-lam * t * 0.1)
            else:  # linear
                return y0 + lam * t

        t_eval = np.arange(t0, t1 + step, step)
        exact = analytical(t_eval)

        # --- Euler method ---
        ctx.log("INFO", "Running Euler method")
        t_euler = [t0]
        y_euler = [y0]
        start = time.perf_counter()
        n_feval_euler = 1
        while t_euler[-1] < t1:
            t_last = t_euler[-1]
            y_last = y_euler[-1]
            if equation == "exponential_decay":
                dydt = -lam * y_last
            elif equation == "sinusoidal":
                dydt = lam * y_last * np.cos(lam * t_last) - 0.05 * lam * y_last * np.sin(lam * t_last)
            else:
                dydt = lam
            t_next = min(t_last + step, t1)
            y_next = y_last + step * dydt
            t_euler.append(t_next)
            y_euler.append(y_next)
            n_feval_euler += 1
        euler_duration = time.perf_counter() - start
        euler_arr = np.array(y_euler)
        euler_err = np.max(np.abs(euler_arr[:len(t_eval)] - exact))
        euler_rerr = euler_err / (np.max(np.abs(exact)) + 1e-30)
        ctx.log("INFO", f"Euler completed: max_abs_error={euler_err:.6e}, steps={len(t_euler)}")
        ctx.record_metric("euler_max_abs_error", euler_err, unit="")
        ctx.record_metric("euler_relative_error", euler_rerr, unit="")
        ctx.record_metric("euler_duration_seconds", euler_duration, unit="s")
        ctx.record_metric("euler_function_evaluations", n_feval_euler, unit="count")
        ctx.record_metric("euler_step_count", len(t_euler), unit="count")

        # --- Classical RK4 ---
        ctx.log("INFO", "Running classical RK4 method")
        t_rk4 = [t0]
        y_rk4 = [y0]
        start = time.perf_counter()
        n_feval_rk4 = 0

        def rk4_step(t: float, y: float) -> tuple[float, int]:
            nonlocal n_feval_rk4

            def f(t_val: float, y_val: float) -> float:
                nonlocal n_feval_rk4
                n_feval_rk4 += 1
                if equation == "exponential_decay":
                    return -lam * y_val
                elif equation == "sinusoidal":
                    return lam * y_val * np.cos(lam * t_val) - 0.05 * lam * y_val * np.sin(lam * t_val)
                return lam

            k1 = f(t, y)
            k2 = f(t + step / 2, y + step / 2 * k1)
            k3 = f(t + step / 2, y + step / 2 * k2)
            k4 = f(t + step, y + step * k3)
            return y + (step / 6) * (k1 + 2 * k2 + 2 * k3 + k4), 4

        while t_rk4[-1] < t1:
            t_last = t_rk4[-1]
            y_last = y_rk4[-1]
            y_next, _ = rk4_step(t_last, y_last)
            t_next = min(t_last + step, t1)
            t_rk4.append(t_next)
            y_rk4.append(y_next)
        rk4_duration = time.perf_counter() - start
        rk4_arr = np.array(y_rk4)
        rk4_err = np.max(np.abs(rk4_arr[:len(t_eval)] - exact))
        rk4_rerr = rk4_err / (np.max(np.abs(exact)) + 1e-30)
        ctx.log("INFO", f"RK4 completed: max_abs_error={rk4_err:.6e}, steps={len(t_rk4)}")
        ctx.record_metric("rk4_max_abs_error", rk4_err, unit="")
        ctx.record_metric("rk4_relative_error", rk4_rerr, unit="")
        ctx.record_metric("rk4_duration_seconds", rk4_duration, unit="s")
        ctx.record_metric("rk4_function_evaluations", n_feval_rk4, unit="count")
        ctx.record_metric("rk4_step_count", len(t_rk4), unit="count")

        # --- SciPy solve_ivp (RK45) ---
        ctx.log("INFO", "Running SciPy solve_ivp (RK45)")
        start = time.perf_counter()
        n_feval_scipy = 0

        def rhs(t: float, y: float) -> float:
            nonlocal n_feval_scipy
            n_feval_scipy += 1
            if equation == "exponential_decay":
                return -lam * y
            elif equation == "sinusoidal":
                return lam * y * np.cos(lam * t) - 0.05 * lam * y * np.sin(lam * t)
            return lam

        sol = solve_ivp(rhs, (t0, t1), [y0], t_eval=t_eval, method="RK45", rtol=1e-8, atol=1e-10)
        scipy_duration = time.perf_counter() - start
        scipy_sol = sol.y[0]
        scipy_err = np.max(np.abs(scipy_sol - exact))
        scipy_rerr = scipy_err / (np.max(np.abs(exact)) + 1e-30)
        ctx.log("INFO", f"SciPy RK45 completed: max_abs_error={scipy_err:.6e}, successes={sol.success}")
        ctx.record_metric("scipy_max_abs_error", scipy_err, unit="")
        ctx.record_metric("scipy_relative_error", scipy_rerr, unit="")
        ctx.record_metric("scipy_duration_seconds", scipy_duration, unit="s")
        ctx.record_metric("scipy_function_evaluations", n_feval_scipy, unit="count")
        ctx.record_metric("scipy_step_count", len(sol.t), unit="count")

        # Error vs step size analysis (Euler at multiple step sizes)
        ctx.log("INFO", "Running error vs step size sweep")
        step_sizes = [0.1, 0.05, 0.025, 0.0125, 0.00625]
        for ss in step_sizes:
            t_s = np.arange(t0, t1 + ss, ss)
            ex_s = analytical(t_s)
            te = [t0]; ye = [y0]
            while te[-1] < t1:
                tl = te[-1]; yl = ye[-1]
                if equation == "exponential_decay":
                    dy = -lam * yl
                elif equation == "sinusoidal":
                    dy = lam * yl * np.cos(lam * tl) - 0.05 * lam * yl * np.sin(lam * tl)
                else:
                    dy = lam
                tn = min(tl + ss, t1)
                ye.append(yl + ss * dy)
                te.append(tn)
            err_s = np.max(np.abs(np.array(ye[:len(t_s)]) - ex_s))
            ctx.record_metric("euler_error_vs_step", err_s, extra={"step_size": ss})
            ctx.log("DEBUG", f"  Euler step={ss:.5f} error={err_s:.6e}")

        results = {
            "equation": equation,
            "analytical_solution": f"y(t) = {y0}·exp({-lam}·t)" if equation == "exponential_decay" else equation,
            "euler": {"max_abs_error": euler_err, "relative_error": euler_rerr, "duration": euler_duration},
            "rk4": {"max_abs_error": rk4_err, "relative_error": rk4_rerr, "duration": rk4_duration},
            "scipy_rk45": {"max_abs_error": scipy_err, "relative_error": scipy_rerr, "duration": scipy_duration},
            "total_steps_euler": len(t_euler),
            "total_steps_rk4": len(t_rk4),
            "total_steps_scipy": len(sol.t),
        }
        ctx.log("INFO", f"Benchmark complete in {ctx.duration:.3f}s")
        return results
