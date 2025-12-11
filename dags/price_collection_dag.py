"""
Price Collection DAG for Vietnam Stock AI Backend.
Collects stock price data every 5 minutes and publishes to Kafka.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from kafka import KafkaProducer
from pymongo import MongoClient
import vnstock3 as vnstock

from src.collectors.price_collector import PriceCollector
from src.services.symbol_manager import SymbolManager
from src.config import config
from src.logging_config import get_logger

logger = get_logger(__name__)


def collect_price_data():
    """
    Collect price data for all active symbols and publish to Kafka.
    This function is called by the Airflow PythonOperator.
    """
    logger.info("Starting price data collection task")
    
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
        
        # Initialize PriceCollector
        price_collector = PriceCollector(
            kafka_producer=kafka_producer,
            vnstock_client=vnstock_client,
            symbol_manager=symbol_manager
        )
        
        # Collect price data
        result = price_collector.collect()
        
        # Log results
        logger.info(
            "Price data collection completed",
            context={
                'success_count': result.success_count,
                'failure_count': result.failure_count,
                'total_symbols': result.total_symbols,
                'failed_symbols': result.failed_symbols
            }
        )
        
        # Raise exception if all collections failed
        if result.total_symbols > 0 and result.success_count == 0:
            raise Exception("All price data collections failed")
        
        return {
            'success_count': result.success_count,
            'failure_count': result.failure_count,
            'total_symbols': result.total_symbols
        }
        
    except Exception as e:
        logger.error(
            "Error in price data collection task",
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
    'retry_delay': timedelta(minutes=1),
    'execution_timeout': timedelta(minutes=10),
}

# Define the DAG
with DAG(
    dag_id='price_collection',
    default_args=default_args,
    description='Collect stock prices every 5 minutes',
    schedule_interval='*/5 * * * *',  # Every 5 minutes
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['data-collection', 'price', 'vnstock'],
) as dag:
    
    # Create the price collection task
    collect_prices_task = PythonOperator(
        task_id='collect_prices',
        python_callable=collect_price_data,
        doc_md="""
        ### Collect Price Data
        
        This task collects stock price data for all active symbols from vnstock
        and publishes the data to the Kafka topic `stock_prices_raw`.
        
        **Frequency**: Every 5 minutes
        
        **Steps**:
        1. Connect to MongoDB and Kafka
        2. Retrieve active symbols from database
        3. Fetch price data for each symbol using vnstock
        4. Publish data to Kafka topic
        5. Log results and handle errors
        
        **Error Handling**:
        - Retries: 2 attempts with 1-minute delay
        - Timeout: 10 minutes
        - Individual symbol failures are logged but don't fail the entire task
        - Task fails only if all symbols fail to collect
        """,
    )

# Task is standalone, no dependencies
