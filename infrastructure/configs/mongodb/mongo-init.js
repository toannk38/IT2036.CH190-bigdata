// MongoDB Initialization Script for Stock AI System

// Switch to the stock_ai database
db = db.getSiblingDB('stock_ai');

// Create application user
db.createUser({
  user: 'stock_ai_user',
  pwd: 'StockAI@User2024',
  roles: [
    { role: 'readWrite', db: 'stock_ai' },
    { role: 'dbAdmin', db: 'stock_ai' }
  ]
});

// ================================================================
// COLLECTIONS CREATION
// ================================================================

// Create stocks collection (company metadata)
db.createCollection('stocks', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['symbol', 'company_name', 'exchange', 'industry', 'created_at'],
      properties: {
        symbol: { bsonType: 'string', description: 'Stock symbol (e.g., VCB, VIC)' },
        company_name: { bsonType: 'string', description: 'Company full name' },
        company_name_en: { bsonType: 'string', description: 'Company English name' },
        exchange: { 
          bsonType: 'string', 
          enum: ['HOSE', 'HNX', 'UPCOM'],
          description: 'Stock exchange' 
        },
        industry: { bsonType: 'string', description: 'Industry sector' },
        market_cap: { bsonType: 'number', description: 'Market capitalization' },
        listed_shares: { bsonType: 'number', description: 'Number of listed shares' },
        is_active: { bsonType: 'bool', description: 'Whether stock is actively traded' },
        metadata: { bsonType: 'object', description: 'Additional company metadata' },
        created_at: { bsonType: 'date', description: 'Record creation timestamp' },
        updated_at: { bsonType: 'date', description: 'Record update timestamp' }
      }
    }
  }
});

// Create price_history collection (historical price data)
db.createCollection('price_history', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['symbol', 'date', 'open', 'high', 'low', 'close', 'volume', 'created_at'],
      properties: {
        symbol: { bsonType: 'string', description: 'Stock symbol' },
        date: { bsonType: 'date', description: 'Trading date' },
        open: { bsonType: 'number', minimum: 0, description: 'Opening price' },
        high: { bsonType: 'number', minimum: 0, description: 'Highest price' },
        low: { bsonType: 'number', minimum: 0, description: 'Lowest price' },
        close: { bsonType: 'number', minimum: 0, description: 'Closing price' },
        volume: { bsonType: 'number', minimum: 0, description: 'Trading volume' },
        adjusted_close: { bsonType: 'number', description: 'Adjusted closing price' },
        change_percent: { bsonType: 'number', description: 'Daily change percentage' },
        value: { bsonType: 'number', description: 'Trading value' },
        created_at: { bsonType: 'date', description: 'Record creation timestamp' }
      }
    }
  }
});

// Create news collection (news articles)
db.createCollection('news', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['title', 'content', 'source', 'published_at', 'symbols', 'created_at'],
      properties: {
        title: { bsonType: 'string', description: 'News article title' },
        content: { bsonType: 'string', description: 'Article content' },
        summary: { bsonType: 'string', description: 'Article summary' },
        source: { bsonType: 'string', description: 'News source' },
        url: { bsonType: 'string', description: 'Original article URL' },
        author: { bsonType: 'string', description: 'Article author' },
        published_at: { bsonType: 'date', description: 'Publication timestamp' },
        symbols: { 
          bsonType: 'array',
          items: { bsonType: 'string' },
          description: 'Related stock symbols'
        },
        categories: {
          bsonType: 'array',
          items: { bsonType: 'string' },
          description: 'News categories'
        },
        language: { bsonType: 'string', description: 'Article language' },
        sentiment_raw: { bsonType: 'string', description: 'Raw sentiment classification' },
        is_processed: { bsonType: 'bool', description: 'Whether article has been processed' },
        created_at: { bsonType: 'date', description: 'Record creation timestamp' },
        updated_at: { bsonType: 'date', description: 'Record update timestamp' }
      }
    }
  }
});

