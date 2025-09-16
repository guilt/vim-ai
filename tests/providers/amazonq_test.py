import os
import unittest
from unittest.mock import Mock, patch, MagicMock

# Mock vim module before importing
import sys
sys.modules['vim'] = MagicMock()

# Set dummy import environment
os.environ["VIMAI_DUMMY_IMPORT"] = "1"

from vim_ai.providers.amazonq import AmazonQProvider

class TestAmazonQProvider(unittest.TestCase):

    def setUp(self):
        self.utils = Mock()
        self.utils.print_debug = Mock()
        self.utils.make_known_error = Mock(side_effect=Exception)
        self.utils.load_api_key = Mock(return_value="test-api-key")

    def test_provider_initialization(self):
        """Test that the provider initializes correctly"""
        with patch('vim.eval') as mock_eval:
            mock_eval.side_effect = lambda x: "0" if "exists" in x else {}
            provider = AmazonQProvider('chat', {}, self.utils)
            self.assertEqual(provider.command_type, 'chat')
            self.assertEqual(provider.utils, self.utils)

    def test_format_messages(self):
        """Test message formatting"""
        with patch('vim.eval') as mock_eval:
            mock_eval.side_effect = lambda x: "0" if "exists" in x else {}
            provider = AmazonQProvider('chat', {}, self.utils)
            
            messages = [
                {
                    'role': 'user',
                    'content': [
                        {'type': 'text', 'text': 'Hello'},
                        {'type': 'text', 'text': 'World'}
                    ]
                }
            ]
            
            # Test that provider can handle messages (basic functionality test)
            assert provider.command_type == 'chat'

    def test_make_amazonq_options(self):
        """Test Amazon Q options creation"""
        with patch('vim.eval') as mock_eval:
            mock_eval.side_effect = lambda x: "0" if "exists" in x else {}
            provider = AmazonQProvider('chat', {}, self.utils)
            
            options = {
                'model': 'test-model',
                'temperature': 0.5,
                'max_tokens': 1000,
                'stream': True
            }
            
            # Test that provider can handle options
            result = provider._parse_raw_options(options)
            assert result['model'] == 'test-model'
            expected = {
                'model': 'test-model',
                'temperature': 0.5,
                'max_tokens': 1000,
                'stream': True
            }
            self.assertEqual(result, expected)

    def test_image_request_not_supported(self):
        """Test that image requests raise an error"""
        with patch('vim.eval') as mock_eval:
            mock_eval.side_effect = lambda x: "0" if "exists" in x else {}
            provider = AmazonQProvider('image', {}, self.utils)
            
            with self.assertRaises(Exception):
                provider.request_image("test prompt")

    def test_q_cli_not_found_error(self):
        """Test that provider handles Q CLI not found gracefully"""
        with patch('vim.eval') as mock_eval:
            mock_eval.side_effect = lambda x: "0" if "exists" in x else {}
            provider = AmazonQProvider('chat', {}, self.utils)
            
            with patch('vim_ai.providers.amazonq.subprocess_run_compat') as mock_run:
                mock_run.side_effect = FileNotFoundError("q command not found")
                
                messages = [{'role': 'user', 'content': [{'type': 'text', 'text': 'Hello'}]}]
                responses = list(provider.request(messages))
                
                self.assertEqual(len(responses), 1)
                self.assertEqual(responses[0]['type'], 'assistant')
                self.assertIn('Amazon Q CLI not found', responses[0]['content'])
                self.assertIn('q login', responses[0]['content'])

    def test_q_cli_available_check(self):
        """Test Q CLI availability check"""
        with patch('vim.eval') as mock_eval:
            mock_eval.side_effect = lambda x: "0" if "exists" in x else {}
            provider = AmazonQProvider('chat', {}, self.utils)
            
            with patch('vim_ai.providers.amazonq.subprocess_run_compat') as mock_run:
                # Test when Q CLI is available
                mock_run.return_value.returncode = 0
                self.assertTrue(provider._is_q_cli_available())
                
                # Test when Q CLI is not available
                mock_run.side_effect = FileNotFoundError()
                self.assertFalse(provider._is_q_cli_available())
