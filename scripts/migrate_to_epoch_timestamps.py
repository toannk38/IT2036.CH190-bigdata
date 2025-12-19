#!/usr/bin/env python3
"""
Migration script to convert all timestamp fields from ISO format to epoch format.
This script will update all collections in the MongoDB database.
"""

import sys
import os
from datetime import datetime
from typing import Dict, Any, List
from pymongo import MongoClient
from pymongo.errors import PyMongoError

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config import get_config
from src.logging_config import get_logger
from src.utils.time_utils import safe_convert_to_epoch, current_epoch

logger = get_logger(__name__)


class TimestampMigrator:
    """
    Migrates timestamp fields from ISO format to epoch format across all collections.
    """
    
    # Define which fields to convert for each collection
    COLLECTION_TIMESTAMP_FIELDS = {
        'price_history': ['timestamp', 'created_at'],
        'news': ['published_at', 'collected_at', 'created_at'],
        'ai_analysis': ['timestamp'],
        'llm_analysis': ['timestamp'],
        'final_scores': ['timestamp'],
        'symbols': []  # No timestamp fields to migrate
    }
    
    def __init__(self, mongo_client: MongoClient, database_name: str = 'vietnam_stock_ai'):
        """
        Initialize the migrator.
        
        Args:
            mongo_client: MongoDB client instance
            database_name: Name of the database to migrate
        """
        self.client = mongo_client
        self.db = mongo_client[database_name]
        self.database_name = database_name
        
        logger.info(f"TimestampMigrator initialized for database: {database_name}")
    
    def migrate_all_collections(self, dry_run: bool = True) -> Dict[str, Any]:
        """
        Migrate all collections with timestamp fields.
        
        Args:
            dry_run: If True, only analyze without making changes
            
        Returns:
            Dictionary with migration results
        """
        logger.info(f"Starting timestamp migration (dry_run={dry_run})")
        
        results = {
            'collections_processed': 0,
            'total_documents_analyzed': 0,
            'total_documents_updated': 0,
            'collections': {},
            'errors': []
        }
        
        for collection_name, timestamp_fields in self.COLLECTION_TIMESTAMP_FIELDS.items():
            if not timestamp_fields:
                logger.info(f"Skipping {collection_name} - no timestamp fields to migrate")
                continue
            
            try:
                logger.info(f"Processing collection: {collection_name}")
                collection_result = self.migrate_collection(
                    collection_name, 
                    timestamp_fields, 
                    dry_run
                )
                
                results['collections'][collection_name] = collection_result
                results['collections_processed'] += 1
                results['total_documents_analyzed'] += collection_result['documents_analyzed']
                results['total_documents_updated'] += collection_result['documents_updated']
                
                logger.info(
                    f"Completed {collection_name}: "
                    f"analyzed={collection_result['documents_analyzed']}, "
                    f"updated={collection_result['documents_updated']}"
                )
                
            except Exception as e:
                error_msg = f"Error processing collection {collection_name}: {str(e)}"
                logger.error(error_msg, exc_info=True)
                results['errors'].append(error_msg)
        
        logger.info(
            f"Migration completed: "
            f"collections={results['collections_processed']}, "
            f"analyzed={results['total_documents_analyzed']}, "
            f"updated={results['total_documents_updated']}, "
            f"errors={len(results['errors'])}"
        )
        
        return results
    
    def migrate_collection(self, collection_name: str, timestamp_fields: List[str], 
                          dry_run: bool = True) -> Dict[str, Any]:
        """
        Migrate timestamp fields in a specific collection.
        
        Args:
            collection_name: Name of the collection to migrate
            timestamp_fields: List of timestamp field names to convert
            dry_run: If True, only analyze without making changes
            
        Returns:
            Dictionary with migration results for this collection
        """
        collection = self.db[collection_name]
        
        result = {
            'documents_analyzed': 0,
            'documents_updated': 0,
            'fields_converted': {},
            'errors': []
        }
        
        # Initialize field conversion counters
        for field in timestamp_fields:
            result['fields_converted'][field] = 0
        
        try:
            # Process documents in batches
            batch_size = 1000
            cursor = collection.find({})
            
            batch = []
            for document in cursor:
                result['documents_analyzed'] += 1
                
                # Check if document needs migration
                needs_update, updates = self._analyze_document(document, timestamp_fields)
                
                if needs_update:
                    if not dry_run:
                        batch.append({
                            '_id': document['_id'],
                            'updates': updates
                        })
                        
                        # Process batch when it reaches batch_size
                        if len(batch) >= batch_size:
                            self._process_batch(collection, batch, result)
                            batch = []
                    else:
                        # In dry run, just count what would be updated
                        result['documents_updated'] += 1
                        for field in updates:
                            result['fields_converted'][field] += 1
            
            # Process remaining batch
            if batch and not dry_run:
                self._process_batch(collection, batch, result)
                
        except Exception as e:
            error_msg = f"Error migrating collection {collection_name}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            result['errors'].append(error_msg)
        
        return result
    
    def _analyze_document(self, document: Dict[str, Any], 
                         timestamp_fields: List[str]) -> tuple[bool, Dict[str, float]]:
        """
        Analyze a document to determine if it needs timestamp migration.
        
        Args:
            document: MongoDB document
            timestamp_fields: List of timestamp fields to check
            
        Returns:
            Tuple of (needs_update, field_updates)
        """
        updates = {}
        
        for field in timestamp_fields:
            if field in document:
                value = document[field]
                
                # Skip if already epoch format (number)
                if isinstance(value, (int, float)):
                    continue
                
                # Try to convert ISO string to epoch
                if isinstance(value, str):
                    epoch_value = safe_convert_to_epoch(value)
                    if epoch_value is not None:
                        updates[field] = epoch_value
        
        return len(updates) > 0, updates
    
    def _process_batch(self, collection, batch: List[Dict], result: Dict[str, Any]):
        """
        Process a batch of document updates.
        
        Args:
            collection: MongoDB collection
            batch: List of documents to update
            result: Result dictionary to update
        """
        try:
            for item in batch:
                doc_id = item['_id']
                updates = item['updates']
                
                # Update document
                update_result = collection.update_one(
                    {'_id': doc_id},
                    {'$set': updates}
                )
                
                if update_result.modified_count > 0:
                    result['documents_updated'] += 1
                    for field in updates:
                        result['fields_converted'][field] += 1
                        
        except PyMongoError as e:
            error_msg = f"Error updating batch: {str(e)}"
            logger.error(error_msg, exc_info=True)
            result['errors'].append(error_msg)
    
    def verify_migration(self) -> Dict[str, Any]:
        """
        Verify that migration was successful by checking for remaining ISO timestamps.
        
        Returns:
            Dictionary with verification results
        """
        logger.info("Starting migration verification")
        
        verification_results = {
            'collections_checked': 0,
            'iso_timestamps_found': 0,
            'collections': {}
        }
        
        for collection_name, timestamp_fields in self.COLLECTION_TIMESTAMP_FIELDS.items():
            if not timestamp_fields:
                continue
            
            collection = self.db[collection_name]
            collection_result = {
                'documents_checked': 0,
                'iso_timestamps_found': 0,
                'fields': {}
            }
            
            # Check for remaining ISO format timestamps
            for field in timestamp_fields:
                # Find documents where the field is a string (likely ISO format)
                count = collection.count_documents({field: {'$type': 'string'}})
                collection_result['fields'][field] = count
                collection_result['iso_timestamps_found'] += count
            
            collection_result['documents_checked'] = collection.count_documents({})
            verification_results['collections'][collection_name] = collection_result
            verification_results['collections_checked'] += 1
            verification_results['iso_timestamps_found'] += collection_result['iso_timestamps_found']
        
        logger.info(
            f"Verification completed: "
            f"collections={verification_results['collections_checked']}, "
            f"remaining_iso_timestamps={verification_results['iso_timestamps_found']}"
        )
        
        return verification_results


