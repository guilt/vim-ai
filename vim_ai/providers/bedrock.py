from collections.abc import Sequence, Mapping, Iterator
from typing import Any
import urllib.request
import os
import json
import base64
import vim
import subprocess
import sys

if "VIMAI_DUMMY_IMPORT" in os.environ:
    import sys
    import os
    
    # Load utils and ai_types modules
    utils_path = os.path.join(os.path.dirname(__file__), '..', 'utils.py')
    exec(open(utils_path).read(), globals())
    
    ai_types_path = os.path.join(os.path.dirname(__file__), '..', 'ai_types.py')
    vim_ai_types = load_module_compat('vim_ai_types', ai_types_path)
    
    # Functions are now available in globals()
    
    AIMessage = vim_ai_types.AIMessage
    AIResponseChunk = vim_ai_types.AIResponseChunk
    AIUtils = vim_ai_types.AIUtils
    AIProvider = vim_ai_types.AIProvider
    AICommandType = vim_ai_types.AICommandType
    AIImageResponseChunk = vim_ai_types.AIImageResponseChunk
else:
    from vim_ai.ai_types import AIMessage, AIResponseChunk, AIUtils, AIProvider, AICommandType, AIImageResponseChunk
    from vim_ai.utils import subprocess_run_compat

class BedrockProvider():

    default_options_varname_chat = "g:vim_ai_bedrock_chat"
    default_options_varname_complete = "g:vim_ai_bedrock_complete"
    default_options_varname_edit = "g:vim_ai_bedrock_edit"
    default_options_varname_image = "g:vim_ai_bedrock_image"

    def __init__(self, command_type, raw_options, utils) -> None:
        self.utils = utils
        self.command_type = command_type
        
        # Get default options from vim config
        raw_default_options = {}
        if hasattr(self, "default_options_varname_{}".format(command_type)):
            varname = getattr(self, "default_options_varname_{}".format(command_type))
            if vim.eval("exists('{}')".format(varname)) == "1":
                raw_default_options = vim.eval(varname)
        
        merged_options = raw_default_options.copy()
        merged_options.update(raw_options)
        self.options = self._parse_raw_options(merged_options)

    def request(self, messages):
        """Main request method that routes to appropriate implementation"""
        
        if self._is_aws_cli_available():
            return self._request_via_aws_cli(messages)
        else:
            # Fallback error message
            yield {'type': 'assistant', 'content': 'Bedrock provider requires AWS CLI with bedrock-runtime access.'}

    def _is_aws_cli_available(self):
        """Check if AWS CLI is available and configured"""
        try:
            result = subprocess_run_compat(['aws', 'sts', 'get-caller-identity'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _request_via_aws_cli(self, messages):
        """Use AWS CLI to call Bedrock"""
        try:
            # Convert messages to Bedrock format
            bedrock_messages = self._format_messages_for_bedrock(messages)
            
            # Prepare request payload
            payload = {
                "messages": bedrock_messages,
                "max_tokens": self.options.get('max_tokens', 4000),
                "temperature": self.options.get('temperature', 0.7),
                "anthropic_version": "bedrock-2023-05-31"
            }
            
            model_id = self.options.get('model', 
                os.environ.get('BEDROCK_MODEL', 'anthropic.claude-4-sonnet-20250109-v1:0'))
            
            # Check if streaming is enabled (opt-in for backward compatibility)
            use_streaming = self.options.get('stream', 0)
            
            # Prepare request payload
            payload_json = json.dumps(payload)
            payload_b64 = base64.b64encode(payload_json.encode('utf-8')).decode('utf-8')
            
            if use_streaming:
                # Call AWS Bedrock with streaming
                cmd = [
                    'aws', 'bedrock-runtime', 'invoke-model-with-response-stream',
                    '--model-id', model_id,
                    '--body', payload_b64,
                    '--region', self.options.get('region', os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
                ]
                
                # Add profile if specified
                if 'profile' in self.options and self.options['profile']:
                    cmd.extend(['--profile', self.options['profile']])
                
                # Stream response
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                
                for line in process.stdout:
                    if line.strip():
                        try:
                            # Parse streaming response
                            chunk = json.loads(line)
                            if 'chunk' in chunk and 'bytes' in chunk['chunk']:
                                chunk_data = base64.b64decode(chunk['chunk']['bytes']).decode('utf-8')
                                chunk_json = json.loads(chunk_data)
                                
                                if 'delta' in chunk_json and 'text' in chunk_json['delta']:
                                    text_delta = chunk_json['delta']['text']
                                    # Yield only the incremental delta, not accumulated content
                                    yield {'type': 'assistant', 'content': text_delta}
                        except (json.JSONDecodeError, KeyError):
                            continue
                
                process.wait()
                
                if process.returncode != 0:
                    stderr_output = process.stderr.read()
                    yield {'type': 'assistant', 'content': 'Bedrock streaming error: {}'.format(stderr_output)}
            else:
                # Non-streaming fallback (for tests and compatibility)
                cmd = [
                    'aws', 'bedrock-runtime', 'invoke-model',
                    '--model-id', model_id,
                    '--body', payload_b64,
                    '--region', self.options.get('region', os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')),
                    '/tmp/bedrock_response.json'
                ]
                
                # Add profile if specified
                if 'profile' in self.options and self.options['profile']:
                    cmd.extend(['--profile', self.options['profile']])
                
                result = subprocess_run_compat(cmd, capture_output=True, text=True, timeout=30)
                
                if result.returncode != 0:
                    yield {'type': 'assistant', 'content': 'Bedrock error: {}'.format(result.stderr)}
                    return
                
                # Read response
                with open('/tmp/bedrock_response.json', 'r') as f:
                    response = json.load(f)
                
                # Extract content
                if 'content' in response and len(response['content']) > 0:
                    content = response['content'][0].get('text', '')
                    yield {'type': 'assistant', 'content': content}
                else:
                    yield {'type': 'assistant', 'content': 'No response from Bedrock'}
                
        except subprocess.TimeoutExpired:
            yield {'type': 'assistant', 'content': 'Bedrock request timed out. The model may be processing a complex query.'}
        except Exception as e:
            yield {'type': 'assistant', 'content': 'Error connecting to Bedrock: {}'.format(str(e))}

    def _format_messages_for_bedrock(self, messages):
        """Convert vim-ai messages to Bedrock format"""
        bedrock_messages = []
        
        for msg in messages:
            role = msg['role']
            if role == 'system':
                # Bedrock doesn't have system role, prepend to first user message
                continue
                
            content_parts = msg.get('content', [])
            if isinstance(content_parts, str):
                content_text = content_parts
            else:
                # Extract text from content parts
                text_parts = []
                for part in content_parts:
                    if part.get('type') == 'text':
                        text_parts.append(part.get('text', ''))
                content_text = '\n'.join(text_parts)
            
            if content_text.strip():
                bedrock_messages.append({
                    'role': 'user' if role == 'user' else 'assistant',
                    'content': content_text
                })
        
        return bedrock_messages

    def request_image(self, prompt: str):
        """Generate image using Bedrock image models"""
        if not self._is_aws_cli_available():
            yield {'type': 'error', 'content': 'Bedrock provider requires AWS CLI with bedrock-runtime access.'}
            return
            
        try:
            # Use Stability AI SDXL model for image generation
            model_id = self.options.get('model', 
                os.environ.get('BEDROCK_IMAGE_MODEL', 'amazon.nova-canvas-v1:0'))
            
            payload = {
                "text_prompts": [{"text": prompt}],
                "cfg_scale": self.options.get('cfg_scale', 10),
                "seed": self.options.get('seed', 0),
                "steps": self.options.get('steps', 50),
                "width": self.options.get('width', 1024),
                "height": self.options.get('height', 1024)
            }
            
            cmd = [
                'aws', 'bedrock-runtime', 'invoke-model',
                '--model-id', model_id,
                '--body', json.dumps(payload),
                '--region', self.options.get('region', os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')),
                '/tmp/bedrock_image_response.json'
            ]
            
            # Add profile if specified
            if 'profile' in self.options and self.options['profile']:
                cmd.extend(['--profile', self.options['profile']])
            
            result = subprocess_run_compat(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                yield {'type': 'error', 'content': 'Bedrock image error: {}'.format(result.stderr)}
                return
            
            # Read response
            with open('/tmp/bedrock_image_response.json', 'r') as f:
                response = json.load(f)
            
            # Extract image data
            if 'artifacts' in response and len(response['artifacts']) > 0:
                image_data = response['artifacts'][0].get('base64', '')
                if image_data:
                    yield {'type': 'image', 'content': image_data, 'format': 'base64'}
                else:
                    yield {'type': 'error', 'content': 'No image data in Bedrock response'}
            else:
                yield {'type': 'error', 'content': 'No image artifacts in Bedrock response'}
                
        except subprocess.TimeoutExpired:
            yield {'type': 'error', 'content': 'Bedrock image generation timed out. Large images may take longer to generate.'}
        except Exception as e:
            yield {'type': 'error', 'content': 'Error generating image with Bedrock: {}'.format(str(e))}

    def _parse_raw_options(self, raw_options):
        return raw_options.copy()
