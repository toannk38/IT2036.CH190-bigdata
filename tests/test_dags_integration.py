"""
Integration tests for Airflow DAGs.
Tests DAG parsing, validation, task execution order, and retry behavior.
"""

import pytest
import os
import sys
from datetime import datetime
from unittest.mock import MagicMock, patch

# Try to import Airflow, skip tests if not available
try:
    from airflow.models import DagBag
    from airflow.utils.state import State
    AIRFLOW_AVAILABLE = True
except ImportError:
    AIRFLOW_AVAILABLE = False
    pytestmark = pytest.mark.skip(reason="Airflow not installed")


@pytest.mark.skipif(not AIRFLOW_AVAILABLE, reason="Airflow not installed")
class TestDAGParsing:
    """Test DAG parsing and validation."""
    
    def test_dags_load_without_errors(self):
        """
        Test that all DAGs load without import errors.
        
        **Validates: Requirements 11.4, 12.3, 12.4**
        """
        dagbag = DagBag(dag_folder='dags', include_examples=False)
        
        # Check for import errors
        assert len(dagbag.import_errors) == 0, \
            f"DAGs should load without errors. Errors: {dagbag.import_errors}"
        
        # Check that expected DAGs are loaded
        expected_dags = ['price_collection', 'news_collection', 'analysis_pipeline']
        
        for dag_id in expected_dags:
            assert dag_id in dagbag.dags, \
                f"DAG '{dag_id}' should be loaded"
    
    def test_price_collection_dag_structure(self):
        """
        Test price collection DAG structure and configuration.
        
        **Validates: Requirements 11.2, 11.4**
        """
        dagbag = DagBag(dag_folder='dags', include_examples=False)
        dag = dagbag.get_dag('price_collection')
        
        # Verify DAG exists
        assert dag is not None, "price_collection DAG should exist"
        
        # Verify schedule
        assert dag.schedule_interval == '*/5 * * * *', \
            f"Price collection should run every 5 minutes, got {dag.schedule_interval}"
        
        # Verify tasks
        assert len(dag.tasks) == 1, \
            f"Price collection should have 1 task, got {len(dag.tasks)}"
        
        task = dag.tasks[0]
        assert task.task_id == 'collect_prices', \
            f"Task should be named 'collect_prices', got {task.task_id}"
        
        # Verify retry configuration
        assert task.retries == 2, \
            f"Task should have 2 retries, got {task.retries}"
        
        assert task.retry_delay.total_seconds() == 60, \
            f"Retry delay should be 1 minute, got {task.retry_delay.total_seconds()}s"
        
        # Verify execution timeout
        assert task.execution_timeout is not None, \
            "Task should have execution timeout"
        
        assert task.execution_timeout.total_seconds() == 600, \
            f"Execution timeout should be 10 minutes, got {task.execution_timeout.total_seconds()}s"
    
    def test_news_collection_dag_structure(self):
        """
        Test news collection DAG structure and configuration.
        
        **Validates: Requirements 11.3, 11.4**
        """
        dagbag = DagBag(dag_folder='dags', include_examples=False)
        dag = dagbag.get_dag('news_collection')
        
        # Verify DAG exists
        assert dag is not None, "news_collection DAG should exist"
        
        # Verify schedule
        assert dag.schedule_interval == '*/30 * * * *', \
            f"News collection should run every 30 minutes, got {dag.schedule_interval}"
        
        # Verify tasks
        assert len(dag.tasks) == 1, \
            f"News collection should have 1 task, got {len(dag.tasks)}"
        
        task = dag.tasks[0]
        assert task.task_id == 'collect_news', \
            f"Task should be named 'collect_news', got {task.task_id}"
        
        # Verify retry configuration
        assert task.retries == 2, \
            f"Task should have 2 retries, got {task.retries}"
        
        assert task.retry_delay.total_seconds() == 120, \
            f"Retry delay should be 2 minutes, got {task.retry_delay.total_seconds()}s"
        
        # Verify execution timeout
        assert task.execution_timeout is not None, \
            "Task should have execution timeout"
        
        assert task.execution_timeout.total_seconds() == 900, \
            f"Execution timeout should be 15 minutes, got {task.execution_timeout.total_seconds()}s"
    
    def test_analysis_pipeline_dag_structure(self):
        """
        Test analysis pipeline DAG structure and configuration.
        
        **Validates: Requirements 12.1, 12.3, 12.4, 12.5**
        """
        dagbag = DagBag(dag_folder='dags', include_examples=False)
        dag = dagbag.get_dag('analysis_pipeline')
        
        # Verify DAG exists
        assert dag is not None, "analysis_pipeline DAG should exist"
        
        # Verify schedule
        assert dag.schedule_interval == '@hourly', \
            f"Analysis pipeline should run hourly, got {dag.schedule_interval}"
        
        # Verify tasks
        assert len(dag.tasks) == 3, \
            f"Analysis pipeline should have 3 tasks, got {len(dag.tasks)}"
        
        task_ids = {task.task_id for task in dag.tasks}
        expected_tasks = {'run_ai_ml', 'run_llm', 'aggregate_results'}
        assert task_ids == expected_tasks, \
            f"Expected tasks {expected_tasks}, got {task_ids}"
        
        # Verify retry configuration for all tasks
        for task in dag.tasks:
            assert task.retries == 1, \
                f"Task {task.task_id} should have 1 retry, got {task.retries}"
            
            assert task.retry_delay.total_seconds() == 300, \
                f"Task {task.task_id} retry delay should be 5 minutes, got {task.retry_delay.total_seconds()}s"
            
            assert task.execution_timeout is not None, \
                f"Task {task.task_id} should have execution timeout"
            
            assert task.execution_timeout.total_seconds() == 1800, \
                f"Task {task.task_id} execution timeout should be 30 minutes, got {task.execution_timeout.total_seconds()}s"


