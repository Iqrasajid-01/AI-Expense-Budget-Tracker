"""
Optimized ML Service with Caching
Provides fast ML predictions with result caching
"""
import sys
import os
from functools import lru_cache
import hashlib

# Add the parent directory to the path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from ..ml_models.ultra_high_accuracy_categorizer import UltraHighAccuracyCategorizer
except ImportError:
    try:
        from ml_models.ultra_high_accuracy_categorizer import UltraHighAccuracyCategorizer
    except ImportError:
        from backend.ml_models.ultra_high_accuracy_categorizer import UltraHighAccuracyCategorizer

from typing import Tuple, Dict, Any
from datetime import datetime
import time

# Simple cache for predictions (in-memory, LRU)
_prediction_cache = {}
CACHE_SIZE = 1000
CACHE_TTL = 3600  # Cache predictions for 1 hour


class MLService:
    """
    Optimized ML service with caching for fast predictions
    """
    
    _instance = None  # Singleton pattern
    
    def __new__(cls):
        """Singleton - only one ML service instance"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.expense_categorizer = UltraHighAccuracyCategorizer()
        self.model_loaded = False
        self._initialized = True
        self._cache_hits = 0
        self._cache_misses = 0

        # Load model once
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        model_path = os.path.join(base_dir, 'ml_models', 'trained_models', 'ultra_high_accuracy_categorizer.pkl')
        
        if os.path.exists(model_path):
            try:
                self.expense_categorizer.load_model(model_path)
                self.model_loaded = True
            except Exception as e:
                print(f"Could not load model: {e}")
                self.model_loaded = False

    def _get_cache_key(self, description: str) -> str:
        """Generate cache key for description"""
        return hashlib.md5(description.lower().strip().encode()).hexdigest()

    def _clean_cache(self):
        """Remove expired cache entries"""
        now = time.time()
        expired_keys = [
            k for k, (t, _) in _prediction_cache.items()
            if now - t > CACHE_TTL
        ]
        for k in expired_keys:
            del _prediction_cache[k]

    def categorize_transaction(self, description: str) -> Tuple[str, float]:
        """
        Categorize transaction with caching for speed
        Returns (category, confidence_score)
        """
        # Clean old cache entries periodically
        if len(_prediction_cache) > CACHE_SIZE:
            self._clean_cache()
        
        # Check cache first (very fast)
        cache_key = self._get_cache_key(description)
        if cache_key in _prediction_cache:
            self._cache_hits += 1
            timestamp, result = _prediction_cache[cache_key]
            if time.time() - timestamp < CACHE_TTL:
                return result
        
        # Cache miss - compute prediction
        self._cache_misses += 1
        
        if not self.model_loaded or not self.expense_categorizer.is_trained:
            result = ("Unknown", 0.0)
        else:
            try:
                result = self.expense_categorizer.predict(description)
            except Exception as e:
                print(f"ML prediction error: {e}")
                result = ("Unknown", 0.0)
        
        # Store in cache
        _prediction_cache[cache_key] = (time.time(), result)
        
        return result

    def get_available_categories(self) -> list:
        """Get list of available categories"""
        return self.expense_categorizer.get_available_categories()

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total = self._cache_hits + self._cache_misses
        hit_rate = (self._cache_hits / total * 100) if total > 0 else 0
        return {
            'cache_size': len(_prediction_cache),
            'hits': self._cache_hits,
            'misses': self._cache_misses,
            'hit_rate': f"{hit_rate:.1f}%"
        }

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the model"""
        return {
            "model_loaded": self.model_loaded,
            "categories": self.get_available_categories(),
            "cache_stats": self.get_cache_stats(),
            "last_updated": datetime.now().isoformat()
        }


# Pre-instantiate for faster first access
_ml_service_instance = None

def get_ml_service():
    """Get ML service instance (fast singleton access)"""
    global _ml_service_instance
    if _ml_service_instance is None:
        _ml_service_instance = MLService()
    return _ml_service_instance
