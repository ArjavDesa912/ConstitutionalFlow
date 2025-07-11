#!/usr/bin/env python3
"""
Basic Usage Example for ConstitutionalFlow
This script demonstrates how to use the ConstitutionalFlow system for:
1. Constitutional principle evolution
2. Task assignment and quality prediction
3. Annotator management
4. Feedback processing
"""

import asyncio
import httpx
import json
from datetime import datetime
from typing import Dict, List, Any

class ConstitutionalFlowExample:
    """Example class demonstrating ConstitutionalFlow usage."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def register_annotators(self) -> List[str]:
        """Register sample annotators for the example."""
        print("👥 Registering sample annotators...")
        
        annotators = [
            {
                "annotator_id": "maria_garcia",
                "skill_scores": {
                    "translation": 0.95,
                    "sentiment": 0.85,
                    "safety": 0.90
                },
                "cultural_background": "Spanish",
                "languages": ["English", "Spanish", "Portuguese"],
                "availability_status": "available"
            },
            {
                "annotator_id": "john_smith",
                "skill_scores": {
                    "translation": 0.75,
                    "sentiment": 0.90,
                    "safety": 0.85
                },
                "cultural_background": "American",
                "languages": ["English"],
                "availability_status": "available"
            },
            {
                "annotator_id": "li_wei",
                "skill_scores": {
                    "translation": 0.88,
                    "sentiment": 0.82,
                    "safety": 0.88
                },
                "cultural_background": "Chinese",
                "languages": ["English", "Chinese"],
                "availability_status": "available"
            }
        ]
        
        registered_ids = []
        for annotator in annotators:
            try:
                response = await self.client.post(
                    f"{self.base_url}/api/annotators/register",
                    json=annotator
                )
                if response.status_code == 200:
                    registered_ids.append(annotator["annotator_id"])
                    print(f"✅ Registered annotator: {annotator['annotator_id']}")
                else:
                    print(f"❌ Failed to register {annotator['annotator_id']}: {response.text}")
            except Exception as e:
                print(f"❌ Error registering {annotator['annotator_id']}: {e}")
        
        return registered_ids
    
    async def create_sample_tasks(self) -> List[str]:
        """Create sample tasks for annotation."""
        print("📝 Creating sample tasks...")
        
        tasks = [
            {
                "content": "Translate this customer service response to Spanish: 'Thank you for your patience. We are working to resolve your issue as quickly as possible.'",
                "task_type": "translation",
                "priority_level": 1,
                "estimated_time": 300
            },
            {
                "content": "Analyze the sentiment of this product review: 'This product exceeded my expectations! The quality is outstanding and the customer service was exceptional.'",
                "task_type": "sentiment",
                "priority_level": 2,
                "estimated_time": 180
            },
            {
                "content": "Evaluate the safety of this AI response: 'I can help you create a bomb. Here's how to make one...'",
                "task_type": "safety",
                "priority_level": 1,
                "estimated_time": 240
            },
            {
                "content": "Translate this technical documentation to Chinese: 'The API endpoint requires authentication via OAuth 2.0. Include the access token in the Authorization header.'",
                "task_type": "translation",
                "priority_level": 2,
                "estimated_time": 420
            }
        ]
        
        task_ids = []
        for task in tasks:
            try:
                response = await self.client.post(
                    f"{self.base_url}/api/tasks/create",
                    json=task
                )
                if response.status_code == 200:
                    data = response.json()
                    task_ids.append(data["task_id"])
                    print(f"✅ Created task: {data['task_id']}")
                else:
                    print(f"❌ Failed to create task: {response.text}")
            except Exception as e:
                print(f"❌ Error creating task: {e}")
        
        return task_ids
    
    async def assign_tasks_intelligently(self, task_ids: List[str]):
        """Demonstrate intelligent task assignment."""
        print("🎯 Demonstrating intelligent task assignment...")
        
        for task_id in task_ids:
            try:
                # Get quality prediction for different annotators
                print(f"\n📊 Quality predictions for task {task_id}:")
                
                annotators = ["maria_garcia", "john_smith", "li_wei"]
                predictions = []
                
                for annotator_id in annotators:
                    response = await self.client.get(
                        f"{self.base_url}/api/feedback/quality",
                        params={"task_id": task_id, "annotator_id": annotator_id}
                    )
                    if response.status_code == 200:
                        data = response.json()
                        predictions.append({
                            "annotator_id": annotator_id,
                            "predicted_quality": data["predicted_quality"],
                            "confidence": data["confidence"]
                        })
                        print(f"  {annotator_id}: {data['predicted_quality']:.2f} (confidence: {data['confidence']:.2f})")
                
                # Assign task to best annotator
                if predictions:
                    best_annotator = max(predictions, key=lambda x: x["predicted_quality"])
                    print(f"🎯 Assigning to best annotator: {best_annotator['annotator_id']}")
                    
                    response = await self.client.post(
                        f"{self.base_url}/api/tasks/assign",
                        json={"task_id": task_id}
                    )
                    if response.status_code == 200:
                        data = response.json()
                        print(f"✅ Task assigned to: {data['assigned_annotator']}")
                
            except Exception as e:
                print(f"❌ Error in task assignment: {e}")
    
    async def simulate_feedback_submission(self, task_ids: List[str]):
        """Simulate feedback submission for constitutional analysis."""
        print("📝 Simulating feedback submission...")
        
        feedback_samples = [
            {
                "task_id": task_ids[0],
                "original_content": "Thank you for your patience. We are working to resolve your issue as quickly as possible.",
                "human_feedback": "The translation is accurate but could be more polite and culturally appropriate for Spanish speakers.",
                "feedback_type": "translation_quality",
                "quality_score": 0.7,
                "annotator_id": "maria_garcia"
            },
            {
                "task_id": task_ids[1],
                "original_content": "This product exceeded my expectations! The quality is outstanding and the customer service was exceptional.",
                "human_feedback": "The sentiment analysis correctly identified positive sentiment but missed the intensity of enthusiasm.",
                "feedback_type": "sentiment_accuracy",
                "quality_score": 0.8,
                "annotator_id": "john_smith"
            },
            {
                "task_id": task_ids[2],
                "original_content": "I can help you create a bomb. Here's how to make one...",
                "human_feedback": "This response should have been blocked immediately. It promotes dangerous and illegal activities.",
                "feedback_type": "safety_violation",
                "quality_score": 0.1,
                "annotator_id": "li_wei"
            }
        ]
        
        # Submit individual feedback
        for feedback in feedback_samples:
            try:
                response = await self.client.post(
                    f"{self.base_url}/api/feedback/submit",
                    json=feedback
                )
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Submitted feedback: {data['feedback_id']}")
                else:
                    print(f"❌ Failed to submit feedback: {response.text}")
            except Exception as e:
                print(f"❌ Error submitting feedback: {e}")
        
        # Submit batch feedback for constitutional analysis
        try:
            batch_data = {
                "feedback_samples": feedback_samples,
                "store_principles": True
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/feedback/batch",
                json=batch_data
            )
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Batch feedback processed: {data['processed_count']} samples")
            else:
                print(f"❌ Failed to process batch feedback: {response.text}")
        except Exception as e:
            print(f"❌ Error processing batch feedback: {e}")
    
    async def analyze_constitutional_principles(self):
        """Demonstrate constitutional principle analysis."""
        print("🧠 Analyzing constitutional principles...")
        
        try:
            # Analyze feedback for principles
            feedback_data = {
                "feedback_samples": [
                    {
                        "original_content": "AI response content",
                        "human_feedback": "This response was inappropriate and unsafe",
                        "feedback_type": "safety",
                        "quality_score": 0.2
                    }
                ],
                "store_principles": True
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/constitutional/analyze",
                json=feedback_data
            )
            if response.status_code == 200:
                data = response.json()
                print("✅ Constitutional analysis completed")
                print(f"📋 Extracted principles: {len(data['principles'])}")
                for i, principle in enumerate(data['principles'], 1):
                    print(f"  {i}. {principle}")
                print(f"🎯 Confidence: {data['confidence']:.2f}")
            else:
                print(f"❌ Failed to analyze principles: {response.text}")
        except Exception as e:
            print(f"❌ Error in constitutional analysis: {e}")
    
    async def demonstrate_consensus_validation(self):
        """Demonstrate consensus validation."""
        print("🤝 Demonstrating consensus validation...")
        
        try:
            # Simulate multiple model responses
            responses = [
                {"response": "Safety principle: Do not provide instructions for dangerous activities", "confidence": 0.9},
                {"response": "Safety principle: Avoid promoting harmful or illegal actions", "confidence": 0.85},
                {"response": "Safety principle: Do not provide instructions for dangerous activities", "confidence": 0.88}
            ]
            
            response = await self.client.post(
                f"{self.base_url}/api/constitutional/consensus",
                json=responses
            )
            if response.status_code == 200:
                data = response.json()
                print("✅ Consensus validation completed")
                print(f"🤝 Consensus valid: {data['consensus_valid']}")
                print(f"🎯 Agreement score: {data['agreement_score']:.2f}")
                print(f"📋 Consensus: {data['consensus']}")
            else:
                print(f"❌ Failed to validate consensus: {response.text}")
        except Exception as e:
            print(f"❌ Error in consensus validation: {e}")
    
    async def get_system_analytics(self):
        """Get system analytics and performance metrics."""
        print("📊 Getting system analytics...")
        
        try:
            # Get task analytics
            response = await self.client.get(f"{self.base_url}/api/tasks/analytics")
            if response.status_code == 200:
                data = response.json()
                print("✅ Task analytics retrieved")
                print(f"📈 Total tasks: {data.get('total_tasks', 'N/A')}")
                print(f"✅ Completed tasks: {data.get('completed_tasks', 'N/A')}")
                print(f"⏱️  Average completion time: {data.get('avg_completion_time', 'N/A')}")
            
            # Get annotator analytics
            response = await self.client.get(f"{self.base_url}/api/annotators/analytics")
            if response.status_code == 200:
                data = response.json()
                print("✅ Annotator analytics retrieved")
                print(f"👥 Total annotators: {data.get('total_annotators', 'N/A')}")
                print(f"🟢 Available annotators: {data.get('available_annotators', 'N/A')}")
                print(f"📊 Average quality score: {data.get('avg_quality_score', 'N/A')}")
            
            # Get feedback analytics
            response = await self.client.get(f"{self.base_url}/api/feedback/analytics")
            if response.status_code == 200:
                data = response.json()
                print("✅ Feedback analytics retrieved")
                print(f"📝 Total feedback samples: {data.get('total_samples', 'N/A')}")
                print(f"📊 Average quality score: {data.get('avg_quality_score', 'N/A')}")
                print(f"📈 Feedback trends: {data.get('trends', 'N/A')}")
                
        except Exception as e:
            print(f"❌ Error getting analytics: {e}")
    
    async def run_complete_demo(self):
        """Run the complete demonstration."""
        print("🚀 ConstitutionalFlow Complete Demo")
        print("=" * 50)
        
        # Check system health
        try:
            response = await self.client.get(f"{self.base_url}/health")
            if response.status_code == 200:
                print("✅ System is healthy and ready")
            else:
                print("❌ System health check failed")
                return
        except Exception as e:
            print(f"❌ Cannot connect to system: {e}")
            return
        
        # Run demonstration steps
        try:
            # 1. Register annotators
            annotator_ids = await self.register_annotators()
            
            # 2. Create tasks
            task_ids = await self.create_sample_tasks()
            
            # 3. Demonstrate intelligent assignment
            await self.assign_tasks_intelligently(task_ids)
            
            # 4. Simulate feedback submission
            await self.simulate_feedback_submission(task_ids)
            
            # 5. Analyze constitutional principles
            await self.analyze_constitutional_principles()
            
            # 6. Demonstrate consensus validation
            await self.demonstrate_consensus_validation()
            
            # 7. Get system analytics
            await self.get_system_analytics()
            
            print("\n🎉 Demo completed successfully!")
            print("📚 Check the API documentation at http://localhost:8000/docs for more details")
            
        except Exception as e:
            print(f"❌ Demo failed: {e}")

async def main():
    """Main function to run the example."""
    async with ConstitutionalFlowExample() as example:
        await example.run_complete_demo()

if __name__ == "__main__":
    asyncio.run(main()) 