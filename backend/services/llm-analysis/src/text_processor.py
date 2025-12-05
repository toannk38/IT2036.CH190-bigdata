import re
import unicodedata
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import langdetect
from langdetect.lang_detect_exception import LangDetectException

@dataclass
class TextChunk:
    content: str
    start_pos: int
    end_pos: int
    word_count: int
    quality_score: float

@dataclass
class ProcessedText:
    original: str
    cleaned: str
    chunks: List[TextChunk]
    language: str
    quality_score: float
    metadata: Dict[str, Any]

class TextProcessor:
    """Text preprocessing and quality assessment for LLM analysis"""
    
    def __init__(self):
        self.max_chunk_size = 2000  # characters
        self.min_chunk_size = 100
        self.overlap_size = 200
        
        # Vietnamese text patterns
        self.vietnamese_patterns = {
            'currency': re.compile(r'(\d+(?:\.\d+)?)\s*(VND|đồng|triệu|tỷ)', re.IGNORECASE),
            'percentage': re.compile(r'(\d+(?:\.\d+)?)\s*%'),
            'stock_codes': re.compile(r'\b[A-Z]{3}\b'),
            'dates': re.compile(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}'),
            'phone_numbers': re.compile(r'(\+84|0)\d{9,10}'),
            'emails': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        }
        
        # Quality indicators
        self.quality_indicators = {
            'min_length': 50,
            'max_length': 10000,
            'min_sentences': 2,
            'financial_keywords': [
                'doanh thu', 'lợi nhuận', 'tăng trưởng', 'đầu tư', 'cổ phiếu',
                'thị trường', 'kinh doanh', 'tài chính', 'ngân hàng', 'bất động sản'
            ]
        }
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize Vietnamese text"""
        if not text:
            return ""
        
        # Normalize Unicode characters
        text = unicodedata.normalize('NFC', text)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep Vietnamese diacritics
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}\"\'àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]', ' ', text)
        
        # Fix common OCR errors in Vietnamese
        replacements = {
            'đươc': 'được',
            'thươc': 'thuộc',
            'môt': 'một',
            'cua': 'của',
            'thi': 'thì'
        }
        
        for wrong, correct in replacements.items():
            text = re.sub(r'\b' + wrong + r'\b', correct, text, flags=re.IGNORECASE)
        
        # Remove extra spaces and trim
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def detect_language(self, text: str) -> str:
        """Detect text language"""
        try:
            return langdetect.detect(text)
        except LangDetectException:
            # Fallback: check for Vietnamese characters
            vietnamese_chars = 'àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ'
            if any(char in text.lower() for char in vietnamese_chars):
                return 'vi'
            return 'unknown'
    
    def calculate_quality_score(self, text: str) -> float:
        """Calculate text quality score (0-1)"""
        if not text:
            return 0.0
        
        score = 0.0
        factors = []
        
        # Length check
        length = len(text)
        if self.quality_indicators['min_length'] <= length <= self.quality_indicators['max_length']:
            length_score = 1.0
        elif length < self.quality_indicators['min_length']:
            length_score = length / self.quality_indicators['min_length']
        else:
            length_score = max(0.5, 1.0 - (length - self.quality_indicators['max_length']) / 10000)
        
        factors.append(('length', length_score, 0.2))
        
        # Sentence structure
        sentences = re.split(r'[.!?]+', text)
        sentence_count = len([s for s in sentences if len(s.strip()) > 10])
        sentence_score = min(1.0, sentence_count / self.quality_indicators['min_sentences'])
        factors.append(('sentences', sentence_score, 0.15))
        
        # Financial keyword presence
        keyword_count = sum(1 for keyword in self.quality_indicators['financial_keywords'] 
                          if keyword in text.lower())
        keyword_score = min(1.0, keyword_count / 3)
        factors.append(('keywords', keyword_score, 0.25))
        
        # Text coherence (basic check)
        words = text.split()
        unique_words = set(words)
        coherence_score = len(unique_words) / len(words) if words else 0
        coherence_score = min(1.0, coherence_score * 2)  # Normalize
        factors.append(('coherence', coherence_score, 0.2))
        
        # Special characters ratio
        special_chars = len(re.findall(r'[^\w\s]', text))
        special_ratio = special_chars / len(text) if text else 0
        special_score = max(0, 1.0 - special_ratio * 5)  # Penalize too many special chars
        factors.append(('special_chars', special_score, 0.1))
        
        # Vietnamese language bonus
        language = self.detect_language(text)
        language_score = 1.0 if language == 'vi' else 0.7
        factors.append(('language', language_score, 0.1))
        
        # Calculate weighted score
        total_weight = sum(weight for _, _, weight in factors)
        score = sum(score * weight for _, score, weight in factors) / total_weight
        
        return round(score, 3)
    
    def chunk_text(self, text: str) -> List[TextChunk]:
        """Split text into overlapping chunks for processing"""
        if len(text) <= self.max_chunk_size:
            return [TextChunk(
                content=text,
                start_pos=0,
                end_pos=len(text),
                word_count=len(text.split()),
                quality_score=self.calculate_quality_score(text)
            )]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = min(start + self.max_chunk_size, len(text))
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence ending within last 200 characters
                search_start = max(end - 200, start)
                sentence_end = -1
                
                for i in range(end - 1, search_start - 1, -1):
                    if text[i] in '.!?':
                        sentence_end = i + 1
                        break
                
                if sentence_end > start:
                    end = sentence_end
            
            chunk_text = text[start:end].strip()
            
            if len(chunk_text) >= self.min_chunk_size:
                chunks.append(TextChunk(
                    content=chunk_text,
                    start_pos=start,
                    end_pos=end,
                    word_count=len(chunk_text.split()),
                    quality_score=self.calculate_quality_score(chunk_text)
                ))
            
            # Move start position with overlap
            start = max(start + 1, end - self.overlap_size)
            
            if start >= len(text):
                break
        
        return chunks
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract financial entities from Vietnamese text"""
        entities = {}
        
        # Extract currency amounts
        currency_matches = self.vietnamese_patterns['currency'].findall(text)
        entities['currency'] = [f"{amount} {unit}" for amount, unit in currency_matches]
        
        # Extract percentages
        percentage_matches = self.vietnamese_patterns['percentage'].findall(text)
        entities['percentages'] = [f"{pct}%" for pct in percentage_matches]
        
        # Extract stock codes
        stock_matches = self.vietnamese_patterns['stock_codes'].findall(text)
        entities['stock_codes'] = list(set(stock_matches))
        
        # Extract dates
        date_matches = self.vietnamese_patterns['dates'].findall(text)
        entities['dates'] = list(set(date_matches))
        
        return entities
    
    def process_text(self, text: str) -> ProcessedText:
        """Complete text processing pipeline"""
        if not text:
            return ProcessedText(
                original="",
                cleaned="",
                chunks=[],
                language="unknown",
                quality_score=0.0,
                metadata={}
            )
        
        # Clean text
        cleaned_text = self.clean_text(text)
        
        # Detect language
        language = self.detect_language(cleaned_text)
        
        # Calculate quality score
        quality_score = self.calculate_quality_score(cleaned_text)
        
        # Create chunks
        chunks = self.chunk_text(cleaned_text)
        
        # Extract entities
        entities = self.extract_entities(cleaned_text)
        
        # Compile metadata
        metadata = {
            'original_length': len(text),
            'cleaned_length': len(cleaned_text),
            'chunk_count': len(chunks),
            'entities': entities,
            'avg_chunk_quality': sum(chunk.quality_score for chunk in chunks) / len(chunks) if chunks else 0,
            'processing_timestamp': None  # Will be set by caller
        }
        
        return ProcessedText(
            original=text,
            cleaned=cleaned_text,
            chunks=chunks,
            language=language,
            quality_score=quality_score,
            metadata=metadata
        )