@pytest.mark.skipif(not AIRFLOW_AVAILABLE, reason="Airflow not installed")
class TestTaskExecutionOrder:
    """Test task execution order and dependencies."""
    
    def test_analysis_pipeline_task_dependencies(self):
        """
        Test that analysis pipeline tasks have correct dependencies.
        
        **Validates: Requirements 12.3, 12.4**
        """
        dagbag = DagBag(dag_folder='dags', include_examples=False)
        dag = dagbag.get_dag('analysis_pipeline')
        
        ai_ml_task = dag.get_task('run_ai_ml')
        llm_task = dag.get_task('run_llm')
        aggregate_task = dag.get_task('aggregate_results')
        
        # AI/ML and LLM should have no upstream dependencies (parallel execution)
        assert len(ai_ml_task.upstream_task_ids) == 0, \
            "run_ai_ml should have no upstream dependencies"
        
        assert len(llm_task.upstream_task_ids) == 0, \
            "run_llm should have no upstream dependencies"
        
        # Aggregation should depend on both AI/ML and LLM
        assert len(aggregate_task.upstream_task_ids) == 2, \
            f"aggregate_results should have 2 upstream dependencies, got {len(aggregate_task.upstream_task_ids)}"
        
        assert 'run_ai_ml' in aggregate_task.upstream_task_ids, \
            "aggregate_results should depend on run_ai_ml"
        
        assert 'run_llm' in aggregate_task.upstream_task_ids, \
            "aggregate_results should depend on run_llm"
        
        # Verify downstream dependencies
        assert 'aggregate_results' in ai_ml_task.downstream_task_ids, \
            "run_ai_ml should have aggregate_results as downstream"
        
        assert 'aggregate_results' in llm_task.downstream_task_ids, \
            "run_llm should have aggregate_results as downstream"
        
        assert len(aggregate_task.downstream_task_ids) == 0, \
            "aggregate_results should have no downstream dependencies (final task)"
    
    def test_analysis_pipeline_topological_order(self):
        """
        Test that analysis pipeline tasks are in correct topological order.
        
        **Validates: Requirements 12.3, 12.4**
        """
        dagbag = DagBag(dag_folder='dags', include_examples=False)
        dag = dagbag.get_dag('analysis_pipeline')
        
        # Get topological sort
        task_order = list(dag.topological_sort())
        
        # Get task indices
        ai_ml_index = task_order.index(dag.get_task('run_ai_ml'))
        llm_index = task_order.index(dag.get_task('run_llm'))
        aggregate_index = task_order.index(dag.get_task('aggregate_results'))
        
        # Aggregation must come after both analyses
        assert aggregate_index > ai_ml_index, \
            "Aggregation must come after AI/ML analysis in topological order"
        
        assert aggregate_index > llm_index, \
            "Aggregation must come after LLM analysis in topological order"
    
    def test_collection_dags_have_no_dependencies(self):
        """
        Test that collection DAGs have no task dependencies (single task).
        
        **Validates: Requirements 11.2, 11.3**
        """
        dagbag = DagBag(dag_folder='dags', include_examples=False)
        
        # Test price collection
        price_dag = dagbag.get_dag('price_collection')
        price_task = price_dag.tasks[0]
        
        assert len(price_task.upstream_task_ids) == 0, \
            "Price collection task should have no upstream dependencies"
        
        assert len(price_task.downstream_task_ids) == 0, \
            "Price collection task should have no downstream dependencies"
        
        # Test news collection
        news_dag = dagbag.get_dag('news_collection')
        news_task = news_dag.tasks[0]
        
        assert len(news_task.upstream_task_ids) == 0, \
            "News collection task should have no upstream dependencies"
        
        assert len(news_task.downstream_task_ids) == 0, \
            "News collection task should have no downstream dependencies"


