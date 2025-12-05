import logging
from typing import List, Dict, Any
from pymongo import MongoClient, UpdateOne
from pymongo.errors import ConnectionFailure, BulkWriteError
from ..exceptions.consumer_exceptions import MongoDBConnectionError, BatchProcessingError
from ..config.settings import MONGODB_URI, MONGODB_DATABASE, MONGODB_COLLECTION_NEWS

logger = logging.getLogger(__name__)

class NewsMongoDBAdapter:
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
        self._connect()
    
    def _connect(self):
        try:
            self.client = MongoClient(MONGODB_URI)
            self.db = self.client[MONGODB_DATABASE]
            self.collection = self.db[MONGODB_COLLECTION_NEWS]
            # Test connection
            self.client.admin.command('ping')
            logger.info("MongoDB connection established for news")
        except ConnectionFailure as e:
            logger.error(f"MongoDB connection failed: {e}")
            raise MongoDBConnectionError(f"Failed to connect to MongoDB: {e}")
    
    def upsert_batch(self, data_batch: List[Dict[str, Any]]) -> Dict[str, int]:
        if not data_batch:
            return {'upserted': 0, 'modified': 0}
        
        try:
            operations = []
            for data in data_batch:
                filter_criteria = {
                    'news_id': data['news_id']
                }
                operations.append(
                    UpdateOne(
                        filter_criteria,
                        {'$set': data},
                        upsert=True
                    )
                )
            
            result = self.collection.bulk_write(operations, ordered=False)
            
            stats = {
                'upserted': result.upserted_count,
                'modified': result.modified_count
            }
            
            logger.info(f"News batch upsert completed: {stats}")
            return stats
            
        except BulkWriteError as e:
            logger.error(f"News bulk write error: {e}")
            raise BatchProcessingError(f"Failed to process news batch: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during news batch upsert: {e}")
            raise BatchProcessingError(f"Unexpected error: {e}")
    
    def close(self):
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed for news")