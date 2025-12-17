"""
News Collection DAG for Vietnam Stock AI Backend.
Collects stock news data every 30 minutes and publishes to Kafka.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from kafka import KafkaProducer
from pymongo import MongoClient
import vnstock

from src.collectors.news_collector import NewsCollector
from src.services.symbol_manager import SymbolManager
from src.config import config
from src.logging_config import get_logger

logger = get_logger(__name__)


def collect_news_data():
    """
    Collect news data for all active symbols and publish to Kafka.
    This function is called by the Airflow PythonOperator.
    """
    logger.info("Starting news data collection task")
    
    # Initialize MongoDB client
    mongo_client = None
    kafka_producer = None
    
    try:
        # Connect to MongoDB
        mongo_client = MongoClient(config.MONGODB_URI)
        logger.info(f"Connected to MongoDB: {config.MONGODB_URI}")
        
        # Initialize Kafka producer
        kafka_producer = KafkaProducer(
            bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS.split(','),
            value_serializer=lambda v: v  # Already serialized in collector
        )
        logger.info(f"Connected to Kafka: {config.KAFKA_BOOTSTRAP_SERVERS}")
        
        # Initialize vnstock client
        vnstock_client = vnstock
        
        # Initialize SymbolManager
        symbol_manager = SymbolManager(
            mongo_client=mongo_client,
            database_name=config.MONGODB_DATABASE
        )
        
        # Initialize NewsCollector
        news_collector = NewsCollector(
            kafka_producer=kafka_producer,
            vnstock_client=vnstock_client,
            symbol_manager=symbol_manager
        )
        
        # Collect news data
        result = news_collector.collect()
        
        # Log results
        logger.info(
            "News data collection completed",
            context={
                'success_count': result.success_count,
                'failure_count': result.failure_count,
                'total_symbols': result.total_symbols,
                'failed_symbols': result.failed_symbols
            }
        )
        
        # Raise exception if all collections failed
        if result.total_symbols > 0 and result.success_count == 0:
            raise Exception("All news data collections failed")
        
        return {
            'success_count': result.success_count,
            'failure_count': result.failure_count,
            'total_symbols': result.total_symbols
        }
        
    except Exception as e:
        logger.error(
            "Error in news data collection task",
            context={'error': str(e)},
            exc_info=True
        )
        raise
    
    finally:
        # Clean up connections
        if kafka_producer:
            kafka_producer.close()
            logger.debug("Kafka producer closed")
        
        if mongo_client:
            mongo_client.close()
            logger.debug("MongoDB client closed")


# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=2),
    'execution_timeout': timedelta(minutes=15),
}

# Define the DAG
with DAG(
    dag_id='news_collection',
    default_args=default_args,
    description='Collect stock news every 30 minutes',
    schedule_interval='*/30 * * * *',  # Every 30 minutes
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['data-collection', 'news', 'vnstock'],
) as dag:
    
    # Create the news collection task
    collect_news_task = PythonOperator(
        task_id='collect_news',
        python_callable=collect_news_data,
        doc_md="""
        ### Collect News Data
        
        This task collects stock news articles for all active symbols from vnstock
        and publishes the data to the Kafka topic `stock_news_raw`.
        
        **Frequency**: Every 30 minutes
        
        **Steps**:
        1. Connect to MongoDB and Kafka
        2. Retrieve active symbols from database
        3. Fetch news articles for each symbol using vnstock
        4. Publish each article to Kafka topic
        5. Log results and handle errors
        
        **Error Handling**:
        - Retries: 2 attempts with 2-minute delay
        - Timeout: 15 minutes
        - Individual symbol failures are logged but don't fail the entire task
        - Task fails only if all symbols fail to collect
        - Empty news results (no articles) are considered successful
        """,
    )

# Task is standalone, no dependencies
