import json
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from .news_analyzer import NewsAnalysisResult

@dataclass
class QualityMetrics:
    completeness_score: float
    consistency_score: float
    confidence_score: float
    format_score: float
    overall_score: float
    issues: List[str]

@dataclass
class ValidationResult:
    is_valid: bool
    quality_metrics: QualityMetrics
    corrected_result: Optional[Dict[str, Any]]
    validation_notes: List[str]

class QualityController:
    """Quality control and validation for LLM analysis results"""
    
    def __init__(self):
        self.min_overall_score = 0.6
        self.required_fields = {
            'sentiment': ['sentiment', 'confidence', 'drivers'],
            'summary': ['summary', 'key_points', 'relevance_score'],
            'insights': ['business_impact', 'investment_thesis', 'catalysts', 'risks'],
            'market_impact': ['sector_impact', 'impact_magnitude', 'affected_stocks']
        }
        
        self.valid_values = {
            'sentiment': ['POSITIVE', 'NEGATIVE', 'NEUTRAL'],
            'impact_magnitude': ['HIGH', 'MEDIUM', 'LOW'],
            'investor_action': ['BUY', 'SELL', 'HOLD', 'WATCH'],
            'urgency': ['HIGH', 'MEDIUM', 'LOW'],
            'risk_level': ['HIGH', 'MEDIUM', 'LOW']
        }
    
    def validate_analysis_result(self, result: NewsAnalysisResult) -> ValidationResult:
        """Comprehensive validation of analysis result"""
        issues = []
        
        # Check completeness
        completeness_score = self._check_completeness(result, issues)
        
        # Check consistency
        consistency_score = self._check_consistency(result, issues)
        
        # Check confidence
        confidence_score = self._check_confidence(result, issues)
        
        # Check format
        format_score = self._check_format(result, issues)
        
        # Calculate overall score
        overall_score = (completeness_score + consistency_score + 
                        confidence_score + format_score) / 4
        
        quality_metrics = QualityMetrics(
            completeness_score=completeness_score,
            consistency_score=consistency_score,
            confidence_score=confidence_score,
            format_score=format_score,
            overall_score=overall_score,
            issues=issues
        )
        
        # Attempt correction if needed
        corrected_result = None
        validation_notes = []
        
        if overall_score < self.min_overall_score:
            corrected_result, correction_notes = self._attempt_correction(result)
            validation_notes.extend(correction_notes)
        
        return ValidationResult(
            is_valid=overall_score >= self.min_overall_score,
            quality_metrics=quality_metrics,
            corrected_result=corrected_result,
            validation_notes=validation_notes
        )
    
    def _check_completeness(self, result: NewsAnalysisResult, issues: List[str]) -> float:
        """Check if all required fields are present"""
        analysis_type = result.analysis_type
        required = self.required_fields.get(analysis_type, [])
        
        if not required:
            return 1.0
        
        present_fields = 0
        total_fields = len(required)
        
        for field in required:
            if field in result.result and result.result[field] is not None:
                if isinstance(result.result[field], str) and result.result[field].strip():
                    present_fields += 1
                elif isinstance(result.result[field], list) and result.result[field]:
                    present_fields += 1
                elif isinstance(result.result[field], (int, float)):
                    present_fields += 1
            else:
                issues.append(f"Missing required field: {field}")
        
        return present_fields / total_fields if total_fields > 0 else 1.0
    
    def _check_consistency(self, result: NewsAnalysisResult, issues: List[str]) -> float:
        """Check internal consistency of the result"""
        score = 1.0
        
        if result.analysis_type == 'sentiment':
            # Check sentiment-confidence consistency
            sentiment = result.result.get('sentiment', '').upper()
            confidence = result.result.get('confidence', 0)
            
            if sentiment in ['POSITIVE', 'NEGATIVE'] and confidence < 60:
                issues.append("Low confidence for strong sentiment")
                score -= 0.2
            
            # Check drivers consistency with sentiment
            drivers = result.result.get('drivers', [])
            if sentiment == 'POSITIVE' and any('negative' in str(d).lower() for d in drivers):
                issues.append("Negative drivers for positive sentiment")
                score -= 0.3
            elif sentiment == 'NEGATIVE' and any('positive' in str(d).lower() for d in drivers):
                issues.append("Positive drivers for negative sentiment")
                score -= 0.3
        
        elif result.analysis_type == 'summary':
            # Check relevance score consistency
            relevance = result.result.get('relevance_score', 0)
            urgency = result.result.get('urgency', '').upper()
            
            if relevance >= 8 and urgency == 'LOW':
                issues.append("High relevance but low urgency")
                score -= 0.2
        
        return max(0.0, score)
    
    def _check_confidence(self, result: NewsAnalysisResult, issues: List[str]) -> float:
        """Check confidence levels and thresholds"""
        confidence = result.confidence
        
        if confidence < 0.3:
            issues.append("Very low confidence score")
            return 0.2
        elif confidence < 0.5:
            issues.append("Low confidence score")
            return 0.5
        elif confidence < 0.7:
            return 0.7
        else:
            return 1.0
    
    def _check_format(self, result: NewsAnalysisResult, issues: List[str]) -> float:
        """Check format and data types"""
        score = 1.0
        
        # Check for valid enum values
        for field, valid_values in self.valid_values.items():
            if field in result.result:
                value = str(result.result[field]).upper()
                if value not in valid_values:
                    issues.append(f"Invalid value for {field}: {value}")
                    score -= 0.2
        
        # Check numeric ranges
        if 'confidence' in result.result:
            conf = result.result['confidence']
            if not isinstance(conf, (int, float)) or conf < 0 or conf > 100:
                issues.append("Confidence must be between 0-100")
                score -= 0.3
        
        if 'relevance_score' in result.result:
            rel = result.result['relevance_score']
            if not isinstance(rel, (int, float)) or rel < 1 or rel > 10:
                issues.append("Relevance score must be between 1-10")
                score -= 0.3
        
        # Check list fields
        list_fields = ['drivers', 'key_points', 'catalysts', 'risks', 'affected_stocks']
        for field in list_fields:
            if field in result.result:
                if not isinstance(result.result[field], list):
                    issues.append(f"{field} should be a list")
                    score -= 0.2
                elif len(result.result[field]) == 0:
                    issues.append(f"{field} list is empty")
                    score -= 0.1
        
        return max(0.0, score)
    
    def _attempt_correction(self, result: NewsAnalysisResult) -> Tuple[Optional[Dict], List[str]]:
        """Attempt to correct common issues"""
        corrected = result.result.copy()
        notes = []
        
        # Fix sentiment values
        if 'sentiment' in corrected:
            sentiment = str(corrected['sentiment']).upper()
            if sentiment not in self.valid_values['sentiment']:
                # Try to map common variations
                if 'pos' in sentiment.lower() or 'good' in sentiment.lower():
                    corrected['sentiment'] = 'POSITIVE'
                    notes.append("Corrected sentiment to POSITIVE")
                elif 'neg' in sentiment.lower() or 'bad' in sentiment.lower():
                    corrected['sentiment'] = 'NEGATIVE'
                    notes.append("Corrected sentiment to NEGATIVE")
                else:
                    corrected['sentiment'] = 'NEUTRAL'
                    notes.append("Defaulted sentiment to NEUTRAL")
        
        # Fix confidence range
        if 'confidence' in corrected:
            conf = corrected['confidence']
            if isinstance(conf, (int, float)):
                if conf > 1 and conf <= 100:
                    # Already in 0-100 range
                    pass
                elif conf <= 1:
                    # Convert from 0-1 to 0-100
                    corrected['confidence'] = int(conf * 100)
                    notes.append("Converted confidence to 0-100 scale")
                else:
                    # Cap at 100
                    corrected['confidence'] = 100
                    notes.append("Capped confidence at 100")
        
        # Fix empty lists
        list_fields = ['drivers', 'key_points', 'catalysts', 'risks']
        for field in list_fields:
            if field in corrected and not corrected[field]:
                corrected[field] = ["Information not available"]
                notes.append(f"Added placeholder for empty {field}")
        
        # Fix missing required fields
        analysis_type = result.analysis_type
        required = self.required_fields.get(analysis_type, [])
        
        for field in required:
            if field not in corrected or not corrected[field]:
                if field == 'sentiment':
                    corrected[field] = 'NEUTRAL'
                elif field == 'confidence':
                    corrected[field] = 50
                elif field in ['drivers', 'key_points', 'catalysts', 'risks']:
                    corrected[field] = ["Information not available"]
                elif field in ['summary', 'business_impact', 'investment_thesis']:
                    corrected[field] = "Analysis not available"
                elif field == 'relevance_score':
                    corrected[field] = 5
                
                notes.append(f"Added default value for missing {field}")
        
        return corrected if notes else None, notes
    
    def batch_validate(self, results: List[NewsAnalysisResult]) -> Dict[str, Any]:
        """Validate a batch of results and provide summary statistics"""
        validations = [self.validate_analysis_result(result) for result in results]
        
        valid_count = sum(1 for v in validations if v.is_valid)
        total_count = len(validations)
        
        # Calculate average scores
        avg_scores = {
            'completeness': sum(v.quality_metrics.completeness_score for v in validations) / total_count,
            'consistency': sum(v.quality_metrics.consistency_score for v in validations) / total_count,
            'confidence': sum(v.quality_metrics.confidence_score for v in validations) / total_count,
            'format': sum(v.quality_metrics.format_score for v in validations) / total_count,
            'overall': sum(v.quality_metrics.overall_score for v in validations) / total_count
        }
        
        # Collect common issues
        all_issues = []
        for v in validations:
            all_issues.extend(v.quality_metrics.issues)
        
        issue_counts = {}
        for issue in all_issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1
        
        return {
            'total_analyzed': total_count,
            'valid_results': valid_count,
            'invalid_results': total_count - valid_count,
            'validation_rate': valid_count / total_count if total_count > 0 else 0,
            'average_scores': avg_scores,
            'common_issues': sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:10],
            'validations': validations
        }