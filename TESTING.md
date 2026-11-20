# Testing Strategy

## Backend Tests

Location: `backend/tests/`

### Test Categories

#### Unit Tests (test_experiments.py)
- Schema validation (Pydantic models)
- Request/response formatting
- Edge cases (empty updates, defaults)

#### Scientific Correctness Tests (test_scientific.py)
- Numerical accuracy against known solutions
- Reproducibility with fixed seeds
- Validation rejection of invalid configs
- Boundary condition handling

### Running Tests

```bash
cd backend
pytest tests/ -v
pytest tests/test_scientific.py -v  # Scientific tests only
pytest tests/ -v --cov=app          # With coverage
```

### Test Coverage

```
tests/test_experiments.py
├── test_experiment_create_schema     # Schema validation
├── test_experiment_update_schema     # Partial updates
├── test_experiment_update_empty      # Empty update handling
├── test_tag_add                      # Tag schema
└── test_experiment_list_params_defaults  # Pagination defaults

tests/test_scientific.py
├── TestNumericalIntegration
│   ├── test_validate_valid_config         ✓
│   ├── test_validate_rejects_bad_equation ✓
│   ├── test_validate_rejects_negative_decay ✓
│   ├── test_exponential_decay_accuracy    ✓ (RK4 beats Euler)
│   └── test_reproducibility               ✓ (same seed = same result)
├── TestMonteCarlo
│   ├── test_estimate_pi_close             ✓ (within 0.05 of π)
│   ├── test_reproducibility               ✓
│   └── test_stratified_vs_basic           ✓
└── TestParameterSweep
    ├── test_quadratic_minimum_at_origin   ✓ (f(0,0) = 0)
    ├── test_sphere_function               ✓
    └── test_validate_too_many_combinations ✓ (>10k rejected)
```

## Frontend Tests

Location: `frontend/src/**/*.test.tsx`

### Testing Stack
- Vitest (test runner)
- React Testing Library (component testing)
- MSW (mock service worker for API mocking)

### Running Tests

```bash
cd frontend
npm test
npm run test:watch
```

### Test Guidelines

1. **Component rendering**: Verify UI renders without errors
2. **User interactions**: Test button clicks, form submissions
3. **API integration**: Mock fetch calls with MSW
4. **Error states**: Verify loading/error/empty states
5. **Accessibility**: Check ARIA attributes

## E2E Tests (Planned)

Location: `tests/e2e/`

Using Playwright for browser automation:

```typescript
test('complete experiment workflow', async ({ page }) => {
  // 1. Open application
  await page.goto('http://localhost:5173');
  
  // 2. Create experiment
  await page.click('[data-testid="new-experiment"]');
  await page.fill('[name="name"]', 'Test Exp');
  await page.click('[type="submit"]');
  
  // 3. Execute experiment
  await page.click('[data-testid="run"]');
  
  // 4. Wait for completion
  await page.waitForSelector('[data-testid="status-completed"]');
  
  // 5. View results
  await page.click('[data-testid="results"]');
  expect(await page.textContent('[data-testid="metric-value"]')).toBeTruthy();
});
```

## Performance Testing

Use Locust or k6 for load testing:

```python
# locustfile.py
from locust import HttpUser, task

class ResearchLabUser(HttpUser):
    @task
    def get_experiments(self):
        self.client.get("/api/v1/experiments")
    
    @task(3)
    def create_experiment(self):
        self.client.post("/api/v1/experiments", json={
            "name": f"Load Test {self.user_id}",
            "category": "general",
            "configuration": {}
        })
```

Run: `locust -f locustfile.py --users 10 --spawn-rate 1 --host http://localhost:8000`
