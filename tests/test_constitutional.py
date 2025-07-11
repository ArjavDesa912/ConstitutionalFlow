import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.constitutional.api_client import OpenAIClient, AnthropicClient, CohereClient, MultiModelClient
from src.constitutional.evolution_engine import ConstitutionalEvolutionEngine
from src.constitutional.consensus_manager import ConsensusManager

class TestOpenAIClient:
    """Test OpenAI client functionality."""
    
    @pytest.fixture
    def client(self):
        return OpenAIClient(api_key="test-key")
    
    @pytest.mark.asyncio
    async def test_generate_response_success(self, client):
        """Test successful response generation."""
        with patch('openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            mock_client.chat.completions.create.return_value = Mock(
                choices=[Mock(message=Mock(content="Test response"))],
                usage=Mock(total_tokens=100)
            )
            
            result = await client.generate_response("Test prompt")
            
            assert result["success"] is True
            assert "Test response" in result["response"]
            assert result["tokens_used"] == 100
    
    @pytest.mark.asyncio
    async def test_generate_response_error(self, client):
        """Test error handling in response generation."""
        with patch('openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            mock_client.chat.completions.create.side_effect = Exception("API Error")
            
            result = await client.generate_response("Test prompt")
            
            assert result["success"] is False
            assert "API Error" in result["error"]

class TestAnthropicClient:
    """Test Anthropic client functionality."""
    
    @pytest.fixture
    def client(self):
        return AnthropicClient(api_key="test-key")
    
    @pytest.mark.asyncio
    async def test_generate_response_success(self, client):
        """Test successful response generation."""
        with patch('anthropic.Anthropic') as mock_anthropic:
            mock_client = Mock()
            mock_anthropic.return_value = mock_client
            mock_client.messages.create.return_value = Mock(
                content=[Mock(text="Test response")],
                usage=Mock(input_tokens=50, output_tokens=50)
            )
            
            result = await client.generate_response("Test prompt")
            
            assert result["success"] is True
            assert "Test response" in result["response"]
            assert result["tokens_used"] == 100

class TestCohereClient:
    """Test Cohere client functionality."""
    
    @pytest.fixture
    def client(self):
        return CohereClient(api_key="test-key")
    
    @pytest.mark.asyncio
    async def test_generate_response_success(self, client):
        """Test successful response generation."""
        with patch('cohere.Client') as mock_cohere:
            mock_client = Mock()
            mock_cohere.return_value = mock_client
            mock_client.generate.return_value = Mock(
                generations=[Mock(text="Test response")],
                meta=Mock(billed_units=Mock(input_tokens=50, output_tokens=50))
            )
            
            result = await client.generate_response("Test prompt")
            
            assert result["success"] is True
            assert "Test response" in result["response"]
            assert result["tokens_used"] == 100

class TestMultiModelClient:
    """Test multi-model client functionality."""
    
    @pytest.fixture
    def client(self):
        return MultiModelClient()
    
    @pytest.mark.asyncio
    async def test_generate_consensus_success(self, client):
        """Test successful consensus generation."""
        with patch.object(client, 'openai_client') as mock_openai, \
             patch.object(client, 'anthropic_client') as mock_anthropic, \
             patch.object(client, 'cohere_client') as mock_cohere:
            
            mock_openai.generate_response.return_value = {
                "success": True, "response": "OpenAI response", "cost": 0.01
            }
            mock_anthropic.generate_response.return_value = {
                "success": True, "response": "Anthropic response", "cost": 0.02
            }
            mock_cohere.generate_response.return_value = {
                "success": True, "response": "Cohere response", "cost": 0.015
            }
            
            result = await client.generate_consensus("Test prompt")
            
            assert result["success"] is True
            assert len(result["responses"]) == 3
            assert result["total_cost"] == 0.045

class TestConstitutionalEvolutionEngine:
    """Test constitutional evolution engine."""
    
    @pytest.fixture
    def engine(self):
        return ConstitutionalEvolutionEngine()
    
    @pytest.mark.asyncio
    async def test_analyze_feedback_batch(self, engine):
        """Test feedback analysis."""
        feedback_samples = [
            {
                "original_content": "AI response",
                "human_feedback": "This was inappropriate",
                "feedback_type": "safety",
                "quality_score": 0.3
            }
        ]
        
        with patch.object(engine, 'api_client') as mock_client:
            mock_client.generate_consensus.return_value = {
                "success": True,
                "responses": ["Principle 1", "Principle 2"],
                "consensus": "Safety principle"
            }
            
            result = await engine.analyze_feedback_batch(feedback_samples)
            
            assert result["success"] is True
            assert "principles" in result
    
    @pytest.mark.asyncio
    async def test_evolve_principles(self, engine):
        """Test principle evolution."""
        with patch.object(engine, '_get_recent_feedback') as mock_feedback, \
             patch.object(engine, 'analyze_feedback_batch') as mock_analyze:
            
            mock_feedback.return_value = [{"sample": "data"}]
            mock_analyze.return_value = {
                "success": True,
                "principles": ["New principle"]
            }
            
            result = await engine.evolve_principles(10)
            
            assert result["success"] is True
            assert "evolved_principles" in result

class TestConsensusManager:
    """Test consensus manager."""
    
    @pytest.fixture
    def manager(self):
        return ConsensusManager()
    
    @pytest.mark.asyncio
    async def test_validate_consensus(self, manager):
        """Test consensus validation."""
        responses = [
            {"response": "Principle 1", "confidence": 0.8},
            {"response": "Principle 1", "confidence": 0.9},
            {"response": "Principle 2", "confidence": 0.7}
        ]
        
        result = await manager.validate_consensus(responses)
        
        assert "consensus_valid" in result
        assert "confidence" in result
    
    @pytest.mark.asyncio
    async def test_weighted_consensus_voting(self, manager):
        """Test weighted consensus voting."""
        responses = [
            {"response": "Principle 1", "confidence": 0.8},
            {"response": "Principle 1", "confidence": 0.9}
        ]
        weights = {"openai": 0.6, "anthropic": 0.4}
        
        result = await manager.weighted_consensus_voting(responses, weights)
        
        assert "consensus_valid" in result
        assert "weighted_scores" in result
    
    @pytest.mark.asyncio
    async def test_conflict_resolution(self, manager):
        """Test conflict resolution."""
        conflicting_responses = [
            {"response": "Principle 1", "confidence": 0.8},
            {"response": "Principle 2", "confidence": 0.9}
        ]
        
        result = await manager.conflict_resolution(conflicting_responses)
        
        assert "resolved_consensus" in result
        assert "resolution_method" in result 