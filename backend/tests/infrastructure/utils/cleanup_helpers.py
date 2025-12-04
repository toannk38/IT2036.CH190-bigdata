"""Cleanup helper functions."""


def cleanup_mongodb_collections(client, collections):
    """Clean up MongoDB test collections."""
    db = client.stock_ai
    for collection in collections:
        db[collection].delete_many({})


def cleanup_redis_keys(client, pattern="test:*"):
    """Clean up Redis test keys."""
    for key in client.scan_iter(pattern):
        client.delete(key)


def cleanup_kafka_topics(admin_client, topics):
    """Clean up Kafka test topics."""
    try:
        admin_client.delete_topics(topics)
    except Exception as e:
        print(f"Error cleaning up Kafka topics: {e}")