// Create ai_analysis collection (AI/ML analysis results)
db.createCollection('ai_analysis', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['symbol', 'analysis_date', 'model_version', 'created_at'],
      properties: {
        symbol: { bsonType: 'string', description: 'Stock symbol' },
        analysis_date: { bsonType: 'date', description: 'Analysis date' },
        model_version: { bsonType: 'string', description: 'AI model version used' },
        technical_indicators: {
          bsonType: 'object',
          properties: {
            rsi: { bsonType: 'number', description: 'RSI indicator' },
            macd: { bsonType: 'number', description: 'MACD indicator' },
            bollinger_position: { bsonType: 'number', description: 'Bollinger Bands position' },
            ma_20: { bsonType: 'number', description: '20-day moving average' },
            ma_50: { bsonType: 'number', description: '50-day moving average' },
            ma_200: { bsonType: 'number', description: '200-day moving average' }
          }
        },
        patterns: {
          bsonType: 'object',
          properties: {
            candlestick_patterns: { bsonType: 'array', items: { bsonType: 'string' } },
            chart_patterns: { bsonType: 'array', items: { bsonType: 'string' } },
            trend_direction: { bsonType: 'string', enum: ['bullish', 'bearish', 'neutral'] }
          }
        },
        predictions: {
          bsonType: 'object',
          properties: {
            price_target_1d: { bsonType: 'number', description: '1-day price prediction' },
            price_target_7d: { bsonType: 'number', description: '7-day price prediction' },
            price_target_30d: { bsonType: 'number', description: '30-day price prediction' },
            confidence_score: { bsonType: 'number', minimum: 0, maximum: 1 },
            volatility_forecast: { bsonType: 'number', description: 'Expected volatility' }
          }
        },
        scores: {
          bsonType: 'object',
          properties: {
            technical_score: { bsonType: 'number', minimum: 0, maximum: 10 },
            trend_strength: { bsonType: 'number', minimum: 0, maximum: 10 },
            momentum_score: { bsonType: 'number', minimum: 0, maximum: 10 },
            risk_score: { bsonType: 'number', minimum: 0, maximum: 10 }
          }
        },
        created_at: { bsonType: 'date', description: 'Analysis creation timestamp' }
      }
    }
  }
});

// Create llm_analysis collection (LLM news analysis results)
db.createCollection('llm_analysis', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['news_id', 'symbols', 'analysis_date', 'llm_model', 'created_at'],
      properties: {
        news_id: { bsonType: 'objectId', description: 'Reference to news article' },
        symbols: {
          bsonType: 'array',
          items: { bsonType: 'string' },
          description: 'Related stock symbols'
        },
        analysis_date: { bsonType: 'date', description: 'Analysis date' },
        llm_model: { bsonType: 'string', description: 'LLM model used (gpt-4, claude, etc.)' },
        sentiment: {
          bsonType: 'object',
          properties: {
            overall_sentiment: { 
              bsonType: 'string', 
              enum: ['very_positive', 'positive', 'neutral', 'negative', 'very_negative'] 
            },
            confidence_score: { bsonType: 'number', minimum: 0, maximum: 1 },
            sentiment_score: { bsonType: 'number', minimum: -1, maximum: 1 },
            reasoning: { bsonType: 'string', description: 'LLM reasoning for sentiment' }
          }
        },
        impact_analysis: {
          bsonType: 'object',
          properties: {
            short_term_impact: { bsonType: 'string', enum: ['high', 'medium', 'low'] },
            long_term_impact: { bsonType: 'string', enum: ['high', 'medium', 'low'] },
            affected_sectors: { bsonType: 'array', items: { bsonType: 'string' } },
            key_factors: { bsonType: 'array', items: { bsonType: 'string' } }
          }
        },
        insights: {
          bsonType: 'object',
          properties: {
            summary: { bsonType: 'string', description: 'Key insights summary' },
            investment_implications: { bsonType: 'string', description: 'Investment implications' },
            risk_factors: { bsonType: 'array', items: { bsonType: 'string' } },
            opportunities: { bsonType: 'array', items: { bsonType: 'string' } }
          }
        },
        created_at: { bsonType: 'date', description: 'Analysis creation timestamp' }
      }
    }
  }
});

