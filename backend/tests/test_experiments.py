"""Tests for experiment CRUD and validation."""
from __future__ import annotations

import uuid

import pytest

from app.schemas.experiment import ExperimentCreate, ExperimentUpdate


def test_experiment_create_schema():
    """Test that valid experiment create data passes schema validation."""
    data = ExperimentCreate(
        name="Test Exp",
        category="physics",
        configuration={"experiment": {"type": "numerical_integration"}},
    )
    assert data.name == "Test Exp"
    assert data.category == "physics"


def test_experiment_update_schema():
    """Test partial update works."""
    data = ExperimentUpdate(name="Updated")
    assert data.name == "Updated"
    assert data.description is None
    assert data.category is None


def test_experiment_update_empty():
    """Test empty update returns no fields."""
    data = ExperimentUpdate()
    assert data.model_dump(exclude_none=True) == {}


def test_tag_add():
    """Test tag add schema."""
    from app.schemas.experiment import TagAdd
    tag = TagAdd(tag="benchmark")
    assert tag.tag == "benchmark"


def test_experiment_list_params_defaults():
    """Test list params defaults."""
    from app.schemas.experiment import ExperimentListParams
    params = ExperimentListParams()
    assert params.skip == 0
    assert params.limit == 20
    assert params.sort_order == "desc"
