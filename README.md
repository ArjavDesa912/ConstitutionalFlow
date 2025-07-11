# ConstitutionalFlow
# Adaptive Constitutional AI Platform - Implementation Documentation

## 🎉 Implementation Complete!

This repository contains a fully implemented **Adaptive Constitutional AI Platform** that combines Dynamic Constitutional Learning with Intelligent Human Feedback Orchestration. The system uses API-based AI models for constitutional reasoning while implementing CPU-optimized infrastructure for scalable data processing.

## 📊 Implementation Status

✅ **Core Infrastructure** - Complete
- FastAPI application with all routers
- PostgreSQL database with SQLAlchemy ORM
- Redis caching and session management
- Docker containerization with docker-compose
- Configuration management with environment variables

✅ **Constitutional AI Components** - Complete
- Multi-model API client (OpenAI, Anthropic, Cohere)
- Constitutional evolution engine
- Consensus manager with weighted voting
- Structured prompt templates
- Principle validation and conflict resolution

✅ **Feedback Orchestration** - Complete
- Smart task router with AI-powered complexity analysis
- Quality predictor using ensemble methods
- Annotator manager with skill assessment
- Cultural matching and availability management
- Performance monitoring and analytics

✅ **API Endpoints** - Complete
- Constitutional management (analyze, validate, evolve)
- Task management (create, assign, complete)
- Feedback processing (submit, batch, quality prediction)
- Annotator management (register, profile, matching)
- Analytics and system health endpoints

✅ **Testing & Documentation** - Complete
- Comprehensive test suite with pytest
- Unit tests for all components
- Integration tests for API endpoints
- Test coverage reporting
- API reference documentation
- Usage examples and tutorials

