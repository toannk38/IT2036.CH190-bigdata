"""
Consumers package for consuming data from Kafka and storing in MongoDB.
"""

from src.consumers.kafka_consumer import KafkaDataConsumer

__all__ = ['KafkaDataConsumer']
