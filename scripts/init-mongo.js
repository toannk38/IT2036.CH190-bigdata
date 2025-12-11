// MongoDB initialization script
// This script runs when MongoDB container starts for the first time
// Requirements: 2.3, 9.1
// Creates collections, validation schemas, and indexes for optimal query performance

db = db.getSiblingDB('vietnam_stock_ai');

print('Starting MongoDB initialization for vietnam_stock_ai database...');

// ============================================================================
// COLLECTION CREATION WITH VALIDATION
// ============================================================================

// Symbols collection - stores stock symbol metadata
db.createCollection('symbols', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['symbol', 'organ_name', 'active'],
      properties: {
        symbol: {
          bsonType: 'string',
          description: 'Stock symbol code - required'
        },
        organ_name: {
          bsonType: 'string',
          description: 'Organization name - required'
        },
        icb_name2: {
          bsonType: 'string',
          description: 'ICB level 2 name'
        },
        icb_name3: {
          bsonType: 'string',
          description: 'ICB level 3 name'
        },
        icb_name4: {
          bsonType: 'string',
          description: 'ICB level 4 name'
        },
        com_type_code: {
          bsonType: 'string',
          description: 'Company type code'
        },
        icb_code: {
          bsonType: 'string',
          description: 'ICB code'
        },
        active: {
          bsonType: 'bool',
          description: 'Whether symbol is active - required'
        },
        created_at: {
          bsonType: 'date',
          description: 'Creation timestamp'
        },
        updated_at: {
          bsonType: 'date',
          description: 'Last update timestamp'
        }
      }
    }
  }
});
print('Created collection: symbols');

// Price history collection - stores historical price data
db.createCollection('price_history');
print('Created collection: price_history');

// News collection - stores news articles
db.createCollection('news');
print('Created collection: news');

// AI/ML analysis collection - stores quantitative analysis results
db.createCollection('ai_analysis');
print('Created collection: ai_analysis');

// LLM analysis collection - stores qualitative analysis results
db.createCollection('llm_analysis');
print('Created collection: llm_analysis');

// Final scores collection - stores aggregated recommendations
db.createCollection('final_scores');
print('Created collection: final_scores');

// ============================================================================
// INDEX CREATION FOR QUERY OPTIMIZATION
// Requirements: 9.1, 9.2
// ============================================================================

print('Creating indexes for optimal query performance...');

// Symbols indexes
db.symbols.createIndex({ symbol: 1 }, { unique: true, name: 'idx_symbol_unique' });
db.symbols.createIndex({ active: 1 }, { name: 'idx_active' });
print('Created indexes for symbols collection');

// Price history indexes - optimized for time-series queries
db.price_history.createIndex({ symbol: 1, timestamp: -1 }, { name: 'idx_symbol_timestamp' });
db.price_history.createIndex({ timestamp: -1 }, { name: 'idx_timestamp' });
db.price_history.createIndex({ symbol: 1 }, { name: 'idx_symbol' });
print('Created indexes for price_history collection');

// News indexes - optimized for date range queries
db.news.createIndex({ symbol: 1, published_at: -1 }, { name: 'idx_symbol_published' });
db.news.createIndex({ published_at: -1 }, { name: 'idx_published' });
db.news.createIndex({ symbol: 1 }, { name: 'idx_symbol' });
print('Created indexes for news collection');

// AI analysis indexes
db.ai_analysis.createIndex({ symbol: 1, timestamp: -1 }, { name: 'idx_symbol_timestamp' });
db.ai_analysis.createIndex({ timestamp: -1 }, { name: 'idx_timestamp' });
print('Created indexes for ai_analysis collection');

// LLM analysis indexes
db.llm_analysis.createIndex({ symbol: 1, timestamp: -1 }, { name: 'idx_symbol_timestamp' });
db.llm_analysis.createIndex({ timestamp: -1 }, { name: 'idx_timestamp' });
print('Created indexes for llm_analysis collection');

// Final scores indexes - optimized for alert queries
db.final_scores.createIndex({ symbol: 1, timestamp: -1 }, { name: 'idx_symbol_timestamp' });
db.final_scores.createIndex({ timestamp: -1 }, { name: 'idx_timestamp' });
db.final_scores.createIndex({ 'alerts.type': 1, timestamp: -1 }, { name: 'idx_alert_type_timestamp' });
db.final_scores.createIndex({ recommendation: 1, timestamp: -1 }, { name: 'idx_recommendation_timestamp' });
print('Created indexes for final_scores collection');

// ============================================================================
// VERIFICATION
// ============================================================================

print('\n=== MongoDB Initialization Summary ===');
print('Database: ' + db.getName());
print('Collections created: ' + db.getCollectionNames().length);
print('Collections: ' + db.getCollectionNames().join(', '));
print('\nIndexes created:');
db.getCollectionNames().forEach(function(collName) {
  var indexes = db.getCollection(collName).getIndexes();
  print('  ' + collName + ': ' + indexes.length + ' indexes');
});

print('\n✓ MongoDB initialization completed successfully!');
