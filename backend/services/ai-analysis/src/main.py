import logging
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from datetime import datetime
import uvicorn

from features.feature_calculator import FeatureCalculator
from training.model_trainer import ModelTrainer
from models.ensemble_model import EnsembleModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="AI Analysis Service",
    description="Stock AI Analysis and Prediction Service",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
feature_calculator = FeatureCalculator()
model_trainer = ModelTrainer()

# Pydantic models
class PredictionRequest(BaseModel):
    symbol: str
    include_features: bool = True

class TrainingRequest(BaseModel):
    symbols: List[str]
    retrain: bool = False

class AnalysisResponse(BaseModel):
    symbol: str
    timestamp: str
    prediction: float
    confidence: float
    recommendation: str
    features: Optional[Dict[str, Any]] = None
    model_accuracy: float

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "AI Analysis Service",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check model trainer
        summary = model_trainer.get_training_summary()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "models_loaded": summary.get('models_in_memory', 0),
            "total_trained_models": summary.get('total_models', 0)
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.post("/analyze/{symbol}")
async def analyze_stock(symbol: str, request: PredictionRequest = None) -> AnalysisResponse:
    """Analyze stock and generate prediction"""
    try:
        logger.info(f"Analyzing stock: {symbol}")
        
        # Get or train model
        model = model_trainer.get_model(symbol)
        if not model:
            # Train model if not exists
            training_result = model_trainer.train_model_for_symbol(symbol)
            if training_result['status'] != 'success':
                raise HTTPException(
                    status_code=404, 
                    detail=f"No model available for {symbol} and training failed"
                )
            model = model_trainer.get_model(symbol)
        
        # Fetch recent data for analysis
        recent_data = model_trainer._fetch_training_data(symbol, limit=50)
        if len(recent_data) < 10:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient data for analysis: {len(recent_data)} records"
            )
        
        # Calculate features
        features = None
        if not request or request.include_features:
            features = feature_calculator.calculate_features(recent_data)
        
        # Generate prediction
        prediction_result = model.predict(recent_data, features or {})
        
        return AnalysisResponse(
            symbol=symbol,
            timestamp=datetime.now().isoformat(),
            prediction=prediction_result.final_prediction,
            confidence=prediction_result.confidence,
            recommendation=prediction_result.recommendation,
            features=features,
            model_accuracy=prediction_result.ensemble_accuracy
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/train")
async def train_models(request: TrainingRequest):
    """Train models for multiple symbols"""
    try:
        logger.info(f"Training models for {len(request.symbols)} symbols")
        
        # Batch train models
        results = model_trainer.batch_train_models(request.symbols)
        
        return {
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "summary": results['summary'],
            "details": results['results']
        }
        
    except Exception as e:
        logger.error(f"Batch training failed: {e}")
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")

@app.get("/models")
async def list_models():
    """List all trained models"""
    try:
        summary = model_trainer.get_training_summary()
        return {
            "timestamp": datetime.now().isoformat(),
            "summary": summary
        }
    except Exception as e:
        logger.error(f"Failed to list models: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list models: {str(e)}")

@app.get("/features/{symbol}")
async def get_features(symbol: str):
    """Get technical features for a symbol"""
    try:
        # Fetch recent data
        recent_data = model_trainer._fetch_training_data(symbol, limit=50)
        if len(recent_data) < 10:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient data for feature calculation: {len(recent_data)} records"
            )
        
        # Calculate features
        features = feature_calculator.calculate_features(recent_data)
        
        return {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "features": features,
            "data_points": len(recent_data)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Feature calculation failed for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Feature calculation failed: {str(e)}")

@app.get("/metrics")
async def get_metrics():
    """Get service metrics"""
    try:
        summary = model_trainer.get_training_summary()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "service_metrics": {
                "models_in_memory": summary.get('models_in_memory', 0),
                "total_trained_models": summary.get('total_models', 0),
                "unique_symbols": summary.get('unique_symbols', 0),
                "service_uptime": "running"
            }
        }
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")

def main():
    """Main entry point"""
    logger.info("Starting AI Analysis Service")
    
    try:
        # Initialize service
        logger.info("AI Analysis Service initialized successfully")
        
        # Start FastAPI server
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info"
        )
        
    except Exception as e:
        logger.error(f"Failed to start AI Analysis Service: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()