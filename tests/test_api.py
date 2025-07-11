import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock

class TestConstitutionalAPI:
    """Test constitutional API endpoints."""
    
    def test_analyze_feedback(self, client, sample_feedback_data):
        """Test feedback analysis endpoint."""
        with patch('src.constitutional.evolution_engine.evolution_engine') as mock_engine:
            mock_engine.analyze_feedback_batch.return_value = {
                "success": True,
                "principles": ["Safety principle", "Helpfulness principle"],
                "summary": "Analysis complete",
                "confidence": 0.85
            }
            
            response = client.post("/api/constitutional/analyze", json=sample_feedback_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data["principles"]) == 2
            assert data["confidence"] == 0.85
    
    def test_get_principles(self, client):
        """Test get principles endpoint."""
        response = client.get("/api/constitutional/principles")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_validate_principle(self, client):
        """Test principle validation endpoint."""
        validation_data = {
            "principle": "Test principle",
            "category": "safety"
        }
        
        with patch('src.constitutional.evolution_engine.evolution_engine') as mock_engine:
            mock_engine._validate_single_principle.return_value = {
                "is_valid": True,
                "confidence_score": 0.8,
                "consistency_score": 0.9
            }
            
            response = client.post("/api/constitutional/validate", json=validation_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["is_valid"] is True
    
    def test_evolve_principles(self, client):
        """Test principle evolution endpoint."""
        with patch('src.constitutional.evolution_engine.evolution_engine') as mock_engine:
            mock_engine.evolve_principles.return_value = {
                "success": True,
                "evolved_principles": ["New principle"],
                "updated_principles": ["Updated principle"],
                "confidence": 0.9
            }
            
            response = client.post("/api/constitutional/evolve?new_feedback_count=100")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data["evolved_principles"]) == 1

class TestTasksAPI:
    """Test tasks API endpoints."""
    
    def test_create_task(self, client, sample_task_data):
        """Test task creation endpoint."""
        response = client.post("/api/tasks/create", json=sample_task_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "task_id" in data
        assert data["content"] == sample_task_data["content"]
    
    def test_get_task_queue(self, client):
        """Test get task queue endpoint."""
        response = client.get("/api/tasks/queue")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_assign_task(self, client):
        """Test task assignment endpoint."""
        assignment_data = {"task_id": "task_123"}
        
        with patch('src.feedback.task_router.task_router') as mock_router:
            mock_router.assign_task.return_value = {
                "success": True,
                "task_id": "task_123",
                "assigned_annotator": "annotator_456"
            }
            
            response = client.post("/api/tasks/assign", json=assignment_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["assigned_annotator"] == "annotator_456"
    
    def test_complete_task(self, client):
        """Test task completion endpoint."""
        completion_data = {
            "feedback": "Task completed successfully",
            "quality_score": 0.9
        }
        
        response = client.put("/api/tasks/task_123/complete", json=completion_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

class TestFeedbackAPI:
    """Test feedback API endpoints."""
    
    def test_submit_feedback(self, client):
        """Test feedback submission endpoint."""
        feedback_data = {
            "task_id": "task_123",
            "original_content": "AI response",
            "human_feedback": "This was helpful",
            "feedback_type": "helpfulness",
            "quality_score": 0.9,
            "annotator_id": "annotator_456"
        }
        
        response = client.post("/api/feedback/submit", json=feedback_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "feedback_id" in data
    
    def test_submit_batch_feedback(self, client):
        """Test batch feedback submission endpoint."""
        batch_data = {
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
        
        response = client.post("/api/feedback/batch", json=batch_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["processed_count"] == 2
    
    def test_get_quality_prediction(self, client):
        """Test quality prediction endpoint."""
        with patch('src.feedback.quality_predictor.quality_predictor') as mock_predictor:
            mock_predictor.predict_quality.return_value = {
                "predicted_quality": 0.85,
                "confidence": 0.9
            }
            
            response = client.get("/api/feedback/quality?task_id=task_123&annotator_id=annotator_456")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["predicted_quality"] == 0.85

class TestAnnotatorsAPI:
    """Test annotators API endpoints."""
    
    def test_register_annotator(self, client, sample_annotator_data):
        """Test annotator registration endpoint."""
        response = client.post("/api/annotators/register", json=sample_annotator_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["annotator_id"] == sample_annotator_data["annotator_id"]
    
    def test_get_annotator_profile(self, client):
        """Test get annotator profile endpoint."""
        response = client.get("/api/annotators/annotator_123/profile")
        
        assert response.status_code == 200
        data = response.json()
        assert "annotator_id" in data
        assert "skill_scores" in data
    
    def test_update_availability(self, client):
        """Test availability update endpoint."""
        availability_data = {"availability_status": "busy"}
        
        response = client.put("/api/annotators/annotator_123/availability", json=availability_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_get_matching_annotators(self, client):
        """Test get matching annotators endpoint."""
        response = client.get("/api/annotators/matching?task_type=translation&required_languages=Spanish")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_all_annotators(self, client):
        """Test get all annotators endpoint."""
        response = client.get("/api/annotators")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_delete_annotator(self, client):
        """Test delete annotator endpoint."""
        response = client.delete("/api/annotators/annotator_123")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

class TestHealthAndRoot:
    """Test health check and root endpoints."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Welcome to ConstitutionalFlow"
        assert data["status"] == "running"
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_api_docs(self, client):
        """Test API docs endpoint."""
        response = client.get("/api/docs")
        
        assert response.status_code == 200
        data = response.json()
        assert "swagger_ui" in data
        assert "redoc" in data

class TestErrorHandling:
    """Test error handling in API endpoints."""
    
    def test_invalid_json(self, client):
        """Test handling of invalid JSON."""
        response = client.post("/api/constitutional/analyze", data="invalid json")
        
        assert response.status_code == 422
    
    def test_missing_required_fields(self, client):
        """Test handling of missing required fields."""
        response = client.post("/api/tasks/create", json={})
        
        assert response.status_code == 422
    
    def test_nonexistent_resource(self, client):
        """Test handling of nonexistent resources."""
        response = client.get("/api/tasks/nonexistent_task")
        
        assert response.status_code == 404
    
    def test_database_error(self, client):
        """Test handling of database errors."""
        with patch('src.core.database.get_db') as mock_db:
            mock_db.side_effect = Exception("Database error")
            
            response = client.get("/api/constitutional/principles")
            
            assert response.status_code == 500 