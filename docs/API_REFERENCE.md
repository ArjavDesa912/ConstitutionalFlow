# ConstitutionalFlow API Reference

## Overview

The ConstitutionalFlow API provides endpoints for managing adaptive constitutional AI principles, intelligent task routing, quality prediction, and annotator management. This document provides detailed information about all available endpoints, request/response formats, and usage examples.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication for development purposes. In production, implement proper authentication using API keys or OAuth 2.0.

## Common Response Format

All API responses follow a consistent format:

```json
{
  "success": true,
  "data": {...},
  "message": "Operation completed successfully",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

Error responses:

```json
{
  "success": false,
  "error": "Error description",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## Constitutional Management Endpoints

### Analyze Feedback for Principles

**POST** `/api/constitutional/analyze`

Analyzes human feedback to extract and evolve constitutional principles.

**Request Body:**
```json
{
  "feedback_samples": [
    {
      "original_content": "AI response content",
      "human_feedback": "This response was inappropriate",
      "feedback_type": "safety",
      "quality_score": 0.3,
      "annotator_id": "annotator_123"
    }
  ],
  "store_principles": true
}
```

**Response:**
```json
{
  "success": true,
  "principles": [
    "Safety principle: Do not provide harmful instructions",
    "Helpfulness principle: Provide accurate and useful information"
  ],
  "summary": "Analysis completed successfully",
  "confidence": 0.85
}
```

### Get Constitutional Principles

**GET** `/api/constitutional/principles`

Retrieves current constitutional principles.

**Query Parameters:**
- `category` (optional): Filter by principle category
- `active_only` (optional, default: true): Return only active principles

**Response:**
```json
[
  {
    "id": 1,
    "principle_text": "Safety principle: Do not provide harmful instructions",
    "category": "safety",
    "confidence_score": 0.9,
    "cultural_context": {"region": "global"},
    "version_number": 1,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "is_active": true
  }
]
```

### Validate Principle Changes

**POST** `/api/constitutional/validate`

Validates proposed principle changes against historical consistency.

**Request Body:**
```json
{
  "principle": "New safety principle",
  "category": "safety"
}
```

**Response:**
```json
{
  "success": true,
  "is_valid": true,
  "confidence_score": 0.8,
  "consistency_score": 0.9,
  "recommendations": ["Consider cultural context"]
}
```

### Evolve Principles

**POST** `/api/constitutional/evolve`

Evolves constitutional principles based on recent feedback.

**Query Parameters:**
- `new_feedback_count` (optional, default: 100): Number of recent feedback samples to analyze

**Response:**
```json
{
  "success": true,
  "evolved_principles": ["New evolved principle"],
  "updated_principles": ["Updated existing principle"],
  "confidence": 0.9
}
```

### Consensus Validation

**POST** `/api/constitutional/consensus`

Validates consensus among multiple model responses.

**Request Body:**
```json
[
  {
    "response": "Principle 1",
    "confidence": 0.8
  },
  {
    "response": "Principle 1",
    "confidence": 0.9
  }
]
```

**Response:**
```json
{
  "success": true,
  "consensus_valid": true,
  "confidence": 0.85,
  "consensus": "Principle 1",
  "agreement_score": 0.9
}
```

## Task Management Endpoints

### Create Task

**POST** `/api/tasks/create`

Creates a new annotation task.

**Request Body:**
```json
{
  "content": "Translate this text to Spanish",
  "task_type": "translation",
  "priority_level": 1,
  "estimated_time": 300
}
```

**Response:**
```json
{
  "success": true,
  "task_id": "task_123",
  "content": "Translate this text to Spanish",
  "task_type": "translation",
  "complexity_score": 0.7,
  "status": "pending"
}
```

### Get Task Queue

**GET** `/api/tasks/queue`

Retrieves available tasks for annotators.

**Query Parameters:**
- `annotator_id` (optional): Filter tasks for specific annotator
- `task_type` (optional): Filter by task type
- `limit` (optional, default: 50): Maximum number of tasks to return

**Response:**
```json
[
  {
    "task_id": "task_123",
    "content": "Task content",
    "task_type": "translation",
    "complexity_score": 0.7,
    "priority_level": 1,
    "status": "pending"
  }
]
```

### Assign Task

**POST** `/api/tasks/assign`

Intelligently assigns a task to the optimal annotator.

**Request Body:**
```json
{
  "task_id": "task_123"
}
```

**Response:**
```json
{
  "success": true,
  "task_id": "task_123",
  "assigned_annotator": "annotator_456",
  "predicted_quality": 0.85,
  "assignment_reason": "Highest skill match"
}
```

### Complete Task

**PUT** `/api/tasks/{task_id}/complete`

Marks a task as completed with feedback.

**Request Body:**
```json
{
  "feedback": "Task completed successfully",
  "quality_score": 0.9,
  "completion_time": 280
}
```

**Response:**
```json
{
  "success": true,
  "task_id": "task_123",
  "completion_time": 280,
  "quality_score": 0.9
}
```

## Feedback Processing Endpoints

### Submit Feedback

**POST** `/api/feedback/submit`

Submits individual feedback for analysis.

**Request Body:**
```json
{
  "task_id": "task_123",
  "original_content": "AI response",
  "human_feedback": "This was helpful",
  "feedback_type": "helpfulness",
  "quality_score": 0.9,
  "annotator_id": "annotator_456"
}
```

**Response:**
```json
{
  "success": true,
  "feedback_id": "feedback_789",
  "processed": true
}
```

### Submit Batch Feedback

**POST** `/api/feedback/batch`

Submits multiple feedback samples for batch processing.

**Request Body:**
```json
{
  "feedback_samples": [
    {
      "task_id": "task_123",
      "original_content": "AI response 1",
      "human_feedback": "Good response",
      "feedback_type": "helpfulness",
      "quality_score": 0.8
    },
    {
      "task_id": "task_124",
      "original_content": "AI response 2",
      "human_feedback": "Bad response",
      "feedback_type": "safety",
      "quality_score": 0.3
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "processed_count": 2,
  "failed_count": 0,
  "feedback_ids": ["feedback_789", "feedback_790"]
}
```

### Get Quality Prediction

**GET** `/api/feedback/quality`

Predicts quality for a task-annotator combination.

**Query Parameters:**
- `task_id`: Task identifier
- `annotator_id`: Annotator identifier

**Response:**
```json
{
  "success": true,
  "predicted_quality": 0.85,
  "confidence": 0.9,
  "features": {
    "task_complexity": 0.7,
    "annotator_skill": 0.9,
    "annotator_avg_performance": 0.85
  }
}
```

## Annotator Management Endpoints

### Register Annotator

**POST** `/api/annotators/register`

Registers a new annotator in the system.

**Request Body:**
```json
{
  "annotator_id": "annotator_123",
  "skill_scores": {
    "translation": 0.9,
    "sentiment": 0.7
  },
  "cultural_background": "Spanish",
  "languages": ["English", "Spanish"],
  "availability_status": "available"
}
```

**Response:**
```json
{
  "success": true,
  "annotator_id": "annotator_123",
  "message": "Annotator registered successfully"
}
```

### Get Annotator Profile

**GET** `/api/annotators/{annotator_id}/profile`

Retrieves an annotator's profile and performance data.

**Response:**
```json
{
  "annotator_id": "annotator_123",
  "skill_scores": {
    "translation": 0.9,
    "sentiment": 0.7
  },
  "performance_history": [0.8, 0.9, 0.85],
  "cultural_background": "Spanish",
  "languages": ["English", "Spanish"],
  "availability_status": "available",
  "total_tasks_completed": 150,
  "average_quality_score": 0.85
}
```

### Update Availability

**PUT** `/api/annotators/{annotator_id}/availability`

Updates an annotator's availability status.

**Request Body:**
```json
{
  "availability_status": "busy"
}
```

**Response:**
```json
{
  "success": true,
  "annotator_id": "annotator_123",
  "availability_status": "busy"
}
```

### Find Matching Annotators

**GET** `/api/annotators/matching`

Finds annotators matching specific criteria.

**Query Parameters:**
- `task_type`: Required task type
- `required_languages` (optional): Required languages
- `cultural_context` (optional): Required cultural context
- `min_skill_score` (optional): Minimum skill score

**Response:**
```json
[
  {
    "annotator_id": "annotator_123",
    "skill_scores": {"translation": 0.9},
    "cultural_background": "Spanish",
    "languages": ["English", "Spanish"],
    "availability_status": "available",
    "match_score": 0.95
  }
]
```

## Analytics Endpoints

### Task Analytics

**GET** `/api/tasks/analytics`

Retrieves task-related analytics and statistics.

**Response:**
```json
{
  "total_tasks": 1000,
  "completed_tasks": 850,
  "pending_tasks": 150,
  "avg_completion_time": 320,
  "quality_distribution": {
    "high": 0.6,
    "medium": 0.3,
    "low": 0.1
  },
  "task_type_distribution": {
    "translation": 0.4,
    "sentiment": 0.3,
    "safety": 0.3
  }
}
```

### Annotator Analytics

**GET** `/api/annotators/analytics`

Retrieves annotator performance analytics.

**Response:**
```json
{
  "total_annotators": 50,
  "available_annotators": 35,
  "avg_quality_score": 0.82,
  "top_performers": [
    {
      "annotator_id": "annotator_123",
      "avg_quality": 0.95,
      "tasks_completed": 200
    }
  ],
  "skill_distribution": {
    "translation": 0.4,
    "sentiment": 0.3,
    "safety": 0.3
  }
}
```

### Feedback Analytics

**GET** `/api/feedback/analytics`

Retrieves feedback analysis and trends.

**Response:**
```json
{
  "total_samples": 5000,
  "avg_quality_score": 0.78,
  "feedback_type_distribution": {
    "helpfulness": 0.4,
    "safety": 0.3,
    "accuracy": 0.3
  },
  "trends": {
    "quality_improvement": 0.05,
    "feedback_volume": "increasing"
  }
}
```

## System Endpoints

### Health Check

**GET** `/health`

Checks system health and status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "version": "1.0.0",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "api_clients": "healthy"
  }
}
```

### API Documentation

**GET** `/api/docs`

Provides information about API documentation.

**Response:**
```json
{
  "message": "API documentation available at /docs",
  "swagger_ui": "/docs",
  "redoc": "/redoc",
  "openapi_spec": "/openapi.json"
}
```

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid input data |
| 404 | Not Found - Resource not found |
| 422 | Validation Error - Invalid request format |
| 500 | Internal Server Error - Server error |

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **OpenAI API**: 100 requests per minute
- **Anthropic API**: 100 requests per minute  
- **Cohere API**: 100 requests per minute
- **General API**: 1000 requests per minute

## Cost Tracking

The system tracks API costs for external services:

- **Daily Budget Limit**: $100 (configurable)
- **Monthly Budget Limit**: $1000 (configurable)
- **Cost Alerts**: Automatic alerts when approaching limits

## Best Practices

1. **Batch Operations**: Use batch endpoints for multiple operations
2. **Error Handling**: Always check response status codes
3. **Rate Limiting**: Implement exponential backoff for retries
4. **Data Validation**: Validate input data before sending requests
5. **Monitoring**: Monitor API usage and costs regularly

## SDK Examples

### Python Client Example

```python
import httpx
import asyncio

async def analyze_feedback():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/constitutional/analyze",
            json={
                "feedback_samples": [{
                    "original_content": "AI response",
                    "human_feedback": "This was inappropriate",
                    "feedback_type": "safety",
                    "quality_score": 0.3
                }],
                "store_principles": True
            }
        )
        return response.json()

# Run the example
result = asyncio.run(analyze_feedback())
print(result)
```

### JavaScript Client Example

```javascript
async function analyzeFeedback() {
    const response = await fetch('http://localhost:8000/api/constitutional/analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            feedback_samples: [{
                original_content: "AI response",
                human_feedback: "This was inappropriate",
                feedback_type: "safety",
                quality_score: 0.3
            }],
            store_principles: true
        })
    });
    return await response.json();
}

// Run the example
analyzeFeedback().then(result => console.log(result));
```

## Support

For API support and questions:

1. Check the interactive documentation at `/docs`
2. Review the test examples in the `tests/` directory
3. Run the example script: `python examples/basic_usage.py`
4. Create an issue on GitHub for bugs or feature requests 