✅ **Deployment & DevOps** - Complete
- Docker setup with health checks
- Setup script for easy installation
- Environment configuration
- Production-ready configuration
- Monitoring and logging setup

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker and Docker Compose (for full setup)
- API keys for OpenAI, Anthropic, and/or Cohere

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ConstitutionalFlow
   ```

2. **Run the setup script**
   ```bash
   python scripts/setup.py
   ```

3. **Configure environment variables**
   ```bash
   # Edit .env file with your API keys
   nano .env
   ```

4. **Start the application**
   ```bash
   uvicorn src.main:app --reload
   ```

5. **Access the API documentation**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## 🏗️ Core Architecture

### Technology Stack
- **Backend**: Python 3.11+ with FastAPI
- **Database**: PostgreSQL with Redis caching
- **Message Queue**: Redis Streams for task processing
- **API Clients**: OpenAI, Anthropic Claude, Cohere
- **Containerization**: Docker + Docker Compose
- **Monitoring**: Structured logging with structlog

### Project Structure
```
constitutional-ai-platform/
├── src/
│   ├── constitutional/
│   │   ├── __init__.py
│   │   ├── api_client.py          # Multi-model API client
│   │   ├── evolution_engine.py    # Constitutional evolution
│   │   ├── consensus_manager.py   # Consensus management
│   │   └── prompts.py             # Prompt templates
│   ├── feedback/
│   │   ├── __init__.py
│   │   ├── task_router.py         # Smart task routing
│   │   ├── quality_predictor.py   # Quality prediction
│   │   └── annotator_manager.py   # Annotator management
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── constitutional.py  # Constitutional endpoints
│   │   │   ├── tasks.py           # Task management
│   │   │   ├── feedback.py        # Feedback processing
│   │   │   └── annotators.py      # Annotator management
│   │   └── models/
│   │       ├── constitutional.py  # Constitutional models
│   │       ├── tasks.py           # Task models
│   │       ├── feedback.py        # Feedback models
│   │       └── annotators.py      # Annotator models
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py              # Configuration management
│   │   ├── database.py            # Database models & connection
│   │   ├── cache.py               # Redis cache utility
│   │   └── utils.py               # Utility functions
│   └── main.py                    # FastAPI application
├── tests/
├── docker/
├── scripts/
│   └── setup.py                   # Setup script
├── docs/
├── requirements.txt               # Python dependencies
├── docker-compose.yml            # Docker services
├── Dockerfile                    # Application container
└── README.md                     # This file
```

## 🔧 Core Components

### 1. Multi-Model API Client (`src/constitutional/api_client.py`)
- **OpenAI Client**: GPT-4 integration with rate limiting
- **Anthropic Client**: Claude integration with error handling
- **Cohere Client**: Generate API integration
- **MultiModelClient**: Orchestrates multiple providers with failover
- **Features**: Rate limiting, caching, cost tracking, consensus generation

### 2. Constitutional Evolution Engine (`src/constitutional/evolution_engine.py`)
- **Feedback Analysis**: Extracts principles from human feedback
- **Principle Validation**: Cross-model consensus checking
- **Evolution Tracking**: Identifies new and updated principles
- **Historical Consistency**: Maintains principle versioning

### 3. Consensus Manager (`src/constitutional/consensus_manager.py`)
- **Multi-Model Consensus**: Aggregates responses from multiple AI models
- **Weighted Voting**: Provider-specific weighting for consensus
- **Conflict Resolution**: Handles conflicting model responses
- **Principle Ranking**: Ranks principles by confidence and consistency

### 4. Smart Task Router (`src/feedback/task_router.py`)
- **AI-Powered Complexity Analysis**: Analyzes task complexity using LLMs
- **Intelligent Assignment**: Matches tasks to optimal annotators
- **Quality Prediction**: Predicts annotation quality before assignment
- **Workload Balancing**: Real-time workload distribution

### 5. Quality Predictor (`src/feedback/quality_predictor.py`)
- **Ensemble Methods**: Random Forest for quality prediction
- **Anomaly Detection**: Isolation Forest for detecting unusual patterns
- **Feature Engineering**: Extracts relevant features from task-annotator pairs
- **Performance Monitoring**: Tracks prediction accuracy over time

### 6. Annotator Manager (`src/feedback/annotator_manager.py`)
- **Skill Assessment**: Tracks annotator skills and performance
- **Cultural Matching**: Matches annotators to culturally appropriate tasks
- **Performance Analytics**: Comprehensive performance metrics
- **Availability Management**: Real-time availability tracking

## 📡 API Endpoints

### Constitutional Management
- `POST /api/constitutional/analyze` - Analyze feedback for principles
- `GET /api/constitutional/principles` - Get current principles
- `POST /api/constitutional/validate` - Validate principle changes
- `GET /api/constitutional/history` - Get evolution history
- `POST /api/constitutional/evolve` - Evolve principles from feedback
- `POST /api/constitutional/consensus` - Validate model consensus
- `POST /api/constitutional/weighted-voting` - Weighted consensus voting
- `POST /api/constitutional/conflict-resolution` - Resolve conflicts
- `GET /api/constitutional/ranking` - Rank principles by confidence

### Task Management
- `POST /api/tasks/create` - Create new annotation tasks
- `GET /api/tasks/queue` - Get task queue for annotators
- `POST /api/tasks/assign` - Intelligently assign tasks
- `PUT /api/tasks/{task_id}/complete` - Complete tasks with feedback
- `GET /api/tasks/{task_id}` - Get task details
- `PUT /api/tasks/{task_id}/status` - Update task status
- `GET /api/tasks/analytics` - Task analytics and statistics

### Feedback Processing
- `POST /api/feedback/submit` - Submit human feedback
- `POST /api/feedback/batch` - Submit batch feedback
- `GET /api/feedback/quality` - Get quality predictions
- `GET /api/feedback/analytics` - Feedback analytics
- `GET /api/feedback/{feedback_id}` - Get feedback details
- `POST /api/feedback/quality-prediction` - Predict quality

### Annotator Management
- `POST /api/annotators/register` - Register new annotators
- `GET /api/annotators/{id}/profile` - Get annotator profile
- `PUT /api/annotators/{id}/availability` - Update availability
- `PUT /api/annotators/{id}/skills` - Update skills
- `GET /api/annotators/matching` - Find matching annotators
- `GET /api/annotators` - Get all annotators
- `GET /api/annotators/analytics` - Annotator analytics
- `DELETE /api/annotators/{id}` - Delete annotator
- `GET /api/annotators/{id}/performance` - Performance metrics

## 🗄️ Database Schema

### Constitutional Principles
```sql
CREATE TABLE constitutional_principles (
    id SERIAL PRIMARY KEY,
    principle_text TEXT NOT NULL,
    category VARCHAR(100),
    confidence_score FLOAT,
    cultural_context JSONB,
    version_number INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true
);
```

### Feedback Samples
```sql
CREATE TABLE feedback_samples (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(255),
    original_content TEXT,
    human_feedback TEXT,
    feedback_type VARCHAR(50),
    annotator_id VARCHAR(255),
    quality_score FLOAT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Annotators
```sql
CREATE TABLE annotators (
    id SERIAL PRIMARY KEY,
    annotator_id VARCHAR(255) UNIQUE,
    skill_scores JSONB,
    performance_history JSONB,
    cultural_background VARCHAR(100),
    languages JSONB,
    availability_status VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Tasks
```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(255) UNIQUE,
    content TEXT,
    task_type VARCHAR(100),
    complexity_score FLOAT,
    estimated_time INTEGER,
    priority_level INTEGER,
    status VARCHAR(50),
    assigned_annotator_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);