def main():
    """Main function to run the migration."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Migrate timestamps from ISO to epoch format')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Analyze only, do not make changes')
    parser.add_argument('--verify', action='store_true',
                       help='Verify migration results')
    parser.add_argument('--database', default='vietnam_stock_ai',
                       help='Database name to migrate')
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        config = get_config()
        
        # Connect to MongoDB
        mongo_client = MongoClient(config.get('mongo_uri', 'mongodb://localhost:27017'))
        
        # Test connection
        mongo_client.admin.command('ping')
        logger.info(f"Connected to MongoDB: {config.get('mongo_uri', 'mongodb://localhost:27017')}")
        
        # Create migrator
        migrator = TimestampMigrator(mongo_client, args.database)
        
        if args.verify:
            # Verify migration
            verification_results = migrator.verify_migration()
            print("\n=== VERIFICATION RESULTS ===")
            print(f"Collections checked: {verification_results['collections_checked']}")
            print(f"ISO timestamps found: {verification_results['iso_timestamps_found']}")
            
            for collection_name, result in verification_results['collections'].items():
                print(f"\n{collection_name}:")
                print(f"  Documents: {result['documents_checked']}")
                print(f"  ISO timestamps: {result['iso_timestamps_found']}")
                for field, count in result['fields'].items():
                    if count > 0:
                        print(f"    {field}: {count} ISO timestamps remaining")
        else:
            # Run migration
            results = migrator.migrate_all_collections(dry_run=args.dry_run)
            
            print(f"\n=== MIGRATION RESULTS ({'DRY RUN' if args.dry_run else 'ACTUAL'}) ===")
            print(f"Collections processed: {results['collections_processed']}")
            print(f"Documents analyzed: {results['total_documents_analyzed']}")
            print(f"Documents updated: {results['total_documents_updated']}")
            
            if results['errors']:
                print(f"Errors: {len(results['errors'])}")
                for error in results['errors']:
                    print(f"  - {error}")
            
            print("\nPer-collection results:")
            for collection_name, result in results['collections'].items():
                print(f"\n{collection_name}:")
                print(f"  Analyzed: {result['documents_analyzed']}")
                print(f"  Updated: {result['documents_updated']}")
                print(f"  Fields converted:")
                for field, count in result['fields_converted'].items():
                    print(f"    {field}: {count}")
                
                if result['errors']:
                    print(f"  Errors: {len(result['errors'])}")
        
        if not args.dry_run and not args.verify:
            print(f"\n✅ Migration completed successfully!")
            print("Run with --verify to check results.")
        elif args.dry_run:
            print(f"\n📊 Dry run completed. Run without --dry-run to apply changes.")
        
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}", exc_info=True)
        print(f"❌ Migration failed: {str(e)}")
        sys.exit(1)
    finally:
        if 'mongo_client' in locals():
            mongo_client.close()


if __name__ == "__main__":
    main()