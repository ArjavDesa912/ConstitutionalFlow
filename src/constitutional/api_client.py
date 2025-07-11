import openai
import anthropic
import cohere
import httpx
import asyncio
import time
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
from src.core.config import settings
from src.core.cache import cache
from src.core.utils import logger, retry_on_failure, validate_api_response

class BaseAPIClient(ABC):
    """Base class for API clients"""
    
    def __init__(self, api_key: str, rate_limit: int):
        self.api_key = api_key
        self.rate_limit = rate_limit
        self.request_count = 0
        self.last_request_time = 0
    
    @abstractmethod
    async def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate response from the API"""
        pass
    
    def _check_rate_limit(self):
        """Check and enforce rate limiting"""
        current_time = time.time()
        if current_time - self.last_request_time < 1.0 / self.rate_limit:
            sleep_time = 1.0 / self.rate_limit - (current_time - self.last_request_time)
            time.sleep(sleep_time)
        self.last_request_time = time.time()
        self.request_count += 1

class OpenAIClient(BaseAPIClient):
    """OpenAI API client"""
    
    def __init__(self):
        super().__init__(settings.OPENAI_API_KEY, settings.OPENAI_RATE_LIMIT)
        self.client = openai.AsyncOpenAI(api_key=self.api_key)
    
    @retry_on_failure(max_retries=3)
    async def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate response using OpenAI API"""
        self._check_rate_limit()
        
        try:
            response = await self.client.chat.completions.create(
                model=kwargs.get('model', 'gpt-4'),
                messages=[{"role": "user", "content": prompt}],
                max_tokens=kwargs.get('max_tokens', 1000),
                temperature=kwargs.get('temperature', 0.7)
            )
            
            return {
                'provider': 'openai',
                'content': response.choices[0].message.content,
                'model': response.model,
                'usage': response.usage.dict() if response.usage else None,
                'success': True
            }
        except Exception as e:
            logger.error("OpenAI API error", error=str(e))
            return {
                'provider': 'openai',
                'content': None,
                'error': str(e),
                'success': False
            }

class AnthropicClient(BaseAPIClient):
    """Anthropic API client"""
    
    def __init__(self):
        super().__init__(settings.ANTHROPIC_API_KEY, settings.ANTHROPIC_RATE_LIMIT)
        self.client = anthropic.AsyncAnthropic(api_key=self.api_key)
    
    @retry_on_failure(max_retries=3)
    async def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate response using Anthropic API"""
        self._check_rate_limit()
        
        try:
            response = await self.client.messages.create(
                model=kwargs.get('model', 'claude-3-sonnet-20240229'),
                max_tokens=kwargs.get('max_tokens', 1000),
                temperature=kwargs.get('temperature', 0.7),
                messages=[{"role": "user", "content": prompt}]
            )
            
            return {
                'provider': 'anthropic',
                'content': response.content[0].text,
                'model': response.model,
                'usage': response.usage.dict() if response.usage else None,
                'success': True
            }
        except Exception as e:
            logger.error("Anthropic API error", error=str(e))
            return {
                'provider': 'anthropic',
                'content': None,
                'error': str(e),
                'success': False
            }

class CohereClient(BaseAPIClient):
    """Cohere API client"""
    
    def __init__(self):
        super().__init__(settings.COHERE_API_KEY, settings.COHERE_RATE_LIMIT)
        self.client = cohere.AsyncClient(api_key=self.api_key)
    
    @retry_on_failure(max_retries=3)
    async def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate response using Cohere API"""
        self._check_rate_limit()
        
        try:
            response = await self.client.generate(
                model=kwargs.get('model', 'command'),
                prompt=prompt,
                max_tokens=kwargs.get('max_tokens', 1000),
                temperature=kwargs.get('temperature', 0.7)
            )
            
            return {
                'provider': 'cohere',
                'content': response.generations[0].text,
                'model': response.model,
                'usage': response.meta.dict() if response.meta else None,
                'success': True
            }
        except Exception as e:
            logger.error("Cohere API error", error=str(e))
            return {
                'provider': 'cohere',
                'content': None,
                'error': str(e),
                'success': False
            }

class MultiModelClient:
    """Main orchestrator for multiple API clients"""
    
    def __init__(self):
        self.clients = {}
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize available API clients"""
        if settings.OPENAI_API_KEY:
            self.clients['openai'] = OpenAIClient()
        
        if settings.ANTHROPIC_API_KEY:
            self.clients['anthropic'] = AnthropicClient()
        
        if settings.COHERE_API_KEY:
            self.clients['cohere'] = CohereClient()
    
    async def generate_response(self, prompt: str, providers: List[str] = None, **kwargs) -> Dict[str, Any]:
        """Generate response using specified providers with failover"""
        if not providers:
            providers = list(self.clients.keys())
        
        # Check cache first
        cache_key = f"api_response:{hash(prompt)}:{','.join(providers)}"
        cached_response = cache.get(cache_key)
        if cached_response:
            logger.info("Using cached API response")
            return cached_response
        
        # Try each provider in order
        for provider in providers:
            if provider not in self.clients:
                continue
            
            try:
                response = await self.clients[provider].generate_response(prompt, **kwargs)
                if response['success']:
                    # Cache successful response
                    cache.set(cache_key, response, expire=3600)
                    return response
            except Exception as e:
                logger.warning(f"Provider {provider} failed", error=str(e))
                continue
        
        # All providers failed
        return {
            'provider': 'none',
            'content': None,
            'error': 'All API providers failed',
            'success': False
        }
    
    async def generate_consensus(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate consensus from multiple providers"""
        responses = []
        
        # Get responses from all available providers
        for provider in self.clients.keys():
            try:
                response = await self.clients[provider].generate_response(prompt, **kwargs)
                if response['success']:
                    responses.append(response)
            except Exception as e:
                logger.warning(f"Provider {provider} failed in consensus", error=str(e))
        
        if not responses:
            return {
                'consensus': None,
                'responses': [],
                'confidence': 0.0,
                'success': False
            }
        
        # Calculate consensus
        contents = [r['content'] for r in responses if r['success']]
        consensus = self._calculate_consensus(contents)
        confidence = len(contents) / len(self.clients) if self.clients else 0.0
        
        return {
            'consensus': consensus,
            'responses': responses,
            'confidence': confidence,
            'success': True
        }
    
    def _calculate_consensus(self, contents: List[str]) -> str:
        """Calculate consensus from multiple responses"""
        if not contents:
            return ""
        
        if len(contents) == 1:
            return contents[0]
        
        # Simple consensus: return the most common response
        # In a more sophisticated implementation, you could use semantic similarity
        content_counts = {}
        for content in contents:
            content_counts[content] = content_counts.get(content, 0) + 1
        
        return max(content_counts.items(), key=lambda x: x[1])[0]

# Global client instance
multi_model_client = MultiModelClient() 