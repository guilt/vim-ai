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
                'model': 'anthropic.claude-4-sonnet-20250109-v1:0',
                'region': 'us-east-1',
                'temperature': 0.7
            }, self.utils)
            
            self.assertEqual(provider.command_type, 'chat')
            self.assertEqual(provider.utils, self.utils)
            self.assertEqual(provider.options['model'], 'anthropic.claude-4-sonnet-20250109-v1:0')
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
            
            bedrock_messages = provider._format_messages_for_bedrock(messages)
            
            # System messages should be filtered out
            expected = [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"},
                {"role": "user", "content": "How are you?"}
            ]
            
            self.assertEqual(bedrock_messages, expected)

    def test_message_formatting_converse(self):
        """Test message formatting for Bedrock converse API"""
        with patch('vim.eval') as mock_eval:
            mock_eval.side_effect = lambda x: "0" if "exists" in x else {}
            provider = BedrockProvider('chat', {}, self.utils)
            
            messages = [
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"},
                {"role": "user", "content": "How are you?"}
            ]
            
            converse_messages = provider._format_messages_for_converse(messages)
            
            # System messages should be filtered out in converse format
            expected = [
                {"role": "user", "content": [{"text": "Hello"}]},
                {"role": "assistant", "content": [{"text": "Hi there!"}]},
                {"role": "user", "content": [{"text": "How are you?"}]}
            ]
            
            self.assertEqual(converse_messages, expected)

    def test_message_formatting_converse_with_content_parts(self):
        """Test converse message formatting with content parts"""
        with patch('vim.eval') as mock_eval:
            mock_eval.side_effect = lambda x: "0" if "exists" in x else {}
            provider = BedrockProvider('chat', {}, self.utils)
            
            messages = [
                {
                    "role": "user", 
                    "content": [
                        {"type": "text", "text": "Hello"},
                        {"type": "text", "text": "World"}
                    ]
                }
            ]
            
            converse_messages = provider._format_messages_for_converse(messages)
            
            expected = [
                {"role": "user", "content": [{"text": "Hello\nWorld"}]}
            ]
            
            self.assertEqual(converse_messages, expected)

    @patch('vim_ai.providers.bedrock.subprocess_run_compat')
    def test_aws_cli_available_success(self, mock_run):
        """Test AWS CLI availability check when AWS is configured"""
        with patch('vim.eval') as mock_eval:
            mock_eval.side_effect = lambda x: "0" if "exists" in x else {}
            mock_run.return_value.returncode = 0
            
            provider = BedrockProvider('chat', {}, self.utils)
            result = provider._is_aws_cli_available()
            
            self.assertTrue(result)
            mock_run.assert_called_once_with(
                ['aws', 'sts', 'get-caller-identity'], 
                capture_output=True, 
                text=True, 
                timeout=10
            )

    @patch('vim_ai.providers.bedrock.subprocess_run_compat')
    def test_aws_cli_available_failure(self, mock_run):
        """Test AWS CLI availability check when AWS is not configured"""
        with patch('vim.eval') as mock_eval:
            mock_eval.side_effect = lambda x: "0" if "exists" in x else {}
            mock_run.return_value.returncode = 1
            
            provider = BedrockProvider('chat', {}, self.utils)
            result = provider._is_aws_cli_available()
            
            self.assertFalse(result)

    @patch('vim_ai.providers.bedrock.subprocess_run_compat')
    def test_aws_cli_not_found(self, mock_run):
        """Test AWS CLI availability check when AWS CLI is not installed"""
        with patch('vim.eval') as mock_eval:
            mock_eval.side_effect = lambda x: "0" if "exists" in x else {}
            mock_run.side_effect = FileNotFoundError()
            
            provider = BedrockProvider('chat', {}, self.utils)
            result = provider._is_aws_cli_available()
            
            self.assertFalse(result)

    @patch('vim_ai.providers.bedrock.subprocess_run_compat')
    def test_request_via_aws_cli_success(self, mock_run):
        """Test successful AWS CLI request using converse API"""
        with patch('vim.eval') as mock_eval:
            mock_eval.side_effect = lambda x: "0" if "exists" in x else {}
            
            # Mock successful AWS CLI call with converse API response
            mock_response = {
                "output": {
                    "message": {
                        "content": [{"text": "Hello! How can I help you?"}]
                    }
                }
            }
            mock_run.return_value.returncode = 0
            mock_run.return_value.stderr = ""
            mock_run.return_value.stdout = json.dumps(mock_response)
            
            provider = BedrockProvider('chat', {
                'model': 'anthropic.claude-4-sonnet-20250109-v1:0',
                'region': 'us-east-1'
            }, self.utils)
            
            messages = [{"role": "user", "content": "Hello"}]
            
            responses = list(provider._request_via_aws_cli(messages))
            
            self.assertEqual(len(responses), 1)
            self.assertEqual(responses[0]['type'], 'assistant')
            self.assertEqual(responses[0]['content'], "Hello! How can I help you?")

    @patch('vim_ai.providers.bedrock.subprocess_run_compat')
    def test_request_via_aws_cli_error(self, mock_run):
        """Test AWS CLI request with error"""
        with patch('vim.eval') as mock_eval:
            mock_eval.side_effect = lambda x: "0" if "exists" in x else {}
            mock_run.return_value.returncode = 1
            mock_run.return_value.stderr = "Access denied"
            
            provider = BedrockProvider('chat', {}, self.utils)
            messages = [{"role": "user", "content": "Hello"}]
            
            responses = list(provider._request_via_aws_cli(messages))
            
            self.assertEqual(len(responses), 1)
            self.assertEqual(responses[0]['type'], 'assistant')
            self.assertIn("Bedrock error: Access denied", responses[0]['content'])

    @patch('builtins.open')
    @patch('vim_ai.providers.bedrock.subprocess_run_compat')
    def test_image_request_success(self, mock_run, mock_open):
        """Test successful image generation"""
        with patch('vim.eval') as mock_eval:
            mock_eval.side_effect = lambda x: "0" if "exists" in x else {}
            
            # Mock successful AWS CLI call
            mock_run.return_value.returncode = 0
            mock_run.return_value.stderr = ""
            
            # Mock file read
            mock_response = {
                "artifacts": [{"base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="}]
            }
            mock_file = MagicMock()
            mock_file.__enter__.return_value.read.return_value = json.dumps(mock_response)
            mock_open.return_value = mock_file
            
            provider = BedrockProvider('image', {
                'model': 'stability.stable-diffusion-xl-v1',
                'region': 'us-east-1'
            }, self.utils)
            
            responses = list(provider.request_image("A beautiful sunset"))
            
            self.assertEqual(len(responses), 1)
            self.assertEqual(responses[0]['type'], 'image')
            self.assertEqual(responses[0]['format'], 'base64')
            self.assertTrue(len(responses[0]['content']) > 0)

    def test_image_request_without_aws(self):
        """Test image generation when AWS CLI is not available"""
        with patch('vim.eval') as mock_eval:
            mock_eval.side_effect = lambda x: "0" if "exists" in x else {}
            
            provider = BedrockProvider('image', {}, self.utils)
            
            with patch.object(provider, '_is_aws_cli_available', return_value=False):
                responses = list(provider.request_image("A beautiful sunset"))
                
                self.assertEqual(len(responses), 1)
                self.assertEqual(responses[0]['type'], 'error')
                self.assertIn("AWS CLI", responses[0]['content'])

    @patch('vim_ai.providers.bedrock.subprocess_run_compat')
    def test_aws_profile_support(self, mock_run):
        """Test AWS profile is passed to CLI"""
        with patch('vim.eval') as mock_eval:
            mock_eval.side_effect = lambda x: "0" if "exists" in x else {}
            mock_run.return_value.returncode = 0
            mock_run.return_value.stderr = ""
            
            provider = BedrockProvider('chat', {
                'profile': 'my-aws-profile',
                'region': 'eu-west-1'
            }, self.utils)
            
            messages = [{"role": "user", "content": "Hello"}]
            list(provider._request_via_aws_cli(messages))
            
            # Check that profile was added to command
            call_args = mock_run.call_args[0][0]
            self.assertIn('--profile', call_args)
            self.assertIn('my-aws-profile', call_args)
            self.assertIn('--region', call_args)
            self.assertIn('eu-west-1', call_args)
        """Test request method integration"""
        with patch('vim.eval') as mock_eval:
            mock_eval.side_effect = lambda x: "0" if "exists" in x else {}
            provider = BedrockProvider('chat', {}, self.utils)
            
            # Test that request method exists and can be called
            messages = [{"role": "user", "content": "Hello"}]
            
            # Get the generator
            response_gen = provider.request(messages)
            
            # Verify it's a generator
            self.assertTrue(hasattr(response_gen, '__iter__'))
            self.assertTrue(hasattr(response_gen, '__next__'))
            
            # Convert to list to consume the generator
            responses = list(response_gen)
            
            # The response count depends on AWS CLI availability and configuration
            # We just verify the method works without crashing
            self.assertIsInstance(responses, list)

    @patch('vim_ai.providers.bedrock.subprocess_run_compat')
    def test_aws_profile_support(self, mock_run):
        """Test AWS profile is passed to CLI"""
        with patch('vim.eval') as mock_eval:
            mock_eval.side_effect = lambda x: "0" if "exists" in x else {}
            mock_run.return_value.returncode = 0
            mock_run.return_value.stderr = ""
            
            provider = BedrockProvider('chat', {
                'profile': 'my-aws-profile',
                'region': 'eu-west-1'
            }, self.utils)
            
            messages = [{"role": "user", "content": "Hello"}]
            list(provider._request_via_aws_cli(messages))
            
            # Check that profile was added to command
            call_args = mock_run.call_args[0][0]
            self.assertIn('--profile', call_args)
            self.assertIn('my-aws-profile', call_args)
            self.assertIn('--region', call_args)
            self.assertIn('eu-west-1', call_args)

    @patch.object(BedrockProvider, '_is_aws_cli_available')
    def test_request_without_aws_available(self, mock_aws_available):
        """Test request method when AWS CLI is not available"""
        with patch('vim.eval') as mock_eval:
            mock_eval.side_effect = lambda x: "0" if "exists" in x else {}
            mock_aws_available.return_value = False
            
            provider = BedrockProvider('chat', {}, self.utils)
            messages = [{"role": "user", "content": "Hello"}]
            
            responses = list(provider.request(messages))
            
            self.assertEqual(len(responses), 1)
            self.assertIn("Bedrock provider requires AWS CLI", responses[0]['content'])

if __name__ == '__main__':
    unittest.main()
