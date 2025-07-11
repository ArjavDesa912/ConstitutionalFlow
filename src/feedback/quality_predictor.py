import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sqlalchemy.orm import Session
from src.core.database import get_db, FeedbackSample, Annotator
from src.core.utils import logger, log_execution_time
from src.core.cache import cache

class QualityPredictor:
    """Ensemble-based quality prediction and anomaly detection system"""
    
    def __init__(self):
        self.rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_columns = [
            'task_complexity', 'annotator_experience', 'task_type_encoded',
            'content_length', 'time_of_day', 'day_of_week',
            'annotator_fatigue', 'cultural_match', 'language_match'
        ]
    
    @log_execution_time
    async def predict_quality(self, task_data: Dict[str, Any], annotator_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict annotation quality for a task-annotator pairing"""
        try:
            # Extract features
            features = await self._extract_features(task_data, annotator_data)
            
            # Check if model is trained
            if not self.is_trained:
                await self._train_model()
            
            # Make prediction
            if self.is_trained:
                prediction = self._make_prediction(features)
                anomaly_score = self._detect_anomaly(features)
            else:
                # Fallback to rule-based prediction
                prediction = self._rule_based_prediction(features)
                anomaly_score = 0.5
            
            return {
                'predicted_quality': prediction,
                'anomaly_score': anomaly_score,
                'confidence': self._calculate_confidence(features),
                'risk_factors': self._identify_risk_factors(features),
                'recommendations': self._generate_recommendations(features, prediction)
            }
            
        except Exception as e:
            logger.error("Error in quality prediction", error=str(e))
            return {
                'predicted_quality': 0.5,
                'anomaly_score': 0.5,
                'confidence': 0.3,
                'risk_factors': ['Prediction failed'],
                'recommendations': ['Use manual review']
            }
    
    async def _extract_features(self, task_data: Dict[str, Any], annotator_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract features for quality prediction"""
        try:
            # Task features
            task_complexity = task_data.get('complexity_score', 0.5)
            content_length = len(task_data.get('content', ''))
            task_type = task_data.get('task_type', 'general')
            
            # Annotator features
            skill_scores = annotator_data.get('skill_scores', {})
            performance_history = annotator_data.get('performance_history', {})
            cultural_background = annotator_data.get('cultural_background', '')
            languages = annotator_data.get('languages', [])
            
            # Calculate derived features
            annotator_experience = self._calculate_experience(performance_history)
            task_type_encoded = self._encode_task_type(task_type)
            time_of_day = datetime.now().hour / 24.0
            day_of_week = datetime.now().weekday() / 7.0
            annotator_fatigue = self._calculate_fatigue(performance_history)
            cultural_match = self._calculate_cultural_match(task_data, cultural_background)
            language_match = self._calculate_language_match(task_data, languages)
            
            return {
                'task_complexity': task_complexity,
                'annotator_experience': annotator_experience,
                'task_type_encoded': task_type_encoded,
                'content_length': content_length,
                'time_of_day': time_of_day,
                'day_of_week': day_of_week,
                'annotator_fatigue': annotator_fatigue,
                'cultural_match': cultural_match,
                'language_match': language_match
            }
            
        except Exception as e:
            logger.error("Error extracting features", error=str(e))
            return {col: 0.5 for col in self.feature_columns}
    
    def _calculate_experience(self, performance_history: Dict[str, Any]) -> float:
        """Calculate annotator experience level"""
        try:
            if not performance_history:
                return 0.5
            
            # Extract relevant metrics
            total_tasks = performance_history.get('total_tasks', 0)
            avg_quality = performance_history.get('average_quality', 0.5)
            months_active = performance_history.get('months_active', 1)
            
            # Normalize experience score
            experience_score = min((total_tasks * avg_quality * months_active) / 100, 1.0)
            return experience_score
            
        except Exception:
            return 0.5
    
    def _encode_task_type(self, task_type: str) -> float:
        """Encode task type as numerical feature"""
        type_encodings = {
            'sentiment': 0.2,
            'classification': 0.4,
            'translation': 0.6,
            'summarization': 0.8,
            'qa': 1.0
        }
        return type_encodings.get(task_type, 0.5)
    
    def _calculate_fatigue(self, performance_history: Dict[str, Any]) -> float:
        """Calculate annotator fatigue level"""
        try:
            if not performance_history:
                return 0.0
            
            # Get recent performance trend
            recent_performance = performance_history.get('recent_performance', [])
            if len(recent_performance) < 3:
                return 0.0
            
            # Calculate performance decline
            recent_avg = np.mean(recent_performance[-3:])
            overall_avg = performance_history.get('average_quality', 0.5)
            
            if overall_avg > 0:
                fatigue = max(0, (overall_avg - recent_avg) / overall_avg)
                return min(fatigue, 1.0)
            
            return 0.0
            
        except Exception:
            return 0.0
    
    def _calculate_cultural_match(self, task_data: Dict[str, Any], cultural_background: str) -> float:
        """Calculate cultural match between task and annotator"""
        try:
            # Simple heuristic - can be enhanced with more sophisticated analysis
            task_content = task_data.get('content', '').lower()
            
            # Check for cultural indicators in content
            cultural_indicators = {
                'western': ['christmas', 'thanksgiving', 'halloween', 'easter'],
                'asian': ['chinese', 'japanese', 'korean', 'lunar new year'],
                'middle_eastern': ['ramadan', 'eid', 'arabic', 'islamic'],
                'indian': ['diwali', 'holi', 'hindu', 'sanskrit']
            }
            
            for culture, indicators in cultural_indicators.items():
                if any(indicator in task_content for indicator in indicators):
                    if culture in cultural_background.lower():
                        return 1.0
                    else:
                        return 0.3
            
            return 0.7  # Default neutral match
            
        except Exception:
            return 0.5
    
    def _calculate_language_match(self, task_data: Dict[str, Any], languages: List[str]) -> float:
        """Calculate language match between task and annotator"""
        try:
            task_content = task_data.get('content', '')
            
            # Simple language detection (can be enhanced)
            if not languages:
                return 0.5
            
            # Check if any of annotator's languages appear in content
            for language in languages:
                if language.lower() in task_content.lower():
                    return 1.0
            
            return 0.5  # Default neutral match
            
        except Exception:
            return 0.5
    
    async def _train_model(self):
        """Train the quality prediction model"""
        try:
            # Get training data from database
            training_data = await self._get_training_data()
            
            if len(training_data) < 50:  # Need minimum data
                logger.warning("Insufficient training data", count=len(training_data))
                return
            
            # Prepare features and targets
            X = []
            y = []
            
            for sample in training_data:
                features = await self._extract_features(sample['task_data'], sample['annotator_data'])
                X.append([features[col] for col in self.feature_columns])
                y.append(sample['actual_quality'])
            
            X = np.array(X)
            y = np.array(y)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train models
            self.rf_model.fit(X_train_scaled, y_train)
            self.anomaly_detector.fit(X_train_scaled)
            
            # Evaluate
            train_score = self.rf_model.score(X_train_scaled, y_train)
            test_score = self.rf_model.score(X_test_scaled, y_test)
            
            self.is_trained = True
            
            logger.info("Model trained successfully", 
                       train_score=train_score, 
                       test_score=test_score,
                       samples=len(training_data))
            
        except Exception as e:
            logger.error("Error training model", error=str(e))
    
    async def _get_training_data(self) -> List[Dict[str, Any]]:
        """Get training data from database"""
        try:
            db = next(get_db())
            
            # Get feedback samples with quality scores
            feedback_samples = db.query(FeedbackSample).filter(
                FeedbackSample.quality_score.isnot(None)
            ).limit(1000).all()
            
            training_data = []
            
            for sample in feedback_samples:
                # Get task data
                task = db.query(Task).filter(Task.task_id == sample.task_id).first()
                if not task:
                    continue
                
                # Get annotator data
                annotator = db.query(Annotator).filter(
                    Annotator.annotator_id == sample.annotator_id
                ).first()
                if not annotator:
                    continue
                
                task_data = {
                    'complexity_score': task.complexity_score,
                    'content': task.content,
                    'task_type': task.task_type
                }
                
                annotator_data = {
                    'skill_scores': annotator.skill_scores,
                    'performance_history': annotator.performance_history,
                    'cultural_background': annotator.cultural_background,
                    'languages': annotator.languages
                }
                
                training_data.append({
                    'task_data': task_data,
                    'annotator_data': annotator_data,
                    'actual_quality': sample.quality_score
                })
            
            return training_data
            
        except Exception as e:
            logger.error("Error getting training data", error=str(e))
            return []
    
    def _make_prediction(self, features: Dict[str, float]) -> float:
        """Make quality prediction using trained model"""
        try:
            feature_vector = [features[col] for col in self.feature_columns]
            feature_vector_scaled = self.scaler.transform([feature_vector])
            
            prediction = self.rf_model.predict(feature_vector_scaled)[0]
            return max(0.0, min(1.0, prediction))  # Clamp to [0, 1]
            
        except Exception as e:
            logger.error("Error making prediction", error=str(e))
            return 0.5
    
    def _detect_anomaly(self, features: Dict[str, float]) -> float:
        """Detect anomalies in the feature vector"""
        try:
            feature_vector = [features[col] for col in self.feature_columns]
            feature_vector_scaled = self.scaler.transform([feature_vector])
            
            # Isolation Forest returns -1 for anomalies, 1 for normal
            anomaly_score = self.anomaly_detector.decision_function(feature_vector_scaled)[0]
            
            # Convert to 0-1 scale where 1 is most anomalous
            return max(0.0, min(1.0, (1 - anomaly_score) / 2))
            
        except Exception as e:
            logger.error("Error detecting anomaly", error=str(e))
            return 0.5
    
    def _rule_based_prediction(self, features: Dict[str, float]) -> float:
        """Rule-based quality prediction when ML model is not available"""
        try:
            # Simple weighted average of features
            weights = {
                'task_complexity': -0.3,  # Higher complexity = lower quality
                'annotator_experience': 0.4,  # More experience = higher quality
                'cultural_match': 0.2,  # Better cultural match = higher quality
                'language_match': 0.2,  # Better language match = higher quality
                'annotator_fatigue': -0.3  # Higher fatigue = lower quality
            }
            
            base_score = 0.5
            for feature, weight in weights.items():
                if feature in features:
                    base_score += weight * features[feature]
            
            return max(0.0, min(1.0, base_score))
            
        except Exception:
            return 0.5
    
    def _calculate_confidence(self, features: Dict[str, float]) -> float:
        """Calculate confidence in the prediction"""
        try:
            # Confidence based on feature completeness and model training
            confidence = 0.5  # Base confidence
            
            if self.is_trained:
                confidence += 0.3
            
            # Check feature completeness
            missing_features = sum(1 for col in self.feature_columns if col not in features)
            completeness = 1 - (missing_features / len(self.feature_columns))
            confidence += 0.2 * completeness
            
            return max(0.0, min(1.0, confidence))
            
        except Exception:
            return 0.5
    
    def _identify_risk_factors(self, features: Dict[str, float]) -> List[str]:
        """Identify potential risk factors for quality"""
        risk_factors = []
        
        try:
            if features.get('task_complexity', 0) > 0.8:
                risk_factors.append('High task complexity')
            
            if features.get('annotator_experience', 0) < 0.3:
                risk_factors.append('Low annotator experience')
            
            if features.get('annotator_fatigue', 0) > 0.7:
                risk_factors.append('High annotator fatigue')
            
            if features.get('cultural_match', 0) < 0.4:
                risk_factors.append('Poor cultural match')
            
            if features.get('language_match', 0) < 0.4:
                risk_factors.append('Poor language match')
            
            if not risk_factors:
                risk_factors.append('No significant risks identified')
                
        except Exception:
            risk_factors.append('Risk assessment failed')
        
        return risk_factors
    
    def _generate_recommendations(self, features: Dict[str, Any], prediction: float) -> List[str]:
        """Generate recommendations based on prediction and features"""
        recommendations = []
        
        try:
            if prediction < 0.6:
                recommendations.append('Consider manual review for quality assurance')
            
            if features.get('task_complexity', 0) > 0.8:
                recommendations.append('Consider assigning to more experienced annotator')
            
            if features.get('annotator_fatigue', 0) > 0.7:
                recommendations.append('Consider giving annotator a break')
            
            if features.get('cultural_match', 0) < 0.4:
                recommendations.append('Consider cultural context training')
            
            if not recommendations:
                recommendations.append('No specific recommendations')
                
        except Exception:
            recommendations.append('Recommendation generation failed')
        
        return recommendations
    
    @log_execution_time
    async def update_model(self):
        """Update the model with new training data"""
        try:
            # Clear training status
            self.is_trained = False
            
            # Retrain model
            await self._train_model()
            
            logger.info("Model updated successfully")
            
        except Exception as e:
            logger.error("Error updating model", error=str(e))

# Global quality predictor instance
quality_predictor = QualityPredictor() 