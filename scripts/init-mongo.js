// MongoDB initialization script
// This script runs when MongoDB container starts for the first time

db = db.getSiblingDB('vietnam_stock_ai');

// Create collections with validation
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

db.createCollection('price_history');
db.createCollection('news');
db.createCollection('ai_analysis');
db.createCollection('llm_analysis');
db.createCollection('final_scores');

// Create indexes for efficient querying
db.symbols.createIndex({ symbol: 1 }, { unique: true });
db.symbols.createIndex({ active: 1 });

db.price_history.createIndex({ symbol: 1, timestamp: -1 });
db.price_history.createIndex({ timestamp: -1 });

db.news.createIndex({ symbol: 1, published_at: -1 });
db.news.createIndex({ published_at: -1 });

db.ai_analysis.createIndex({ symbol: 1, timestamp: -1 });
db.ai_analysis.createIndex({ timestamp: -1 });

db.llm_analysis.createIndex({ symbol: 1, timestamp: -1 });
db.llm_analysis.createIndex({ timestamp: -1 });

db.final_scores.createIndex({ symbol: 1, timestamp: -1 });
db.final_scores.createIndex({ timestamp: -1 });
db.final_scores.createIndex({ 'alerts.type': 1, timestamp: -1 });

print('MongoDB initialization completed successfully');
