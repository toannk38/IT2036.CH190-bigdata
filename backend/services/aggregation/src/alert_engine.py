import asyncio
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import json

class AlertType(Enum):
    SCORE_CHANGE = "score_change"
    RECOMMENDATION_CHANGE = "recommendation_change"
    THRESHOLD_BREACH = "threshold_breach"
    PATTERN_DETECTED = "pattern_detected"
    RISK_ALERT = "risk_alert"
    VOLUME_SPIKE = "volume_spike"

class AlertPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class Alert:
    id: str
    alert_type: AlertType
    priority: AlertPriority
    stock_symbol: str
    title: str
    message: str
    data: Dict[str, Any]
    timestamp: datetime
    expires_at: Optional[datetime] = None
    acknowledged: bool = False
    sent: bool = False

@dataclass
class AlertRule:
    id: str
    name: str
    alert_type: AlertType
    conditions: Dict[str, Any]
    priority: AlertPriority
    enabled: bool = True
    cooldown_minutes: int = 60
    last_triggered: Optional[datetime] = None

class AlertEngine:
    """Generate and manage trading alerts based on score changes and patterns"""
    
    def __init__(self):
        self.alerts = []
        self.alert_rules = []
        self.subscribers = []
        self.alert_history = []
        
        # Initialize default rules
        self._setup_default_rules()
        
        # Deduplication tracking
        self.recent_alerts = {}
        self.dedup_window = timedelta(minutes=30)
    
    def _setup_default_rules(self):
        """Setup default alert rules"""
        default_rules = [
            AlertRule(
                id="strong_buy_signal",
                name="Strong Buy Signal",
                alert_type=AlertType.RECOMMENDATION_CHANGE,
                conditions={
                    "new_recommendation": "BUY",
                    "min_confidence": 0.7,
                    "min_score": 0.75
                },
                priority=AlertPriority.HIGH,
                cooldown_minutes=120
            ),
            AlertRule(
                id="strong_sell_signal",
                name="Strong Sell Signal",
                alert_type=AlertType.RECOMMENDATION_CHANGE,
                conditions={
                    "new_recommendation": "STRONG_SELL",
                    "min_confidence": 0.6
                },
                priority=AlertPriority.HIGH,
                cooldown_minutes=120
            ),
            AlertRule(
                id="score_spike",
                name="Score Spike",
                alert_type=AlertType.SCORE_CHANGE,
                conditions={
                    "min_change": 0.2,
                    "timeframe_minutes": 60
                },
                priority=AlertPriority.MEDIUM,
                cooldown_minutes=60
            ),
            AlertRule(
                id="high_risk_alert",
                name="High Risk Alert",
                alert_type=AlertType.RISK_ALERT,
                conditions={
                    "risk_threshold": 0.8,
                    "min_confidence": 0.5
                },
                priority=AlertPriority.HIGH,
                cooldown_minutes=180
            ),
            AlertRule(
                id="bullish_pattern",
                name="Bullish Pattern Detected",
                alert_type=AlertType.PATTERN_DETECTED,
                conditions={
                    "pattern_signal": "bullish",
                    "min_confidence": 0.7
                },
                priority=AlertPriority.MEDIUM,
                cooldown_minutes=240
            ),
            AlertRule(
                id="bearish_pattern",
                name="Bearish Pattern Detected",
                alert_type=AlertType.PATTERN_DETECTED,
                conditions={
                    "pattern_signal": "bearish",
                    "min_confidence": 0.7
                },
                priority=AlertPriority.MEDIUM,
                cooldown_minutes=240
            )
        ]
        
        self.alert_rules.extend(default_rules)
    
    def add_alert_rule(self, rule: AlertRule):
        """Add custom alert rule"""
        self.alert_rules.append(rule)
    
    def remove_alert_rule(self, rule_id: str):
        """Remove alert rule"""
        self.alert_rules = [r for r in self.alert_rules if r.id != rule_id]
    
    def subscribe(self, callback: Callable[[Alert], None]):
        """Subscribe to alert notifications"""
        self.subscribers.append(callback)
    
    async def notify_subscribers(self, alert: Alert):
        """Notify all subscribers of new alert"""
        for callback in self.subscribers:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(alert)
                else:
                    callback(alert)
            except Exception as e:
                print(f"Error notifying subscriber: {e}")
    
    def _generate_alert_id(self, stock_symbol: str, alert_type: AlertType) -> str:
        """Generate unique alert ID"""
        timestamp = int(datetime.now().timestamp())
        return f"{stock_symbol}_{alert_type.value}_{timestamp}"
    
    def _is_duplicate_alert(self, stock_symbol: str, alert_type: AlertType, 
                          message: str) -> bool:
        """Check if alert is duplicate within dedup window"""
        key = f"{stock_symbol}_{alert_type.value}_{hash(message)}"
        now = datetime.now()
        
        if key in self.recent_alerts:
            last_time = self.recent_alerts[key]
            if now - last_time < self.dedup_window:
                return True
        
        self.recent_alerts[key] = now
        return False
    
    def _check_rule_cooldown(self, rule: AlertRule, stock_symbol: str) -> bool:
        """Check if rule is in cooldown period"""
        if not rule.last_triggered:
            return False
        
        cooldown = timedelta(minutes=rule.cooldown_minutes)
        return datetime.now() - rule.last_triggered < cooldown
    
    async def check_score_alerts(self, current_score, previous_score, stock_symbol: str):
        """Check for score-based alerts"""
        if not previous_score:
            return
        
        score_change = current_score.final_score - previous_score.final_score
        
        for rule in self.alert_rules:
            if (rule.alert_type == AlertType.SCORE_CHANGE and 
                rule.enabled and 
                not self._check_rule_cooldown(rule, stock_symbol)):
                
                conditions = rule.conditions
                min_change = conditions.get('min_change', 0.1)
                
                if abs(score_change) >= min_change:
                    direction = "increased" if score_change > 0 else "decreased"
                    
                    alert = Alert(
                        id=self._generate_alert_id(stock_symbol, AlertType.SCORE_CHANGE),
                        alert_type=AlertType.SCORE_CHANGE,
                        priority=rule.priority,
                        stock_symbol=stock_symbol,
                        title=f"Score {direction.title()} - {stock_symbol}",
                        message=f"Score {direction} by {abs(score_change):.2f} to {current_score.final_score:.2f}",
                        data={
                            'previous_score': previous_score.final_score,
                            'current_score': current_score.final_score,
                            'change': score_change,
                            'recommendation': current_score.recommendation
                        },
                        timestamp=datetime.now()
                    )
                    
                    if not self._is_duplicate_alert(stock_symbol, AlertType.SCORE_CHANGE, alert.message):
                        await self._create_alert(alert, rule)
    
    async def check_recommendation_alerts(self, current_score, previous_score, stock_symbol: str):
        """Check for recommendation change alerts"""
        if not previous_score or current_score.recommendation == previous_score.recommendation:
            return
        
        for rule in self.alert_rules:
            if (rule.alert_type == AlertType.RECOMMENDATION_CHANGE and 
                rule.enabled and 
                not self._check_rule_cooldown(rule, stock_symbol)):
                
                conditions = rule.conditions
                target_recommendation = conditions.get('new_recommendation')
                min_confidence = conditions.get('min_confidence', 0.5)
                
                if (not target_recommendation or current_score.recommendation == target_recommendation) and \
                   current_score.confidence >= min_confidence:
                    
                    alert = Alert(
                        id=self._generate_alert_id(stock_symbol, AlertType.RECOMMENDATION_CHANGE),
                        alert_type=AlertType.RECOMMENDATION_CHANGE,
                        priority=rule.priority,
                        stock_symbol=stock_symbol,
                        title=f"Recommendation Changed - {stock_symbol}",
                        message=f"Recommendation changed from {previous_score.recommendation} to {current_score.recommendation}",
                        data={
                            'previous_recommendation': previous_score.recommendation,
                            'current_recommendation': current_score.recommendation,
                            'confidence': current_score.confidence,
                            'score': current_score.final_score
                        },
                        timestamp=datetime.now()
                    )
                    
                    if not self._is_duplicate_alert(stock_symbol, AlertType.RECOMMENDATION_CHANGE, alert.message):
                        await self._create_alert(alert, rule)
    
    async def check_threshold_alerts(self, current_score, stock_symbol: str):
        """Check for threshold breach alerts"""
        for rule in self.alert_rules:
            if (rule.alert_type == AlertType.THRESHOLD_BREACH and 
                rule.enabled and 
                not self._check_rule_cooldown(rule, stock_symbol)):
                
                conditions = rule.conditions
                threshold = conditions.get('threshold')
                direction = conditions.get('direction', 'above')  # 'above' or 'below'
                
                if threshold is not None:
                    breached = (direction == 'above' and current_score.final_score >= threshold) or \
                              (direction == 'below' and current_score.final_score <= threshold)
                    
                    if breached:
                        alert = Alert(
                            id=self._generate_alert_id(stock_symbol, AlertType.THRESHOLD_BREACH),
                            alert_type=AlertType.THRESHOLD_BREACH,
                            priority=rule.priority,
                            stock_symbol=stock_symbol,
                            title=f"Threshold Breached - {stock_symbol}",
                            message=f"Score {current_score.final_score:.2f} is {direction} threshold {threshold}",
                            data={
                                'score': current_score.final_score,
                                'threshold': threshold,
                                'direction': direction
                            },
                            timestamp=datetime.now()
                        )
                        
                        if not self._is_duplicate_alert(stock_symbol, AlertType.THRESHOLD_BREACH, alert.message):
                            await self._create_alert(alert, rule)
    
    async def check_risk_alerts(self, current_score, stock_symbol: str):
        """Check for risk-based alerts"""
        for rule in self.alert_rules:
            if (rule.alert_type == AlertType.RISK_ALERT and 
                rule.enabled and 
                not self._check_rule_cooldown(rule, stock_symbol)):
                
                conditions = rule.conditions
                risk_threshold = conditions.get('risk_threshold', 0.7)
                min_confidence = conditions.get('min_confidence', 0.5)
                
                if (current_score.risk_score >= risk_threshold and 
                    current_score.confidence >= min_confidence):
                    
                    risk_level = current_score.components['risk']['level']
                    
                    alert = Alert(
                        id=self._generate_alert_id(stock_symbol, AlertType.RISK_ALERT),
                        alert_type=AlertType.RISK_ALERT,
                        priority=rule.priority,
                        stock_symbol=stock_symbol,
                        title=f"High Risk Alert - {stock_symbol}",
                        message=f"Risk level: {risk_level} (Score: {current_score.risk_score:.2f})",
                        data={
                            'risk_score': current_score.risk_score,
                            'risk_level': risk_level,
                            'confidence': current_score.confidence
                        },
                        timestamp=datetime.now()
                    )
                    
                    if not self._is_duplicate_alert(stock_symbol, AlertType.RISK_ALERT, alert.message):
                        await self._create_alert(alert, rule)
    
    async def check_pattern_alerts(self, current_score, stock_symbol: str):
        """Check for pattern-based alerts"""
        patterns = current_score.components.get('technical', {}).get('patterns', [])
        
        for pattern in patterns:
            for rule in self.alert_rules:
                if (rule.alert_type == AlertType.PATTERN_DETECTED and 
                    rule.enabled and 
                    not self._check_rule_cooldown(rule, stock_symbol)):
                    
                    conditions = rule.conditions
                    target_signal = conditions.get('pattern_signal')
                    min_confidence = conditions.get('min_confidence', 0.6)
                    
                    pattern_signal = pattern.get('signal')
                    pattern_confidence = pattern.get('confidence', 0)
                    
                    if (pattern_signal == target_signal and 
                        pattern_confidence >= min_confidence):
                        
                        alert = Alert(
                            id=self._generate_alert_id(stock_symbol, AlertType.PATTERN_DETECTED),
                            alert_type=AlertType.PATTERN_DETECTED,
                            priority=rule.priority,
                            stock_symbol=stock_symbol,
                            title=f"Pattern Detected - {stock_symbol}",
                            message=f"{pattern_signal.title()} pattern: {pattern.get('name', 'Unknown')}",
                            data={
                                'pattern_name': pattern.get('name'),
                                'pattern_signal': pattern_signal,
                                'confidence': pattern_confidence,
                                'description': pattern.get('description', '')
                            },
                            timestamp=datetime.now()
                        )
                        
                        if not self._is_duplicate_alert(stock_symbol, AlertType.PATTERN_DETECTED, alert.message):
                            await self._create_alert(alert, rule)
    
    async def _create_alert(self, alert: Alert, rule: AlertRule):
        """Create and process new alert"""
        self.alerts.append(alert)
        self.alert_history.append(alert)
        
        # Update rule last triggered time
        rule.last_triggered = datetime.now()
        
        # Notify subscribers
        await self.notify_subscribers(alert)
        
        # Mark as sent
        alert.sent = True
    
    async def process_score_update(self, current_score, previous_score, stock_symbol: str):
        """Process all alert checks for a score update"""
        await asyncio.gather(
            self.check_score_alerts(current_score, previous_score, stock_symbol),
            self.check_recommendation_alerts(current_score, previous_score, stock_symbol),
            self.check_threshold_alerts(current_score, stock_symbol),
            self.check_risk_alerts(current_score, stock_symbol),
            self.check_pattern_alerts(current_score, stock_symbol)
        )
    
    def get_active_alerts(self, stock_symbol: str = None) -> List[Alert]:
        """Get active alerts, optionally filtered by stock"""
        now = datetime.now()
        active = [a for a in self.alerts 
                 if not a.acknowledged and 
                 (not a.expires_at or a.expires_at > now)]
        
        if stock_symbol:
            active = [a for a in active if a.stock_symbol == stock_symbol]
        
        return sorted(active, key=lambda x: (x.priority.value, x.timestamp), reverse=True)
    
    def acknowledge_alert(self, alert_id: str):
        """Acknowledge an alert"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                break
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get alert statistics"""
        now = datetime.now()
        last_24h = now - timedelta(hours=24)
        
        recent_alerts = [a for a in self.alert_history if a.timestamp >= last_24h]
        
        stats = {
            'total_alerts_24h': len(recent_alerts),
            'active_alerts': len(self.get_active_alerts()),
            'alerts_by_type': {},
            'alerts_by_priority': {},
            'top_stocks': {}
        }
        
        # Count by type
        for alert in recent_alerts:
            alert_type = alert.alert_type.value
            stats['alerts_by_type'][alert_type] = stats['alerts_by_type'].get(alert_type, 0) + 1
        
        # Count by priority
        for alert in recent_alerts:
            priority = alert.priority.value
            stats['alerts_by_priority'][priority] = stats['alerts_by_priority'].get(priority, 0) + 1
        
        # Count by stock
        for alert in recent_alerts:
            symbol = alert.stock_symbol
            stats['top_stocks'][symbol] = stats['top_stocks'].get(symbol, 0) + 1
        
        # Sort top stocks
        stats['top_stocks'] = dict(sorted(stats['top_stocks'].items(), 
                                        key=lambda x: x[1], reverse=True)[:10])
        
        return stats
    
    def cleanup_old_alerts(self, days: int = 7):
        """Clean up old alerts"""
        cutoff = datetime.now() - timedelta(days=days)
        self.alert_history = [a for a in self.alert_history if a.timestamp >= cutoff]
        self.alerts = [a for a in self.alerts if a.timestamp >= cutoff]