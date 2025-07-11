import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.feedback.task_router import SmartTaskRouter
from src.feedback.quality_predictor import QualityPredictor
from src.feedback.annotator_manager import AnnotatorManager

class TestSmartTaskRouter:
    """Test smart task router functionality."""
    
    @pytest.fixture
    def router(self):
        return SmartTaskRouter()
    
    @pytest.mark.asyncio
    async def test_analyze_complexity(self, router):
        """Test task complexity analysis."""
        task_content = "Translate this complex technical document"
        
        with patch.object(router, 'api_client') as mock_client:
            mock_client.generate_consensus.return_value = {
                "success": True,
                "consensus": "High complexity",
                "responses": ["High", "Medium", "High"]
            }
            
            result = await router.analyze_complexity(task_content)
            
            assert result["success"] is True
            assert "complexity_score" in result
            assert result["complexity_level"] in ["Low", "Medium", "High"]
    
    @pytest.mark.asyncio
    async def test_find_optimal_annotator(self, router):
        """Test optimal annotator finding."""
        task_data = {
            "content": "Translate to Spanish",
            "task_type": "translation",
            "complexity_score": 0.7
        }
        available_annotators = [
            {"id": "1", "skills": {"translation": 0.9}, "availability": "available"},
            {"id": "2", "skills": {"translation": 0.6}, "availability": "available"}
        ]
        
        result = await router.find_optimal_annotator(task_data, available_annotators)
        
        assert result["success"] is True
        assert "optimal_annotator" in result
        assert result["optimal_annotator"]["id"] == "1"  # Higher skill score
    
    @pytest.mark.asyncio
    async def test_assign_task(self, router):
        """Test task assignment."""
        task_id = "task_123"
        annotator_id = "annotator_456"
        
        with patch.object(router, 'db') as mock_db:
            mock_db.query.return_value.filter.return_value.first.return_value = Mock(
                id=task_id, status="pending"
            )
            
            result = await router.assign_task(task_id, annotator_id)
            
            assert result["success"] is True
            assert result["task_id"] == task_id
            assert result["assigned_annotator"] == annotator_id

class TestQualityPredictor:
    """Test quality predictor functionality."""
    
    @pytest.fixture
    def predictor(self):
        return QualityPredictor()
    
    def test_extract_features(self, predictor):
        """Test feature extraction."""
        task_data = {
            "content": "Test content",
            "task_type": "translation",
            "complexity_score": 0.8
        }
        annotator_data = {
            "skill_scores": {"translation": 0.9},
            "performance_history": [0.8, 0.9, 0.85]
        }
        
        features = predictor.extract_features(task_data, annotator_data)
        
        assert "task_complexity" in features
        assert "annotator_skill" in features
        assert "annotator_avg_performance" in features
        assert len(features) > 0
    
    def test_predict_quality(self, predictor):
        """Test quality prediction."""
        task_data = {
            "content": "Test content",
            "task_type": "translation",
            "complexity_score": 0.7
        }
        annotator_data = {
            "skill_scores": {"translation": 0.9},
            "performance_history": [0.8, 0.9, 0.85]
        }
        
        with patch.object(predictor, 'model') as mock_model:
            mock_model.predict.return_value = [0.85]
            mock_model.predict_proba.return_value = [[0.15, 0.85]]
            
            result = predictor.predict_quality(task_data, annotator_data)
            
            assert "predicted_quality" in result
            assert "confidence" in result
            assert result["predicted_quality"] == 0.85
    
    def test_detect_anomalies(self, predictor):
        """Test anomaly detection."""
        task_annotator_pairs = [
            ({"complexity": 0.5}, {"skill": 0.8}),
            ({"complexity": 0.9}, {"skill": 0.3}),  # Potential anomaly
            ({"complexity": 0.6}, {"skill": 0.7})
        ]
        
        with patch.object(predictor, 'anomaly_detector') as mock_detector:
            mock_detector.predict.return_value = [0, 1, 0]  # 1 = anomaly
            
            anomalies = predictor.detect_anomalies(task_annotator_pairs)
            
            assert len(anomalies) == 1
            assert anomalies[0]["index"] == 1
            assert anomalies[0]["is_anomaly"] is True

class TestAnnotatorManager:
    """Test annotator manager functionality."""
    
    @pytest.fixture
    def manager(self):
        return AnnotatorManager()
    
    def test_assess_skills(self, manager):
        """Test skill assessment."""
        performance_data = [
            {"task_type": "translation", "quality_score": 0.9},
            {"task_type": "translation", "quality_score": 0.8},
            {"task_type": "sentiment", "quality_score": 0.7}
        ]
        
        skills = manager.assess_skills(performance_data)
        
        assert "translation" in skills
        assert "sentiment" in skills
        assert skills["translation"] > skills["sentiment"]  # Better performance
    
    def test_calculate_performance_metrics(self, manager):
        """Test performance metrics calculation."""
        performance_history = [0.8, 0.9, 0.7, 0.95, 0.85]
        
        metrics = manager.calculate_performance_metrics(performance_history)
        
        assert "average_quality" in metrics
        assert "consistency_score" in metrics
        assert "trend" in metrics
        assert metrics["average_quality"] == 0.86
    
    @pytest.mark.asyncio
    async def test_find_cultural_matches(self, manager):
        """Test cultural matching."""
        task_data = {
            "content": "Spanish cultural content",
            "required_cultural_context": "Spanish"
        }
        available_annotators = [
            {"id": "1", "cultural_background": "Spanish"},
            {"id": "2", "cultural_background": "English"},
            {"id": "3", "cultural_background": "Spanish"}
        ]
        
        matches = await manager.find_cultural_matches(task_data, available_annotators)
        
        assert len(matches) == 2
        assert all(match["cultural_background"] == "Spanish" for match in matches)
    
    def test_update_availability(self, manager):
        """Test availability update."""
        annotator_id = "annotator_123"
        new_status = "busy"
        
        with patch.object(manager, 'db') as mock_db:
            mock_annotator = Mock()
            mock_db.query.return_value.filter.return_value.first.return_value = mock_annotator
            
            result = manager.update_availability(annotator_id, new_status)
            
            assert result["success"] is True
            assert mock_annotator.availability_status == new_status
    
    def test_get_annotator_profile(self, manager):
        """Test annotator profile retrieval."""
        annotator_id = "annotator_123"
        
        with patch.object(manager, 'db') as mock_db:
            mock_annotator = Mock(
                id=1,
                annotator_id=annotator_id,
                skill_scores={"translation": 0.9},
                performance_history=[0.8, 0.9],
                cultural_background="Spanish",
                availability_status="available"
            )
            mock_db.query.return_value.filter.return_value.first.return_value = mock_annotator
            
            profile = manager.get_annotator_profile(annotator_id)
            
            assert profile["annotator_id"] == annotator_id
            assert profile["skill_scores"]["translation"] == 0.9
            assert profile["availability_status"] == "available" 