```

## 🔄 Workflow Examples

### 1. Constitutional Principle Evolution
```python
# Submit feedback for analysis
feedback_data = {
    "feedback_samples": [
        {
            "original_content": "AI response content",
            "human_feedback": "This response was inappropriate",
            "feedback_type": "safety",
            "quality_score": 0.3
        }
    ],
    "store_principles": True
}

# Analyze and extract principles
response = await client.post("/api/constitutional/analyze", json=feedback_data)
principles = response.json()["principles"]

# Evolve principles over time
evolution = await client.post("/api/constitutional/evolve?new_feedback_count=100")
```

### 2. Task Assignment and Quality Prediction
```python
# Create a new task
task_data = {
    "content": "Translate this text to Spanish",
    "task_type": "translation",
    "priority": 1
}

task = await client.post("/api/tasks/create", json=task_data)

# Get quality prediction for annotator
prediction = await client.get(f"/api/feedback/quality?task_id={task['task_id']}&annotator_id=annotator_123")

# Assign task to best annotator
assignment = await client.post("/api/tasks/assign", json={
    "task_id": task["task_id"]
})
```

### 3. Annotator Management
```python
# Register new annotator
annotator_data = {
    "annotator_id": "annotator_123",
    "skill_scores": {"translation": 0.9, "sentiment": 0.7},
    "cultural_background": "Spanish",
    "languages": ["English", "Spanish"]
}

await client.post("/api/annotators/register", json=annotator_data)

# Get matching annotators for task
matches = await client.get("/api/annotators/matching?task_type=translation&required_languages=Spanish")
```

## 🧪 Testing

### Run Tests
```bash
# Run the test runner script (recommended)
python scripts/run_tests.py

# Run all tests with coverage
python scripts/run_tests.py

# Run specific test categories
python scripts/run_tests.py unit
python scripts/run_tests.py integration
python scripts/run_tests.py constitutional
python scripts/run_tests.py feedback
python scripts/run_tests.py api

# Manual test execution
pytest tests/ -v --cov=src --cov-report=html --cov-report=xml

# Run specific test files
pytest tests/test_constitutional.py -v
pytest tests/test_feedback.py -v
pytest tests/test_api.py -v
```

### Test Coverage
The comprehensive test suite covers:
- ✅ API endpoint functionality and error handling
- ✅ Database operations and data validation
- ✅ Constitutional evolution algorithms
- ✅ Quality prediction models and feature engineering
- ✅ Task routing logic and intelligent assignment
- ✅ Annotator management and skill assessment
- ✅ Multi-model API client integration
- ✅ Consensus management and conflict resolution
- ✅ Performance monitoring and analytics
- ✅ Error handling and edge cases

### Test Structure
```
tests/
├── conftest.py              # Test configuration and fixtures
├── test_constitutional.py   # Constitutional AI component tests
├── test_feedback.py         # Feedback orchestration tests
└── test_api.py             # API endpoint integration tests
```

## 🚀 Deployment

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d

# Scale services
docker-compose up -d --scale app=3
```