// Create final_scores collection (aggregated final scores)
db.createCollection('final_scores', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['symbol', 'score_date', 'final_score', 'created_at'],
      properties: {
        symbol: { bsonType: 'string', description: 'Stock symbol' },
        score_date: { bsonType: 'date', description: 'Score calculation date' },
        final_score: { bsonType: 'number', minimum: 0, maximum: 10, description: 'Final aggregated score' },
        component_scores: {
          bsonType: 'object',
          properties: {
            technical_score: { bsonType: 'number', minimum: 0, maximum: 10 },
            sentiment_score: { bsonType: 'number', minimum: 0, maximum: 10 },
            news_impact_score: { bsonType: 'number', minimum: 0, maximum: 10 },
            risk_adjusted_score: { bsonType: 'number', minimum: 0, maximum: 10 }
          }
        },
        weights: {
          bsonType: 'object',
          properties: {
            technical_weight: { bsonType: 'number', minimum: 0, maximum: 1 },
            sentiment_weight: { bsonType: 'number', minimum: 0, maximum: 1 },
            news_weight: { bsonType: 'number', minimum: 0, maximum: 1 },
            risk_weight: { bsonType: 'number', minimum: 0, maximum: 1 }
          }
        },
        recommendation: {
          bsonType: 'string',
          enum: ['BUY', 'WATCH', 'HOLD', 'RISK', 'SELL'],
          description: 'Investment recommendation'
        },
        confidence_level: { bsonType: 'number', minimum: 0, maximum: 1 },
        last_updated: { bsonType: 'date', description: 'Last score update timestamp' },
        created_at: { bsonType: 'date', description: 'Score creation timestamp' }
      }
    }
  }
});

// Create alerts collection (generated alerts)
db.createCollection('alerts', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['symbol', 'alert_type', 'message', 'severity', 'created_at'],
      properties: {
        symbol: { bsonType: 'string', description: 'Stock symbol' },
        alert_type: {
          bsonType: 'string',
          enum: ['PRICE_BREAKOUT', 'VOLUME_SPIKE', 'NEWS_IMPACT', 'TECHNICAL_SIGNAL', 'SCORE_CHANGE'],
          description: 'Type of alert'
        },
        message: { bsonType: 'string', description: 'Alert message' },
        severity: {
          bsonType: 'string',
          enum: ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'],
          description: 'Alert severity level'
        },
        trigger_conditions: { bsonType: 'object', description: 'Conditions that triggered the alert' },
        current_values: { bsonType: 'object', description: 'Current values when alert was triggered' },
        is_active: { bsonType: 'bool', description: 'Whether alert is still active' },
        acknowledged: { bsonType: 'bool', description: 'Whether alert has been acknowledged' },
        acknowledged_by: { bsonType: 'string', description: 'User who acknowledged the alert' },
        acknowledged_at: { bsonType: 'date', description: 'Alert acknowledgment timestamp' },
        expires_at: { bsonType: 'date', description: 'Alert expiration timestamp' },
        created_at: { bsonType: 'date', description: 'Alert creation timestamp' }
      }
    }
  }
});

// ================================================================
// INDEXES CREATION
// ================================================================

// Stocks collection indexes
db.stocks.createIndex({ symbol: 1 }, { unique: true });
db.stocks.createIndex({ exchange: 1 });
db.stocks.createIndex({ industry: 1 });
db.stocks.createIndex({ is_active: 1 });

