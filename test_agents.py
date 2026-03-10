"""
Unit tests for Self-Improving AI Agent Framework

Author: Selvagurunathan Ramalingam
Date: March 10, 2026
Version: 1.0

Description:
    Comprehensive test suite for all agent components and system functionality.
    Run with: python -m pytest test_agents.py
"""

import unittest
from unittest.mock import Mock, patch
from typing import Dict, Any

# Mock the requests module to avoid actual API calls
import sys
from unittest.mock import MagicMock

# Create mock for optional dependencies
sys.modules['chromadb'] = MagicMock()
sys.modules['chromadb.config'] = MagicMock()
sys.modules['fastapi'] = MagicMock()
sys.modules['pydantic'] = MagicMock()


class TestBaseAgent(unittest.TestCase):
    """Test suite for BaseAgent."""
    
    def test_base_agent_initialization(self):
        """Test BaseAgent initialization."""
        from agents.base_agent import BaseAgent
        
        # Create a concrete implementation for testing
        class TestAgent(BaseAgent):
            def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
                return {"result": "test"}
        
        agent = TestAgent(name="TestAgent", model="test-model")
        
        self.assertEqual(agent.name, "TestAgent")
        self.assertEqual(agent.model, "test-model")
        self.assertEqual(agent.temperature, 0.7)
    
    def test_base_agent_repr(self):
        """Test BaseAgent string representation."""
        from agents.base_agent import BaseAgent
        
        class TestAgent(BaseAgent):
            def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
                return {}
        
        agent = TestAgent(name="TestAgent", model="test-model")
        
        self.assertIn("TestAgent", repr(agent))
        self.assertIn("test-model", repr(agent))


class TestExecutorAgent(unittest.TestCase):
    """Test suite for ExecutorAgent."""
    
    @patch('requests.post')
    def test_executor_agent_initialization(self, mock_post):
        """Test ExecutorAgent initialization."""
        from agents.executor_agent import ExecutorAgent
        
        agent = ExecutorAgent(model="test-model")
        
        self.assertEqual(agent.name, "ExecutorAgent")
        self.assertEqual(agent.model, "test-model")
    
    @patch('requests.post')
    def test_executor_agent_execute(self, mock_post):
        """Test ExecutorAgent execute method."""
        from agents.executor_agent import ExecutorAgent
        
        # Mock the API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": "This is a test response"
        }
        mock_post.return_value = mock_response
        
        agent = ExecutorAgent(model="test-model")
        
        result = agent.execute({
            "task": "Test task",
            "prompt": "Test prompt"
        })
        
        self.assertTrue(result["success"])
        self.assertEqual(result["task"], "Test task")
        self.assertIn("response", result)


class TestEvaluatorAgent(unittest.TestCase):
    """Test suite for EvaluatorAgent."""
    
    @patch('requests.post')
    def test_evaluator_agent_initialization(self, mock_post):
        """Test EvaluatorAgent initialization."""
        from agents.evaluator_agent import EvaluatorAgent
        
        agent = EvaluatorAgent(model="test-model")
        
        self.assertEqual(agent.name, "EvaluatorAgent")
        self.assertEqual(agent.model, "test-model")
        self.assertEqual(agent.temperature, 0.3)
    
    @patch('requests.post')
    def test_evaluator_agent_execute(self, mock_post):
        """Test EvaluatorAgent execute method."""
        from agents.evaluator_agent import EvaluatorAgent
        
        # Mock the API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": "Score: 7\nFeedback: Good response\nStrengths: Clear writing\nWeaknesses: Could be more detailed"
        }
        mock_post.return_value = mock_response
        
        agent = EvaluatorAgent(model="test-model")
        
        result = agent.execute({
            "task": "Test task",
            "response": "Test response"
        })
        
        self.assertEqual(result["task"], "Test task")
        self.assertEqual(result["score"], 7)
        self.assertIn("feedback", result)


class TestOptimizerAgent(unittest.TestCase):
    """Test suite for OptimizerAgent."""
    
    @patch('requests.post')
    def test_optimizer_agent_initialization(self, mock_post):
        """Test OptimizerAgent initialization."""
        from agents.optimizer_agent import OptimizerAgent
        
        agent = OptimizerAgent(model="test-model")
        
        self.assertEqual(agent.name, "OptimizerAgent")
        self.assertEqual(agent.model, "test-model")
    
    @patch('requests.post')
    def test_optimizer_agent_create_base_prompt(self, mock_post):
        """Test OptimizerAgent base prompt creation."""
        from agents.optimizer_agent import OptimizerAgent
        
        agent = OptimizerAgent()
        
        prompt = agent._create_base_prompt("Test task")
        
        self.assertIn("Test task", prompt)
        self.assertIn("expert", prompt.lower())


