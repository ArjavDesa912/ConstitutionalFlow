import structlog
import time
import functools
from typing import Any, Callable
from src.core.config import settings

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

def log_execution_time(func: Callable) -> Callable:
    """Decorator to log function execution time"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(
                "Function executed successfully",
                function_name=func.__name__,
                execution_time=execution_time
            )
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                "Function execution failed",
                function_name=func.__name__,
                execution_time=execution_time,
                error=str(e)
            )
            raise
    return wrapper

def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Decorator to retry function on failure"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(
                            "Function failed, retrying",
                            function_name=func.__name__,
                            attempt=attempt + 1,
                            max_retries=max_retries,
                            error=str(e)
                        )
                        time.sleep(delay * (2 ** attempt))  # Exponential backoff
                    else:
                        logger.error(
                            "Function failed after all retries",
                            function_name=func.__name__,
                            max_retries=max_retries,
                            error=str(e)
                        )
            raise last_exception
        return wrapper
    return decorator

def validate_api_response(response: dict, required_fields: list) -> bool:
    """Validate API response structure"""
    if not isinstance(response, dict):
        return False
    
    for field in required_fields:
        if field not in response:
            return False
    
    return True

def sanitize_text(text: str) -> str:
    """Sanitize text input"""
    if not text:
        return ""
    
    # Remove potentially dangerous characters
    dangerous_chars = ['<script>', '</script>', 'javascript:', 'data:']
    sanitized = text
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')
    
    return sanitized.strip()

def calculate_complexity_score(text: str) -> float:
    """Calculate text complexity score (0-1)"""
    if not text:
        return 0.0
    
    # Simple complexity calculation based on:
    # - Text length
    # - Average word length
    # - Number of sentences
    # - Presence of technical terms
    
    words = text.split()
    sentences = text.split('.')
    
    if not words:
        return 0.0
    
    avg_word_length = sum(len(word) for word in words) / len(words)
    num_sentences = len([s for s in sentences if s.strip()])
    
    # Normalize factors
    length_factor = min(len(text) / 1000, 1.0)  # Normalize to 1000 chars
    word_length_factor = min(avg_word_length / 10, 1.0)  # Normalize to 10 chars
    sentence_factor = min(num_sentences / 10, 1.0)  # Normalize to 10 sentences
    
    # Weighted average
    complexity = (length_factor * 0.3 + word_length_factor * 0.4 + sentence_factor * 0.3)
    
    return min(complexity, 1.0)

def generate_task_id() -> str:
    """Generate unique task ID"""
    import uuid
    return f"task_{uuid.uuid4().hex[:8]}"

def format_error_response(error: str, details: Any = None) -> dict:
    """Format error response for API"""
    response = {
        "error": error,
        "timestamp": time.time()
    }
    if details:
        response["details"] = details
    return response 