// Price history collection indexes
db.price_history.createIndex({ symbol: 1, date: -1 });
db.price_history.createIndex({ date: -1 });
db.price_history.createIndex({ symbol: 1, date: -1 }, { unique: true });
db.price_history.createIndex({ volume: -1 });
db.price_history.createIndex({ change_percent: -1 });

// News collection indexes
db.news.createIndex({ symbols: 1, published_at: -1 });
db.news.createIndex({ published_at: -1 });
db.news.createIndex({ source: 1, published_at: -1 });
db.news.createIndex({ is_processed: 1 });
db.news.createIndex({ categories: 1 });
db.news.createIndex({ url: 1 }, { unique: true, sparse: true });

// AI analysis collection indexes
db.ai_analysis.createIndex({ symbol: 1, analysis_date: -1 });
db.ai_analysis.createIndex({ analysis_date: -1 });
db.ai_analysis.createIndex({ model_version: 1 });
db.ai_analysis.createIndex({ "scores.technical_score": -1 });
db.ai_analysis.createIndex({ "predictions.confidence_score": -1 });

// LLM analysis collection indexes
db.llm_analysis.createIndex({ symbols: 1, analysis_date: -1 });
db.llm_analysis.createIndex({ news_id: 1 });
db.llm_analysis.createIndex({ analysis_date: -1 });
db.llm_analysis.createIndex({ llm_model: 1 });
db.llm_analysis.createIndex({ "sentiment.overall_sentiment": 1 });

// Final scores collection indexes
db.final_scores.createIndex({ symbol: 1, score_date: -1 });
db.final_scores.createIndex({ final_score: -1 });
db.final_scores.createIndex({ recommendation: 1, final_score: -1 });
db.final_scores.createIndex({ score_date: -1 });
db.final_scores.createIndex({ symbol: 1, score_date: -1 }, { unique: true });

// Alerts collection indexes
db.alerts.createIndex({ symbol: 1, created_at: -1 });
db.alerts.createIndex({ alert_type: 1, created_at: -1 });
db.alerts.createIndex({ severity: 1, created_at: -1 });
db.alerts.createIndex({ is_active: 1, created_at: -1 });
db.alerts.createIndex({ acknowledged: 1 });
db.alerts.createIndex({ expires_at: 1 });

// ================================================================
// SAMPLE DATA INSERTION
// ================================================================

// Insert sample stock data
db.stocks.insertMany([
  {
    symbol: 'VCB',
    company_name: 'Ngân hàng TMCP Ngoại thương Việt Nam',
    company_name_en: 'Vietnam Joint Stock Commercial Bank for Foreign Trade',
    exchange: 'HOSE',
    industry: 'Banking',
    market_cap: 500000000000,
    listed_shares: 3500000000,
    is_active: true,
    metadata: {
      sector: 'Financial Services',
      established: 1963,
      employees: 25000
    },
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    symbol: 'VIC',
    company_name: 'Tập đoàn VINGROUP',
    company_name_en: 'Vingroup Joint Stock Company',
    exchange: 'HOSE',
    industry: 'Real Estate',
    market_cap: 400000000000,
    listed_shares: 4600000000,
    is_active: true,
    metadata: {
      sector: 'Real Estate',
      established: 1993,
      employees: 200000
    },
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    symbol: 'FPT',
    company_name: 'Tập đoàn FPT',
    company_name_en: 'FPT Corporation',
    exchange: 'HOSE',
    industry: 'Technology',
    market_cap: 200000000000,
    listed_shares: 1200000000,
    is_active: true,
    metadata: {
      sector: 'Information Technology',
      established: 1988,
      employees: 48000
    },
    created_at: new Date(),
    updated_at: new Date()
  }
]);

print('MongoDB initialization completed successfully!');
print('Created collections: stocks, price_history, news, ai_analysis, llm_analysis, final_scores, alerts');
print('Created indexes for performance optimization');
print('Inserted sample stock data');
print('Created application user: stock_ai_user');