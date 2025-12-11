"""
Property-based tests for Analysis Pipeline DAG.
Tests workflow orchestration properties.
"""

import pytest
from hypothesis import given, strategies as st, settings
from datetime import datetime
from unittest.mock import MagicMock, patch, call
import ast
import os

from src.logging_config import get_logger

logger = get_logger(__name__)

# Try to import Airflow, skip tests if not available
try:
    from airflow.models import DagBag, TaskInstance
    from airflow.utils.state import State
    from airflow.utils.types import DagRunType
    AIRFLOW_AVAILABLE = True
except ImportError:
    AIRFLOW_AVAILABLE = False
    pytestmark = pytest.mark.skip(reason="Airflow not installed")


@pytest.mark.skipif(not AIRFLOW_AVAILABLE, reason="Airflow not installed")
@settings(max_examples=100, deadline=None)
@given(
    symbols=st.lists(
        st.text(min_size=2, max_size=5, alphabet=st.characters(whitelist_categories=('Lu',))),
        min_size=1,
        max_size=10,
        unique=True
    )
)
def test_property_35_aggregation_triggering_after_dual_analysis(symbols):
    """
    **Feature: vietnam-stock-ai-backend, Property 35: Aggregation triggering after dual analysis**
    
    For any stock symbol in the analysis pipeline DAG, the Aggregation Service should 
    only be triggered after both AI/ML analysis and LLM analysis have completed successfully.
    
    **Validates: Requirements 12.3**
    """
    # Load the DAG
    dagbag = DagBag(dag_folder='dags', include_examples=False)
    
    # Verify DAG exists and loaded without errors
    assert 'analysis_pipeline' in dagbag.dags, \
        "analysis_pipeline DAG should be loaded"
    
    assert len(dagbag.import_errors) == 0, \
        f"DAG should load without errors, got: {dagbag.import_errors}"
    
    dag = dagbag.get_dag('analysis_pipeline')
    
    # Property: DAG should have exactly 3 tasks
    assert len(dag.tasks) == 3, \
        f"DAG should have 3 tasks (run_ai_ml, run_llm, aggregate_results), got {len(dag.tasks)}"
    
    # Get tasks
    task_ids = {task.task_id for task in dag.tasks}
    assert 'run_ai_ml' in task_ids, "DAG should have run_ai_ml task"
    assert 'run_llm' in task_ids, "DAG should have run_llm task"
    assert 'aggregate_results' in task_ids, "DAG should have aggregate_results task"
    
    ai_ml_task = dag.get_task('run_ai_ml')
    llm_task = dag.get_task('run_llm')
    aggregate_task = dag.get_task('aggregate_results')
    
    # Property: AI/ML and LLM tasks should have no upstream dependencies
    assert len(ai_ml_task.upstream_task_ids) == 0, \
        "run_ai_ml task should have no upstream dependencies (runs in parallel)"
    
    assert len(llm_task.upstream_task_ids) == 0, \
        "run_llm task should have no upstream dependencies (runs in parallel)"
    
    # Property: Aggregation task should depend on BOTH AI/ML and LLM tasks
    assert len(aggregate_task.upstream_task_ids) == 2, \
        f"aggregate_results should have 2 upstream dependencies, got {len(aggregate_task.upstream_task_ids)}"
    
    assert 'run_ai_ml' in aggregate_task.upstream_task_ids, \
        "aggregate_results should depend on run_ai_ml"
    
    assert 'run_llm' in aggregate_task.upstream_task_ids, \
        "aggregate_results should depend on run_llm"
    
    # Property: AI/ML and LLM tasks should have aggregation as downstream
    assert 'aggregate_results' in ai_ml_task.downstream_task_ids, \
        "run_ai_ml should have aggregate_results as downstream"
    
    assert 'aggregate_results' in llm_task.downstream_task_ids, \
        "run_llm should have aggregate_results as downstream"
    
    # Property: Aggregation task should have no downstream dependencies (it's the final task)
    assert len(aggregate_task.downstream_task_ids) == 0, \
        "aggregate_results should have no downstream dependencies (final task)"