@pytest.mark.skipif(not AIRFLOW_AVAILABLE, reason="Airflow not installed")
class TestRetryBehavior:
    """Test retry behavior on failures."""
    
    def test_price_collection_retry_configuration(self):
        """
        Test that price collection has correct retry configuration.
        
        **Validates: Requirements 11.4**
        """
        dagbag = DagBag(dag_folder='dags', include_examples=False)
        dag = dagbag.get_dag('price_collection')
        task = dag.tasks[0]
        
        # Verify retry settings
        assert task.retries == 2, \
            "Price collection should retry 2 times on failure"
        
        assert task.retry_delay.total_seconds() == 60, \
            "Price collection should wait 1 minute between retries"
        
        # Verify task has execution timeout
        assert task.execution_timeout is not None, \
            "Price collection should have execution timeout"
    
    def test_news_collection_retry_configuration(self):
        """
        Test that news collection has correct retry configuration.
        
        **Validates: Requirements 11.4**
        """
        dagbag = DagBag(dag_folder='dags', include_examples=False)
        dag = dagbag.get_dag('news_collection')
        task = dag.tasks[0]
        
        # Verify retry settings
        assert task.retries == 2, \
            "News collection should retry 2 times on failure"
        
        assert task.retry_delay.total_seconds() == 120, \
            "News collection should wait 2 minutes between retries"
        
        # Verify task has execution timeout
        assert task.execution_timeout is not None, \
            "News collection should have execution timeout"
    
    def test_analysis_pipeline_retry_configuration(self):
        """
        Test that analysis pipeline tasks have correct retry configuration.
        
        **Validates: Requirements 11.4, 12.4**
        """
        dagbag = DagBag(dag_folder='dags', include_examples=False)
        dag = dagbag.get_dag('analysis_pipeline')
        
        # All tasks should have same retry configuration
        for task in dag.tasks:
            assert task.retries == 1, \
                f"Task {task.task_id} should retry 1 time on failure"
            
            assert task.retry_delay.total_seconds() == 300, \
                f"Task {task.task_id} should wait 5 minutes between retries"
            
            assert task.execution_timeout is not None, \
                f"Task {task.task_id} should have execution timeout"
    
    def test_aggregation_trigger_rule(self):
        """
        Test that aggregation task has correct trigger rule.
        
        **Validates: Requirements 12.3**
        """
        dagbag = DagBag(dag_folder='dags', include_examples=False)
        dag = dagbag.get_dag('analysis_pipeline')
        aggregate_task = dag.get_task('aggregate_results')
        
        # Aggregation should use 'all_success' trigger rule
        # This means it only runs if ALL upstream tasks succeed
        assert aggregate_task.trigger_rule.value == 'all_success', \
            f"Aggregation should use 'all_success' trigger rule, got {aggregate_task.trigger_rule}"