### Production Configuration
1. Set `DEBUG=False` in environment
2. Configure production database and Redis
3. Set up proper API key management
4. Configure monitoring and logging
5. Set up load balancing and SSL

### Environment Variables
```bash
# Required
DATABASE_URL=postgresql://user:password@host/db
REDIS_URL=redis://host:port
OPENAI_API_KEY=your-key
ANTHROPIC_API_KEY=your-key
COHERE_API_KEY=your-key

# Optional
DEBUG=False
SECRET_KEY=your-secret-key
LOG_LEVEL=INFO
DAILY_BUDGET_LIMIT=100.0
```

## 📊 Monitoring and Analytics

### Built-in Analytics
- Constitutional principle evolution tracking
- Annotator performance metrics
- Task completion rates and quality trends
- API usage and cost monitoring
- System health and performance metrics

### Logging
- Structured logging with structlog
- Performance monitoring with execution time tracking
- Error tracking and alerting
- API request/response logging

## 🔒 Security Features

- API key secure storage (environment variables)
- Database connection encryption
- Input validation and sanitization
- Rate limiting per user/endpoint
- Audit logging for all constitutional changes
- CORS configuration for web access

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for GPT-4 API
- Anthropic for Claude API
- Cohere for Generate API
- FastAPI for the web framework
- SQLAlchemy for database ORM
- Redis for caching and session management

## 📚 Documentation

### API Reference
- **Complete API Documentation**: [docs/API_REFERENCE.md](docs/API_REFERENCE.md)
- **Interactive Swagger UI**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc

### Examples and Tutorials
- **Basic Usage Example**: [examples/basic_usage.py](examples/basic_usage.py)
- **Workflow Examples**: See the README workflow section
- **Test Examples**: Review the comprehensive test suite

### Architecture Documentation
- **System Architecture**: See the Core Architecture section
- **Database Schema**: See the Database Schema section
- **Component Documentation**: See the Core Components section

## 🎯 Quick Examples

### Constitutional Principle Evolution
```python
import asyncio
import httpx

async def evolve_principles():
    async with httpx.AsyncClient() as client:
        # Submit feedback for analysis
        response = await client.post("http://localhost:8000/api/constitutional/analyze", json={
            "feedback_samples": [{
                "original_content": "AI response content",
                "human_feedback": "This response was inappropriate",
                "feedback_type": "safety",
                "quality_score": 0.3
            }],
            "store_principles": True
        })
        
        # Evolve principles
        evolution = await client.post("http://localhost:8000/api/constitutional/evolve?new_feedback_count=100")
        return evolution.json()

# Run the example
result = asyncio.run(evolve_principles())
print(result)
```

### Intelligent Task Assignment
```python
async def assign_task_intelligently():
    async with httpx.AsyncClient() as client:
        # Create a task
        task = await client.post("http://localhost:8000/api/tasks/create", json={
            "content": "Translate this text to Spanish",
            "task_type": "translation",
            "priority": 1
        })
        
        # Get quality prediction
        prediction = await client.get(
            f"http://localhost:8000/api/feedback/quality?task_id={task.json()['task_id']}&annotator_id=annotator_123"
        )
        
        # Assign task to best annotator
        assignment = await client.post("http://localhost:8000/api/tasks/assign", json={
            "task_id": task.json()["task_id"]
        })
        
        return assignment.json()
```

## 📞 Support

For questions and support:
- 📖 **Documentation**: Check the API reference and examples
- 🧪 **Testing**: Run the test suite to verify functionality
- 🐛 **Issues**: Create an issue on GitHub for bugs
- 💡 **Features**: Submit feature requests on GitHub
- 📧 **Contact**: Review the project documentation

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and add tests
4. **Run the test suite**: `python scripts/run_tests.py`
5. **Submit a pull request**

### Development Setup
```bash
# Clone and setup
git clone <repository-url>
cd ConstitutionalFlow
python scripts/setup.py

# Run tests
python scripts/run_tests.py

# Start development server
uvicorn src.main:app --reload
```

---

**ConstitutionalFlow** - Building the future of AI alignment through adaptive constitutional learning and intelligent feedback orchestration.

*🎉 **Fully Implemented and Production Ready** 🎉*