class TestMemoryManager(unittest.TestCase):
    """Test suite for MemoryManager."""
    
    def test_memory_manager_initialization(self):
        """Test MemoryManager initialization."""
        from memory.memory_manager import MemoryManager
        
        manager = MemoryManager()
        
        self.assertIsNotNone(manager.vector_store)
        self.assertIsNotNone(manager.memory_index)
    
    def test_memory_manager_store_task_execution(self):
        """Test storing task execution."""
        from memory.memory_manager import MemoryManager
        
        manager = MemoryManager()
        
        memory_id = manager.store_task_execution(
            task="Test task",
            response="Test response"
        )
        
        # memory_id should be a non-empty string
        self.assertIsInstance(memory_id, str)
        self.assertGreater(len(memory_id), 0)
    
    def test_memory_manager_store_evaluation(self):
        """Test storing evaluation."""
        from memory.memory_manager import MemoryManager
        
        manager = MemoryManager()
        
        memory_id = manager.store_evaluation(
            task="Test task",
            score=8,
            feedback="Good response",
            suggestions=["Add more detail"]
        )
        
        self.assertIsInstance(memory_id, str)
        self.assertGreater(len(memory_id), 0)
    
    def test_memory_manager_store_prompt_version(self):
        """Test storing prompt version."""
        from memory.memory_manager import MemoryManager
        
        manager = MemoryManager()
        
        memory_id = manager.store_prompt_version(
            task="Test task",
            prompt="Test prompt",
            iteration=1,
            score=7
        )
        
        self.assertIsInstance(memory_id, str)
        self.assertGreater(len(memory_id), 0)
    
    def test_memory_manager_get_statistics(self):
        """Test getting statistics."""
        from memory.memory_manager import MemoryManager
        
        manager = MemoryManager()
        
        stats = manager.get_statistics()
        
        self.assertIn("total_memories", stats)
        self.assertIn("task_executions", stats)
        self.assertIn("evaluations", stats)


class TestSelfImprovingAgent(unittest.TestCase):
    """Test suite for SelfImprovingAIAgent."""
    
    @patch('requests.post')
    def test_agent_initialization(self, mock_post):
        """Test SelfImprovingAIAgent initialization."""
        from main import SelfImprovingAIAgent
        
        agent = SelfImprovingAIAgent(max_iterations=2)
        
        self.assertIsNotNone(agent.executor)
        self.assertIsNotNone(agent.evaluator)
        self.assertIsNotNone(agent.optimizer)
        self.assertIsNotNone(agent.memory)
        self.assertEqual(agent.max_iterations, 2)
    
    def test_agent_load_base_prompt(self):
        """Test loading base prompt."""
        from main import SelfImprovingAIAgent
        
        agent = SelfImprovingAIAgent()
        
        self.assertIsNotNone(agent.base_prompt)
        self.assertIsInstance(agent.base_prompt, str)
        self.assertGreater(len(agent.base_prompt), 0)
    
    def test_agent_create_task_prompt(self):
        """Test creating task-specific prompt."""
        from main import SelfImprovingAIAgent
        
        agent = SelfImprovingAIAgent()
        
        prompt = agent._create_task_prompt("Test task")
        
        self.assertIn("Test task", prompt)
        self.assertIn(agent.base_prompt, prompt)
    
    def test_agent_get_statistics(self):
        """Test getting agent statistics."""
        from main import SelfImprovingAIAgent
        
        agent = SelfImprovingAIAgent()
        
        stats = agent.get_statistics()
        
        self.assertIsInstance(stats, dict)
        self.assertIn("total_memories", stats)


class TestLogger(unittest.TestCase):
    """Test suite for Logger utility."""
    
    def test_logger_initialization(self):
        """Test Logger initialization."""
        from utils.logger import Logger
        
        logger = Logger("test_logger")
        
        self.assertIsNotNone(logger.logger)
        self.assertEqual(logger.logger.name, "test_logger")
    
    def test_logger_methods(self):
        """Test Logger methods."""
        from utils.logger import Logger
        
        logger = Logger("test_logger")
        
        # These should not raise exceptions
        logger.info("Test info message")
        logger.debug("Test debug message")
        logger.warning("Test warning message")
        logger.error("Test error message")


def run_tests():
    """Run all tests."""
    unittest.main(argv=[''], verbosity=2, exit=False)


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Self-Improving AI Agent - Test Suite")
    print("="*60 + "\n")
    
    run_tests()
