"""
Test script for the Dispute Resolution Agent
"""
import unittest
from unittest.mock import Mock, patch
from agent.dispute_agent import DisputeResolutionAgent

class TestDisputeResolutionAgent(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.sample_policies = [
            {
                "id": "test_policy_1",
                "title": "Test Billing Policy",
                "text": "Test policy for billing disputes"
            }
        ]
        
        # Create agent with mocked Bedrock client
        with patch('boto3.client'):
            self.agent = DisputeResolutionAgent(self.sample_policies)
            self.agent.bedrock_runtime = Mock()
    
    def test_agent_initialization(self):
        """Test that agent initializes correctly"""
        self.assertIsNotNone(self.agent)
        self.assertEqual(len(self.agent.policies), 1)
        self.assertEqual(self.agent.aws_region, "us-east-1")
    
    def test_classify_dispute_fallback(self):
        """Test dispute classification with fallback when Bedrock is unavailable"""
        # Mock Bedrock to be unavailable
        self.agent.bedrock_runtime = None
        
        result = self.agent.classify_dispute("test transaction", "test interaction")
        
        # Should return a valid classification even without Bedrock
        self.assertIn(result, ['fraud', 'billing', 'service'])
    
    def test_cosine_similarity(self):
        """Test cosine similarity calculation"""
        import numpy as np
        
        # Test with identical vectors
        vec1 = np.array([1, 0, 0])
        vec2 = np.array([1, 0, 0])
        similarity = self.agent._cosine_similarity(vec1, vec2)
        self.assertAlmostEqual(similarity, 1.0, places=5)
        
        # Test with orthogonal vectors
        vec3 = np.array([0, 1, 0])
        similarity = self.agent._cosine_similarity(vec1, vec3)
        self.assertAlmostEqual(similarity, 0.0, places=5)
        
        # Test with None vectors
        similarity = self.agent._cosine_similarity(None, vec1)
        self.assertEqual(similarity, 0.0)

class TestIntegration(unittest.TestCase):
    """Integration tests (require AWS credentials)"""
    
    @unittest.skipUnless(
        __name__ == '__main__' and '--integration' in __import__('sys').argv,
        "Integration tests require --integration flag and AWS credentials"
    )
    def test_bedrock_integration(self):
        """Test actual Bedrock integration (requires AWS credentials)"""
        policies = [
            {
                "id": "integration_test",
                "title": "Integration Test Policy", 
                "text": "This is a test policy for integration testing"
            }
        ]
        
        agent = DisputeResolutionAgent(policies)
        
        if agent.bedrock_runtime:
            # Test classification
            result = agent.classify_dispute(
                "Customer charged $100 unexpectedly",
                "Customer called complaining about unknown charge"
            )
            self.assertIn(result, ['fraud', 'billing', 'service'])
            print(f"Classification result: {result}")
        else:
            print("Skipping Bedrock integration test - no AWS credentials")

def run_basic_tests():
    """Run basic unit tests"""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDisputeResolutionAgent)
    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(suite)

def run_integration_tests():
    """Run integration tests"""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestIntegration)
    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(suite)

if __name__ == "__main__":
    import sys
    
    print("=== Dispute Resolution Agent Tests ===\n")
    
    if '--integration' in sys.argv:
        print("Running integration tests (requires AWS credentials)...")
        run_integration_tests()
    else:
        print("Running basic unit tests...")
        result = run_basic_tests()
        
        if result.wasSuccessful():
            print("\n✓ All tests passed!")
        else:
            print(f"\n✗ {len(result.failures)} test(s) failed")
            
        print("\nTo run integration tests: python test_agent.py --integration")