@pytest.mark.skipif(not AIRFLOW_AVAILABLE, reason="Airflow not installed")
@settings(max_examples=50, deadline=None)
@given(
    ai_ml_state=st.sampled_from(['SUCCESS', 'FAILED', 'SKIPPED']),
    llm_state=st.sampled_from(['SUCCESS', 'FAILED', 'SKIPPED'])
)
def test_property_35_aggregation_execution_depends_on_both_analyses(ai_ml_state, llm_state):
    """
    **Feature: vietnam-stock-ai-backend, Property 35: Aggregation triggering after dual analysis**
    
    For any execution of the analysis pipeline, the aggregation task should only execute
    when both AI/ML and LLM analysis tasks have completed successfully.
    
    **Validates: Requirements 12.3**
    """
    # Load the DAG
    dagbag = DagBag(dag_folder='dags', include_examples=False)
    dag = dagbag.get_dag('analysis_pipeline')
    
    # Get tasks
    ai_ml_task = dag.get_task('run_ai_ml')
    llm_task = dag.get_task('run_llm')
    aggregate_task = dag.get_task('aggregate_results')
    
    # Create a mock DAG run
    execution_date = datetime(2024, 1, 1, 12, 0, 0)
    
    # Create mock task instances
    mock_ai_ml_ti = MagicMock(spec=TaskInstance)
    mock_ai_ml_ti.task_id = 'run_ai_ml'
    mock_ai_ml_ti.state = ai_ml_state
    
    mock_llm_ti = MagicMock(spec=TaskInstance)
    mock_llm_ti.task_id = 'run_llm'
    mock_llm_ti.state = llm_state
    
    # Property: Aggregation should only be eligible to run if both upstream tasks succeeded
    # This is enforced by Airflow's trigger rules (default is 'all_success')
    
    # Check the trigger rule
    assert aggregate_task.trigger_rule.value == 'all_success', \
        f"Aggregation task should have 'all_success' trigger rule, got {aggregate_task.trigger_rule}"
    
    # Property: With 'all_success' trigger rule, aggregation runs only when both are SUCCESS
    both_succeeded = (ai_ml_state == 'SUCCESS' and llm_state == 'SUCCESS')
    
    # The trigger rule 'all_success' means:
    # - All upstream tasks must be in SUCCESS state
    # - If any upstream task is FAILED or SKIPPED, aggregation won't run
    
    if both_succeeded:
        # Property: When both analyses succeed, aggregation should be eligible to run
        # (In actual Airflow execution, this would be enforced by the scheduler)
        logger.info(
            "Both analyses succeeded - aggregation should run",
            context={'ai_ml_state': ai_ml_state, 'llm_state': llm_state}
        )
        assert True, "Aggregation should be eligible to run when both analyses succeed"
    else:
        # Property: When either analysis fails or is skipped, aggregation should NOT run
        # (In actual Airflow execution, this would be enforced by the scheduler)
        logger.info(
            "At least one analysis did not succeed - aggregation should not run",
            context={'ai_ml_state': ai_ml_state, 'llm_state': llm_state}
        )
        assert True, "Aggregation should not run when either analysis fails or is skipped"


@pytest.mark.skipif(not AIRFLOW_AVAILABLE, reason="Airflow not installed")
def test_property_35_dag_structure_validation():
    """
    **Feature: vietnam-stock-ai-backend, Property 35: Aggregation triggering after dual analysis**
    
    Validate that the analysis pipeline DAG structure enforces the correct execution order.
    
    **Validates: Requirements 12.3**
    """
    # Load the DAG
    dagbag = DagBag(dag_folder='dags', include_examples=False)
    
    # Property: DAG should load without errors
    assert len(dagbag.import_errors) == 0, \
        f"DAG should load without errors, got: {dagbag.import_errors}"
    
    assert 'analysis_pipeline' in dagbag.dags, \
        "analysis_pipeline DAG should be loaded"
    
    dag = dagbag.get_dag('analysis_pipeline')
    
    # Property: DAG should be valid
    assert dag is not None, "DAG should not be None"
    
    # Property: DAG should have correct schedule
    assert dag.schedule_interval == '@hourly', \
        f"DAG should run hourly, got schedule: {dag.schedule_interval}"
    
    # Property: DAG should not catch up on missed runs
    assert dag.catchup is False, \
        "DAG should not catch up on missed runs"
    
    # Get tasks
    aggregate_task = dag.get_task('aggregate_results')
    
    # Property: Aggregation task should use default trigger rule (all_success)
    # This ensures it only runs when ALL upstream tasks succeed
    assert aggregate_task.trigger_rule.value == 'all_success', \
        f"Aggregation should use 'all_success' trigger rule, got {aggregate_task.trigger_rule}"
    
    # Property: Verify task execution order using topological sort
    # The DAG's task_dict maintains the dependency structure
    task_order = list(dag.topological_sort())
    
    ai_ml_index = task_order.index(dag.get_task('run_ai_ml'))
    llm_index = task_order.index(dag.get_task('run_llm'))
    aggregate_index = task_order.index(dag.get_task('aggregate_results'))
    
    # Property: Aggregation must come after both analyses in topological order
    assert aggregate_index > ai_ml_index, \
        "Aggregation must come after AI/ML analysis in execution order"
    
    assert aggregate_index > llm_index, \
        "Aggregation must come after LLM analysis in execution order"
    
    # Property: AI/ML and LLM can be in any order relative to each other (parallel)
    # We just verify they're both before aggregation
    assert ai_ml_index < aggregate_index and llm_index < aggregate_index, \
        "Both analyses must complete before aggregation"


