import asyncio
import json
import websockets
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime
import aioredis
from motor.motor_asyncio import AsyncIOMotorClient

@dataclass
class RealtimeUpdate:
    stock_symbol: str
    update_type: str
    data: Dict[str, Any]
    timestamp: datetime

class RealtimeProcessor:
    """Real-time processing and WebSocket broadcasting for live updates"""
    
    def __init__(self, mongodb_url: str, redis_url: str):
        self.mongodb_url = mongodb_url
        self.redis_url = redis_url
        
        # WebSocket connections
        self.websocket_clients: Set[websockets.WebSocketServerProtocol] = set()
        self.client_subscriptions: Dict[websockets.WebSocketServerProtocol, Set[str]] = {}
        
        # Processing queues
        self.update_queue = asyncio.Queue()
        self.processing_active = False
        
        # Database connections
        self.mongo_client = None
        self.redis_client = None
        self.db = None
        
        # Cache for recent scores
        self.score_cache = {}
        self.cache_ttl = 300  # 5 minutes
        
    async def initialize(self):
        """Initialize database connections"""
        self.mongo_client = AsyncIOMotorClient(self.mongodb_url)
        self.db = self.mongo_client.stock_ai
        self.redis_client = await aioredis.from_url(self.redis_url)
    
    async def start_processing(self):
        """Start real-time processing"""
        if not self.processing_active:
            self.processing_active = True
            asyncio.create_task(self._process_updates())
            asyncio.create_task(self._periodic_score_updates())
    
    async def stop_processing(self):
        """Stop real-time processing"""
        self.processing_active = False
        if self.mongo_client:
            self.mongo_client.close()
        if self.redis_client:
            await self.redis_client.close()
    
    async def _process_updates(self):
        """Process updates from the queue"""
        while self.processing_active:
            try:
                update = await asyncio.wait_for(self.update_queue.get(), timeout=1.0)
                await self._handle_update(update)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"Error processing update: {e}")
    
    async def _periodic_score_updates(self):
        """Periodically update scores for active stocks"""
        while self.processing_active:
            try:
                # Get list of actively watched stocks
                active_stocks = await self._get_active_stocks()
                
                # Update scores for active stocks
                for stock_symbol in active_stocks:
                    await self.queue_score_update(stock_symbol)
                
                # Wait before next update cycle
                await asyncio.sleep(60)  # Update every minute
                
            except Exception as e:
                print(f"Error in periodic updates: {e}")
                await asyncio.sleep(30)
    
    async def _get_active_stocks(self) -> List[str]:
        """Get list of actively monitored stocks"""
        # Get stocks that have active WebSocket subscriptions
        subscribed_stocks = set()
        for subscriptions in self.client_subscriptions.values():
            subscribed_stocks.update(subscriptions)
        
        # Add top traded stocks (from database)
        try:
            cursor = self.db.stock_scores.find().sort("timestamp", -1).limit(50)
            recent_scores = await cursor.to_list(length=50)
            db_stocks = {score['stock_symbol'] for score in recent_scores}
            subscribed_stocks.update(db_stocks)
        except Exception:
            pass
        
        return list(subscribed_stocks)
    
    async def queue_score_update(self, stock_symbol: str):
        """Queue a score update for processing"""
        update = RealtimeUpdate(
            stock_symbol=stock_symbol,
            update_type="score_update",
            data={},
            timestamp=datetime.now()
        )
        await self.update_queue.put(update)
    
    async def queue_price_update(self, stock_symbol: str, price_data: Dict[str, Any]):
        """Queue a price update"""
        update = RealtimeUpdate(
            stock_symbol=stock_symbol,
            update_type="price_update",
            data=price_data,
            timestamp=datetime.now()
        )
        await self.update_queue.put(update)
    
    async def queue_news_update(self, stock_symbol: str, news_data: Dict[str, Any]):
        """Queue a news update"""
        update = RealtimeUpdate(
            stock_symbol=stock_symbol,
            update_type="news_update",
            data=news_data,
            timestamp=datetime.now()
        )
        await self.update_queue.put(update)
    
    async def _handle_update(self, update: RealtimeUpdate):
        """Handle different types of updates"""
        if update.update_type == "score_update":
            await self._handle_score_update(update)
        elif update.update_type == "price_update":
            await self._handle_price_update(update)
        elif update.update_type == "news_update":
            await self._handle_news_update(update)
    
    async def _handle_score_update(self, update: RealtimeUpdate):
        """Handle score recalculation and broadcasting"""
        stock_symbol = update.stock_symbol
        
        try:
            # Get latest score from aggregation service
            # This would call your score calculator
            from .score_calculator import ScoreCalculator
            calculator = ScoreCalculator()
            
            new_score = await calculator.calculate_comprehensive_score(stock_symbol)
            
            # Get previous score for comparison
            previous_score = self.score_cache.get(stock_symbol)
            
            # Update cache
            self.score_cache[stock_symbol] = new_score
            
            # Store in database
            await self._store_score(new_score)
            
            # Check for alerts
            if previous_score:
                from .alert_engine import AlertEngine
                alert_engine = AlertEngine()
                await alert_engine.process_score_update(new_score, previous_score, stock_symbol)
            
            # Broadcast to WebSocket clients
            await self._broadcast_score_update(stock_symbol, new_score, previous_score)
            
        except Exception as e:
            print(f"Error handling score update for {stock_symbol}: {e}")
    
    async def _handle_price_update(self, update: RealtimeUpdate):
        """Handle price updates"""
        stock_symbol = update.stock_symbol
        price_data = update.data
        
        # Store price update
        await self._store_price_update(stock_symbol, price_data)
        
        # Broadcast to clients
        await self._broadcast_price_update(stock_symbol, price_data)
        
        # Trigger score recalculation if significant price change
        price_change = price_data.get('change_percent', 0)
        if abs(price_change) > 2.0:  # 2% change threshold
            await self.queue_score_update(stock_symbol)
    
    async def _handle_news_update(self, update: RealtimeUpdate):
        """Handle news updates"""
        stock_symbol = update.stock_symbol
        news_data = update.data
        
        # Store news update
        await self._store_news_update(stock_symbol, news_data)
        
        # Broadcast to clients
        await self._broadcast_news_update(stock_symbol, news_data)
        
        # Trigger score recalculation for news impact
        await self.queue_score_update(stock_symbol)
    
    async def _store_score(self, score):
        """Store score in database"""
        try:
            score_doc = {
                'stock_symbol': score.stock_symbol,
                'technical_score': score.technical_score,
                'sentiment_score': score.sentiment_score,
                'risk_score': score.risk_score,
                'final_score': score.final_score,
                'recommendation': score.recommendation,
                'confidence': score.confidence,
                'components': score.components,
                'timestamp': score.timestamp
            }
            await self.db.stock_scores.insert_one(score_doc)
            
            # Also cache in Redis for quick access
            await self.redis_client.setex(
                f"score:{score.stock_symbol}",
                self.cache_ttl,
                json.dumps(score_doc, default=str)
            )
        except Exception as e:
            print(f"Error storing score: {e}")
    
    async def _store_price_update(self, stock_symbol: str, price_data: Dict[str, Any]):
        """Store price update"""
        try:
            price_doc = {
                'stock_symbol': stock_symbol,
                'price': price_data.get('price'),
                'change': price_data.get('change'),
                'change_percent': price_data.get('change_percent'),
                'volume': price_data.get('volume'),
                'timestamp': datetime.now()
            }
            await self.db.price_updates.insert_one(price_doc)
        except Exception as e:
            print(f"Error storing price update: {e}")
    
    async def _store_news_update(self, stock_symbol: str, news_data: Dict[str, Any]):
        """Store news update"""
        try:
            news_doc = {
                'stock_symbol': stock_symbol,
                'title': news_data.get('title'),
                'content': news_data.get('content'),
                'source': news_data.get('source'),
                'sentiment': news_data.get('sentiment'),
                'timestamp': datetime.now()
            }
            await self.db.news_updates.insert_one(news_doc)
        except Exception as e:
            print(f"Error storing news update: {e}")
    
    async def _broadcast_score_update(self, stock_symbol: str, new_score, previous_score):
        """Broadcast score update to WebSocket clients"""
        message = {
            'type': 'score_update',
            'stock_symbol': stock_symbol,
            'data': {
                'current_score': asdict(new_score),
                'previous_score': asdict(previous_score) if previous_score else None,
                'change': new_score.final_score - previous_score.final_score if previous_score else 0
            },
            'timestamp': datetime.now().isoformat()
        }
        
        await self._broadcast_to_subscribers(stock_symbol, message)
    
    async def _broadcast_price_update(self, stock_symbol: str, price_data: Dict[str, Any]):
        """Broadcast price update to WebSocket clients"""
        message = {
            'type': 'price_update',
            'stock_symbol': stock_symbol,
            'data': price_data,
            'timestamp': datetime.now().isoformat()
        }
        
        await self._broadcast_to_subscribers(stock_symbol, message)
    
    async def _broadcast_news_update(self, stock_symbol: str, news_data: Dict[str, Any]):
        """Broadcast news update to WebSocket clients"""
        message = {
            'type': 'news_update',
            'stock_symbol': stock_symbol,
            'data': news_data,
            'timestamp': datetime.now().isoformat()
        }
        
        await self._broadcast_to_subscribers(stock_symbol, message)
    
    async def _broadcast_to_subscribers(self, stock_symbol: str, message: Dict[str, Any]):
        """Broadcast message to subscribed WebSocket clients"""
        if not self.websocket_clients:
            return
        
        # Find clients subscribed to this stock
        target_clients = []
        for client, subscriptions in self.client_subscriptions.items():
            if stock_symbol in subscriptions or '*' in subscriptions:
                target_clients.append(client)
        
        # Send message to target clients
        if target_clients:
            message_json = json.dumps(message)
            await asyncio.gather(
                *[self._send_to_client(client, message_json) for client in target_clients],
                return_exceptions=True
            )
    
    async def _send_to_client(self, client: websockets.WebSocketServerProtocol, message: str):
        """Send message to individual WebSocket client"""
        try:
            await client.send(message)
        except websockets.exceptions.ConnectionClosed:
            # Remove disconnected client
            self.websocket_clients.discard(client)
            self.client_subscriptions.pop(client, None)
        except Exception as e:
            print(f"Error sending to client: {e}")
    
    async def handle_websocket_connection(self, websocket, path):
        """Handle new WebSocket connection"""
        self.websocket_clients.add(websocket)
        self.client_subscriptions[websocket] = set()
        
        try:
            async for message in websocket:
                await self._handle_websocket_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.websocket_clients.discard(websocket)
            self.client_subscriptions.pop(websocket, None)
    
    async def _handle_websocket_message(self, websocket, message: str):
        """Handle WebSocket message from client"""
        try:
            data = json.loads(message)
            action = data.get('action')
            
            if action == 'subscribe':
                stock_symbols = data.get('stocks', [])
                self.client_subscriptions[websocket].update(stock_symbols)
                
                # Send current scores for subscribed stocks
                for symbol in stock_symbols:
                    if symbol in self.score_cache:
                        score = self.score_cache[symbol]
                        await self._send_to_client(websocket, json.dumps({
                            'type': 'initial_score',
                            'stock_symbol': symbol,
                            'data': asdict(score),
                            'timestamp': datetime.now().isoformat()
                        }))
            
            elif action == 'unsubscribe':
                stock_symbols = data.get('stocks', [])
                self.client_subscriptions[websocket].difference_update(stock_symbols)
            
            elif action == 'ping':
                await self._send_to_client(websocket, json.dumps({'type': 'pong'}))
                
        except json.JSONDecodeError:
            await self._send_to_client(websocket, json.dumps({
                'type': 'error',
                'message': 'Invalid JSON message'
            }))
        except Exception as e:
            await self._send_to_client(websocket, json.dumps({
                'type': 'error',
                'message': str(e)
            }))
    
    async def get_realtime_stats(self) -> Dict[str, Any]:
        """Get real-time processing statistics"""
        return {
            'connected_clients': len(self.websocket_clients),
            'total_subscriptions': sum(len(subs) for subs in self.client_subscriptions.values()),
            'active_stocks': len(set().union(*self.client_subscriptions.values())),
            'queue_size': self.update_queue.qsize(),
            'processing_active': self.processing_active,
            'cache_size': len(self.score_cache)
        }