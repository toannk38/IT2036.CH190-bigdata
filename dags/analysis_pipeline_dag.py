"""
Analysis Pipeline DAG for Vietnam Stock AI Backend.
Runs AI/ML and LLM analysis in parallel, then aggregates results.
Executes every hour.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from pymongo import MongoClient

from src.engines.aiml_engine import AIMLEngine
from src.engines.llm_engine import LLMEngine
from src.services.aggregation_service import AggregationService
from src.services.symbol_manager import SymbolManager
from src.config import config
from src.logging_config import get_logger

logger = get_logger(__name__)


def run_ai_ml_analysis():
    """
    Run AI/ML analysis for all active symbols.
    This function is called by the Airflow PythonOperator.
    """
    logger.info("Starting AI/ML analysis task")
    
    mongo_client = None
    
    try:
        # Connect to MongoDB
        mongo_client = MongoClient(config.MONGODB_URI)
        logger.info(f"Connected to MongoDB: {config.MONGODB_URI}")
        
        # Initialize SymbolManager
        symbol_manager = SymbolManager(
            mongo_client=mongo_client,
            database_name=config.MONGODB_DATABASE
        )
        
        # Initialize AIMLEngine
        aiml_engine = AIMLEngine(
            mongo_client=mongo_client,
            database_name=config.MONGODB_DATABASE
        )
        
        # Get active symbols
        symbols = symbol_manager.get_active_symbols()
        
        if not symbols:
            logger.warning("No active symbols found for AI/ML analysis")
            return {'success_count': 0, 'failure_count': 0, 'total_symbols': 0}
        
        logger.info(f"Running AI/ML analysis for {len(symbols)} symbols")
        
        # Analyze each symbol
        success_count = 0
        failure_count = 0
        
        for symbol in symbols:
            try:
                result = aiml_engine.analyze_stock(symbol, lookback_days=90)
                
                if result:
                    success_count += 1
                    logger.debug(f"AI/ML analysis completed for {symbol}")
                else:
                    failure_count += 1
                    logger.warning(f"AI/ML analysis returned None for {symbol}")
                    
            except Exception as e:
                failure_count += 1
                logger.error(
                    f"Error analyzing symbol",
                    context={'symbol': symbol, 'error': str(e)},
                    exc_info=True
                )
        
        logger.info(
            "AI/ML analysis task completed",
            context={
                'success_count': success_count,
                'failure_count': failure_count,
                'total_symbols': len(symbols)
            }
        )
        
        # Raise exception if all analyses failed
        if len(symbols) > 0 and success_count == 0:
            raise Exception("All AI/ML analyses failed")
        
        return {
            'success_count': success_count,
            'failure_count': failure_count,
            'total_symbols': len(symbols)
        }
        
    except Exception as e:
        logger.error(
            "Error in AI/ML analysis task",
            context={'error': str(e)},
            exc_info=True
        )
        raise
    
    finally:
        if mongo_client:
            mongo_client.close()
            logger.debug("MongoDB client closed")


def run_llm_analysis():
    """
    Run LLM analysis for all active symbols.
    This function is called by the Airflow PythonOperator.
    """
    logger.info("Starting LLM analysis task")
    
    mongo_client = None
    
    try:
        # Connect to MongoDB
        mongo_client = MongoClient(config.MONGODB_URI)
        logger.info(f"Connected to MongoDB: {config.MONGODB_URI}")
        
        # Initialize SymbolManager
        symbol_manager = SymbolManager(
            mongo_client=mongo_client,
            database_name=config.MONGODB_DATABASE
        )
        
        # Initialize LLMEngine
        llm_engine = LLMEngine(
            mongo_client=mongo_client,
            database_name=config.MONGODB_DATABASE,
            api_key=config.OPENAI_API_KEY,
            model=config.OPENAI_MODEL,
            use_openai=bool(config.OPENAI_API_KEY)
        )
        
        # Get active symbols
        symbols = symbol_manager.get_active_symbols()
        
        if not symbols:
            logger.warning("No active symbols found for LLM analysis")
            return {'success_count': 0, 'failure_count': 0, 'total_symbols': 0}
        
        logger.info(f"Running LLM analysis for {len(symbols)} symbols")
        
        # Analyze each symbol
        success_count = 0
        failure_count = 0
        
        for symbol in symbols:
            try:
                result = llm_engine.analyze_news(symbol, lookback_days=7)
                
                if result:
                    success_count += 1
                    logger.debug(f"LLM analysis completed for {symbol}")
                else:
                    failure_count += 1
                    logger.warning(f"LLM analysis returned None for {symbol} (possibly no news)")
                    
            except Exception as e:
                failure_count += 1
                logger.error(
                    f"Error analyzing symbol",
                    context={'symbol': symbol, 'error': str(e)},
                    exc_info=True
                )
        
        logger.info(
            "LLM analysis task completed",
            context={
                'success_count': success_count,
                'failure_count': failure_count,
                'total_symbols': len(symbols)
            }
        )
        
        # Raise exception if all analyses failed
        if len(symbols) > 0 and success_count == 0:
            raise Exception("All LLM analyses failed")
        
        return {
            'success_count': success_count,
            'failure_count': failure_count,
            'total_symbols': len(symbols)
        }
        
    except Exception as e:
        logger.error(
            "Error in LLM analysis task",
            context={'error': str(e)},
            exc_info=True
        )
        raise
    
    finally:
        if mongo_client:
            mongo_client.close()
            logger.debug("MongoDB client closed")


def aggregate_results():
    """
    Aggregate AI/ML and LLM analysis results for all active symbols.
    This function is called by the Airflow PythonOperator.
    """
    logger.info("Starting aggregation task")
    
    mongo_client = None
    
    try:
        # Connect to MongoDB
        mongo_client = MongoClient(config.MONGODB_URI)
        logger.info(f"Connected to MongoDB: {config.MONGODB_URI}")
        
        # Initialize SymbolManager
        symbol_manager = SymbolManager(
            mongo_client=mongo_client,
            database_name=config.MONGODB_DATABASE
        )
        
        # Initialize AggregationService
        aggregation_service = AggregationService(
            mongo_client=mongo_client,
            database_name=config.MONGODB_DATABASE,
            weights={
                'technical': config.WEIGHT_TECHNICAL,
                'risk': config.WEIGHT_RISK,
                'sentiment': config.WEIGHT_SENTIMENT
            }
        )
        
        # Get active symbols
        symbols = symbol_manager.get_active_symbols()
        
        if not symbols:
            logger.warning("No active symbols found for aggregation")
            return {'success_count': 0, 'failure_count': 0, 'total_symbols': 0}
        
        logger.info(f"Running aggregation for {len(symbols)} symbols")
        
        # Aggregate results for each symbol
        success_count = 0
        failure_count = 0
        
        for symbol in symbols:
            try:
                result = aggregation_service.aggregate(symbol)
                
                if result:
                    success_count += 1
                    logger.debug(
                        f"Aggregation completed for {symbol}",
                        context={
                            'final_score': result.final_score,
                            'recommendation': result.recommendation
                        }
                    )
                else:
                    failure_count += 1
                    logger.warning(f"Aggregation returned None for {symbol} (missing analysis data)")
                    
            except Exception as e:
                failure_count += 1
                logger.error(
                    f"Error aggregating results for symbol",
                    context={'symbol': symbol, 'error': str(e)},
                    exc_info=True
                )
        
        logger.info(
            "Aggregation task completed",
            context={
                'success_count': success_count,
                'failure_count': failure_count,
                'total_symbols': len(symbols)
            }
        )
        
        # Don't fail if some aggregations failed (analysis data might be missing)
        # Only fail if all aggregations failed
        if len(symbols) > 0 and success_count == 0:
            raise Exception("All aggregations failed")
        
        return {
            'success_count': success_count,
            'failure_count': failure_count,
            'total_symbols': len(symbols)
        }
        
    except Exception as e:
        logger.error(
            "Error in aggregation task",
            context={'error': str(e)},
            exc_info=True
        )
        raise
    
    finally:
        if mongo_client:
            mongo_client.close()
            logger.debug("MongoDB client closed")


# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(minutes=30),
}

# Define the DAG
with DAG(
    dag_id='analysis_pipeline',
    default_args=default_args,
    description='Run analysis and aggregation every hour',
    schedule_interval='@hourly',  # Every hour
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['analysis', 'aiml', 'llm', 'aggregation'],
) as dag:
    
    # Create AI/ML analysis task
    run_ai_ml_task = PythonOperator(
        task_id='run_ai_ml',
        python_callable=run_ai_ml_analysis,
        doc_md="""
        ### Run AI/ML Analysis
        
        This task performs quantitative analysis on stock price data for all active symbols.
        
        **Analysis includes**:
        - Trend prediction using time-series analysis
        - Risk score calculation based on volatility
        - Technical score calculation using indicators (RSI, MACD, Bollinger Bands)
        
        **Data source**: MongoDB `price_history` collection (90 days lookback)
        
        **Output**: Results stored in MongoDB `ai_analysis` collection
        
        **Error Handling**:
        - Retries: 1 attempt with 5-minute delay
        - Timeout: 30 minutes
        - Individual symbol failures are logged but don't fail the entire task
        """,
    )
    
    # Create LLM analysis task
    run_llm_task = PythonOperator(
        task_id='run_llm',
        python_callable=run_llm_analysis,
        doc_md="""
        ### Run LLM Analysis
        
        This task performs qualitative analysis on news articles for all active symbols.
        
        **Analysis includes**:
        - Sentiment analysis of news articles
        - Summary generation of key points
        - Influence score calculation based on source credibility
        
        **Data source**: MongoDB `news` collection (7 days lookback)
        
        **Output**: Results stored in MongoDB `llm_analysis` collection
        
        **Error Handling**:
        - Retries: 1 attempt with 5-minute delay
        - Timeout: 30 minutes
        - Individual symbol failures are logged but don't fail the entire task
        - Symbols with no news articles are logged as warnings
        """,
    )
    
    # Create aggregation task
    aggregate_task = PythonOperator(
        task_id='aggregate_results',
        python_callable=aggregate_results,
        doc_md="""
        ### Aggregate Results
        
        This task combines AI/ML and LLM analysis results to generate final recommendations.
        
        **Aggregation includes**:
        - Weighted combination of technical, risk, and sentiment scores
        - Final recommendation score (0-100)
        - Alert generation based on score thresholds
        
        **Data sources**: 
        - MongoDB `ai_analysis` collection
        - MongoDB `llm_analysis` collection
        
        **Output**: Results stored in MongoDB `final_scores` collection
        
        **Weights** (configurable via environment variables):
        - Technical: 40%
        - Risk: 30%
        - Sentiment: 30%
        
        **Alert Thresholds**:
        - Score > 70: BUY alert (high priority)
        - Score 40-70: WATCH alert (medium priority)
        - Score < 40: RISK alert (high priority)
        
        **Error Handling**:
        - Retries: 1 attempt with 5-minute delay
        - Timeout: 30 minutes
        - Symbols missing analysis data are logged as warnings
        """,
    )
    
    # Define task dependencies
    # Both AI/ML and LLM analyses run in parallel
    # Aggregation runs after both complete
    [run_ai_ml_task, run_llm_task] >> aggregate_task
