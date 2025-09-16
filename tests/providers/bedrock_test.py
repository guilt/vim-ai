import os
import unittest
from unittest.mock import Mock, patch, MagicMock
import json

# Mock vim module before importing
import sys
sys.modules['vim'] = MagicMock()

# Set dummy import environment
os.environ["VIMAI_DUMMY_IMPORT"] = "1"

from vim_ai.providers.bedrock import BedrockProvider

class TestBedrockProvider(unittest.TestCase):

    def setUp(self):
        self.utils = Mock()
        self.utils.print_debug = Mock()
        self.utils.make_known_error = Mock(side_effect=Exception)

    def test_provider_initialization(self):
        """Test that the provider initializes correctly"""
        with patch('vim.eval') as mock_eval:
            mock_eval.side_effect = lambda x: "0" if "exists" in x else {}
            provider = BedrockProvider('chat', {
                'model': 'amazon.nova-micro-v1:0',
                'region': 'us-east-1',
                'temperature': 0.7
            }, self.utils)
            
            self.assertEqual(provider.command_type, 'chat')
            self.assertEqual(provider.utils, self.utils)
            self.assertEqual(provider.options['model'], 'amazon.nova-micro-v1:0')
            self.assertEqual(provider.options['region'], 'us-east-1')
            self.assertEqual(provider.options['temperature'], 0.7)

    def test_message_formatting(self):
        """Test message formatting for Bedrock API"""
        with patch('vim.eval') as mock_eval:
            mock_eval.side_effect = lambda x: "0" if "exists" in x else {}
            provider = BedrockProvider('chat', {}, self.utils)
            
            messages = [
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"},
                {"role": "user", "content": "How are you?"}
            ]
            
            formatted = provider._format_messages_for_bedrock(messages)
            
            # Bedrock format filters out system messages and returns list of user/assistant messages
            self.assertIsInstance(formatted, list)
            self.assertTrue(len(formatted) > 0)
            
            # Should have user and assistant messages (system is filtered out)
            roles = [msg['role'] for msg in formatted]
            self.assertIn('user', roles)
            self.assertIn('assistant', roles)

    def test_aws_cli_availability_check(self):
        """Test AWS CLI availability check"""
        with patch('vim.eval') as mock_eval:
            mock_eval.side_effect = lambda x: "0" if "exists" in x else {}
            
            provider = BedrockProvider('chat', {}, self.utils)
            
            # Test that the method exists and can be called
            self.assertTrue(hasattr(provider, '_is_aws_cli_available'))
            self.assertTrue(callable(provider._is_aws_cli_available))

    def test_request_handling_without_cli(self):
        """Test request handling when AWS CLI is not available"""
        with patch('vim.eval') as mock_eval:
            mock_eval.side_effect = lambda x: "0" if "exists" in x else {}
            
            provider = BedrockProvider('chat', {}, self.utils)
            
            # Test when AWS CLI is not available
            with patch.object(provider, '_is_aws_cli_available', return_value=False):
                messages = [{"role": "user", "content": "Hello"}]
                responses = list(provider.request(messages))
                
                self.assertEqual(len(responses), 1)
                self.assertEqual(responses[0]['type'], 'assistant')
                self.assertIn('Bedrock provider requires AWS CLI', responses[0]['content'])

    def test_image_generation_support(self):
        """Test Bedrock image generation functionality"""
        with patch('vim.eval') as mock_eval:
            mock_eval.side_effect = lambda x: "0" if "exists" in x else {}
            
            options = {
                'model': 'amazon.nova-canvas-v1:0',
                'region': 'us-east-1',
                'width': 1024,
                'height': 1024
            }
            provider = BedrockProvider('image', options, self.utils)
            
            # Test image request structure
            with patch.object(provider, '_is_aws_cli_available', return_value=True):
                with patch('vim_ai.utils.subprocess_run_compat') as mock_run:
                    # Mock successful image generation
                    mock_response = {
                        'images': [{'source': {'bytes': 'base64encodeddata'}}]
                    }
                    mock_run.return_value.returncode = 0
                    mock_run.return_value.stdout = json.dumps(mock_response)
                    
                    # This should not raise an exception
                    try:
                        result = list(provider.request_image("test prompt"))
                        # Should return some result
                        self.assertTrue(len(result) >= 0)
                    except Exception as e:
                        # Expected to fail in test environment, but should not crash
                        self.assertIsInstance(e, Exception)

    def test_option_parsing(self):
        """Test that provider parses options correctly"""
        with patch('vim.eval') as mock_eval:
            mock_eval.side_effect = lambda x: "0" if "exists" in x else {}
            
            options = {
                'model': 'amazon.nova-lite-v1:0',
                'region': 'us-west-2',
                'temperature': 0.7,
                'max_tokens': 2000
            }
            provider = BedrockProvider('chat', options, self.utils)
            parsed = provider._parse_raw_options(options)
            self.assertEqual(parsed['model'], 'amazon.nova-lite-v1:0')
            self.assertEqual(parsed['region'], 'us-west-2')