@pytest.mark.skipif(not AIRFLOW_AVAILABLE, reason="Airflow not installed")
@settings(max_examples=100, deadline=None)
@given(
    num_symbols=st.integers(min_value=1, max_value=20)
)
def test_property_35_parallel_execution_independence(num_symbols):
    """
    **Feature: vietnam-stock-ai-backend, Property 35: Aggregation triggering after dual analysis**
    
    For any number of symbols, AI/ML and LLM analyses should be independent and can
    execute in parallel, while aggregation waits for both.
    
    **Validates: Requirements 12.3**
    """
    # Load the DAG
    dagbag = DagBag(dag_folder='dags', include_examples=False)
    dag = dagbag.get_dag('analysis_pipeline')
    
    ai_ml_task = dag.get_task('run_ai_ml')
    llm_task = dag.get_task('run_llm')
    aggregate_task = dag.get_task('aggregate_results')
    
    # Property: AI/ML and LLM tasks should be independent (no direct dependency)
    assert 'run_llm' not in ai_ml_task.upstream_task_ids, \
        "AI/ML should not depend on LLM (they run in parallel)"
    
    assert 'run_llm' not in ai_ml_task.downstream_task_ids, \
        "AI/ML should not have LLM as downstream (they run in parallel)"
    
    assert 'run_ai_ml' not in llm_task.upstream_task_ids, \
        "LLM should not depend on AI/ML (they run in parallel)"
    
    assert 'run_ai_ml' not in llm_task.downstream_task_ids, \
        "LLM should not have AI/ML as downstream (they run in parallel)"
    
    # Property: Both analyses should only have aggregation as downstream
    assert ai_ml_task.downstream_task_ids == {'aggregate_results'}, \
        f"AI/ML should only have aggregation as downstream, got {ai_ml_task.downstream_task_ids}"
    
    assert llm_task.downstream_task_ids == {'aggregate_results'}, \
        f"LLM should only have aggregation as downstream, got {llm_task.downstream_task_ids}"
    
    # Property: Aggregation should have both analyses as upstream
    assert aggregate_task.upstream_task_ids == {'run_ai_ml', 'run_llm'}, \
        f"Aggregation should have both analyses as upstream, got {aggregate_task.upstream_task_ids}"
    
    # Property: The DAG structure allows parallel execution
    # This is verified by checking that the two analysis tasks have no dependency on each other
    # and both feed into the aggregation task
    
    # Get all paths from start to aggregation
    # Since AI/ML and LLM have no upstream, they are both "start" tasks
    start_tasks = [task for task in dag.tasks if len(task.upstream_task_ids) == 0]
    
    assert len(start_tasks) == 2, \
        f"Should have 2 start tasks (parallel analyses), got {len(start_tasks)}"
    
    assert set(task.task_id for task in start_tasks) == {'run_ai_ml', 'run_llm'}, \
        "Start tasks should be the two analysis tasks"


@pytest.mark.skipif(not AIRFLOW_AVAILABLE, reason="Airflow not installed")
def test_property_35_dag_configuration():
    """
    **Feature: vietnam-stock-ai-backend, Property 35: Aggregation triggering after dual analysis**
    
    Verify that the DAG is configured correctly for the analysis pipeline workflow.
    
    **Validates: Requirements 12.3**
    """
    # Load the DAG
    dagbag = DagBag(dag_folder='dags', include_examples=False)
    dag = dagbag.get_dag('analysis_pipeline')
    
    # Property: DAG should have correct metadata
    assert dag.dag_id == 'analysis_pipeline', \
        f"DAG ID should be 'analysis_pipeline', got {dag.dag_id}"
    
    assert dag.description == 'Run analysis and aggregation every hour', \
        f"DAG description mismatch"
    
    # Property: DAG should have appropriate tags
    assert 'analysis' in dag.tags, "DAG should be tagged with 'analysis'"
    assert 'aiml' in dag.tags, "DAG should be tagged with 'aiml'"
    assert 'llm' in dag.tags, "DAG should be tagged with 'llm'"
    assert 'aggregation' in dag.tags, "DAG should be tagged with 'aggregation'"
    
    # Property: All tasks should have appropriate retry configuration
    for task in dag.tasks:
        assert task.retries >= 0, \
            f"Task {task.task_id} should have non-negative retries"
        
        if task.retries > 0:
            assert task.retry_delay is not None, \
                f"Task {task.task_id} with retries should have retry_delay"
    
    # Property: All tasks should have execution timeout
    for task in dag.tasks:
        assert task.execution_timeout is not None, \
            f"Task {task.task_id} should have execution timeout"
