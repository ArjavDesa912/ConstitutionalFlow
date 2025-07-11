import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import Mock, patch
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.main import app
from src.core.database import Base, get_db
from src.core.config import settings

# Test database URL
TEST_DATABASE_URL = "sqlite:///./test.db"

# Create test engine
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with a fresh database session."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    with patch('src.constitutional.api_client.OpenAIClient') as mock:
        mock_instance = Mock()
        mock.return_value = mock_instance
        mock_instance.generate_response.return_value = {
            "success": True,
            "response": "Mock OpenAI response",
            "cost": 0.01,
            "tokens_used": 100
        }
        yield mock_instance

@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic client for testing."""
    with patch('src.constitutional.api_client.AnthropicClient') as mock:
        mock_instance = Mock()
        mock.return_value = mock_instance
        mock_instance.generate_response.return_value = {
            "success": True,
            "response": "Mock Anthropic response",
            "cost": 0.02,
            "tokens_used": 150
        }
        yield mock_instance

@pytest.fixture
def mock_cohere_client():
    """Mock Cohere client for testing."""
    with patch('src.constitutional.api_client.CohereClient') as mock:
        mock_instance = Mock()
        mock.return_value = mock_instance
        mock_instance.generate_response.return_value = {
            "success": True,
            "response": "Mock Cohere response",
            "cost": 0.015,
            "tokens_used": 120
        }
        yield mock_instance

@pytest.fixture
def sample_feedback_data():
    """Sample feedback data for testing."""
    return {
        "feedback_samples": [
            {
                "original_content": "AI response content",
                "human_feedback": "This response was inappropriate",
                "feedback_type": "safety",
                "quality_score": 0.3,
                "annotator_id": "test_annotator_1"
            },
            {
                "original_content": "Another AI response",
                "human_feedback": "This was helpful and accurate",
                "feedback_type": "helpfulness",
                "quality_score": 0.9,
                "annotator_id": "test_annotator_2"
            }
        ],
        "store_principles": True
    }

@pytest.fixture
def sample_task_data():
    """Sample task data for testing."""
    return {
        "content": "Translate this text to Spanish",
        "task_type": "translation",
        "priority_level": 1,
        "estimated_time": 300
    }

@pytest.fixture
def sample_annotator_data():
    """Sample annotator data for testing."""
    return {
        "annotator_id": "test_annotator_123",
        "skill_scores": {"translation": 0.9, "sentiment": 0.7},
        "cultural_background": "Spanish",
        "languages": ["English", "Spanish"],
        "availability_status": "available"
    } 