@pytest.mark.skipif(not AIRFLOW_AVAILABLE, reason="Airflow not installed")
class TestDAGConfiguration:
    """Test DAG configuration and metadata."""
    
    def test_all_dags_have_correct_metadata(self):
        """
        Test that all DAGs have correct metadata configuration.
        
        **Validates: Requirements 11.2, 11.3, 12.1**
        """
        dagbag = DagBag(dag_folder='dags', include_examples=False)
        
        for dag_id in ['price_collection', 'news_collection', 'analysis_pipeline']:
            dag = dagbag.get_dag(dag_id)
            
            # Verify DAG has owner
            assert dag.default_args.get('owner') == 'airflow', \
                f"DAG {dag_id} should have owner 'airflow'"
            
            # Verify catchup is disabled
            assert dag.catchup is False, \
                f"DAG {dag_id} should have catchup disabled"
            
            # Verify start date is set
            assert dag.start_date is not None, \
                f"DAG {dag_id} should have start_date"
            
            # Verify description is set
            assert dag.description is not None and len(dag.description) > 0, \
                f"DAG {dag_id} should have description"
    
    def test_all_dags_have_tags(self):
        """
        Test that all DAGs have appropriate tags.
        
        **Validates: Requirements 11.2, 11.3, 12.1**
        """
        dagbag = DagBag(dag_folder='dags', include_examples=False)
        
        # Price collection should have data-collection tags
        price_dag = dagbag.get_dag('price_collection')
        assert 'data-collection' in price_dag.tags, \
            "Price collection should be tagged with 'data-collection'"
        assert 'price' in price_dag.tags, \
            "Price collection should be tagged with 'price'"
        
        # News collection should have data-collection tags
        news_dag = dagbag.get_dag('news_collection')
        assert 'data-collection' in news_dag.tags, \
            "News collection should be tagged with 'data-collection'"
        assert 'news' in news_dag.tags, \
            "News collection should be tagged with 'news'"
        
        # Analysis pipeline should have analysis tags
        analysis_dag = dagbag.get_dag('analysis_pipeline')
        assert 'analysis' in analysis_dag.tags, \
            "Analysis pipeline should be tagged with 'analysis'"
        assert 'aiml' in analysis_dag.tags, \
            "Analysis pipeline should be tagged with 'aiml'"
        assert 'llm' in analysis_dag.tags, \
            "Analysis pipeline should be tagged with 'llm'"
        assert 'aggregation' in analysis_dag.tags, \
            "Analysis pipeline should be tagged with 'aggregation'"
    
    def test_all_tasks_have_documentation(self):
        """
        Test that all tasks have documentation.
        
        **Validates: Requirements 11.4, 12.4**
        """
        dagbag = DagBag(dag_folder='dags', include_examples=False)
        
        for dag_id in ['price_collection', 'news_collection', 'analysis_pipeline']:
            dag = dagbag.get_dag(dag_id)
            
            for task in dag.tasks:
                # Check if task has documentation
                assert task.doc_md is not None and len(task.doc_md) > 0, \
                    f"Task {task.task_id} in DAG {dag_id} should have documentation"
