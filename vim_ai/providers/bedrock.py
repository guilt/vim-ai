import urllib.request
import os
import json
import base64
import subprocess
import sys
import vim

from vim_ai.provider_imports import setup_provider_imports
_imports = setup_provider_imports()
globals().update(_imports)
from vim_ai.ai_typing import Any, Sequence, Mapping, Iterator, List
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
        """Use AWS CLI to call Bedrock using the converse API"""
        try:
            # Convert messages to Bedrock converse format
            converse_messages = self._format_messages_for_converse(messages)
            
            # Get model ID - use Nova Micro as default since it supports on-demand
            model_id = self.options.get('model', os.environ.get('BEDROCK_MODEL', 'anthropic.claude-4-sonnet-20250109-v1:0'))
            
            # Prepare converse API payload
            payload = {
                "modelId": model_id,
                "messages": converse_messages,
                "inferenceConfig": {
                    "maxTokens": self.options.get('max_tokens', 4000),
                    "temperature": self.options.get('temperature', 0.7)
                }
            }
            
            # Add system message if present
            system_messages = [msg for msg in messages if msg.get('role') == 'system']
            if system_messages:
                # Use the last system message
                system_content = system_messages[-1].get('content', '')
                if isinstance(system_content, list):
                    # Extract text from content parts
                    system_text = '\n'.join([part.get('text', '') for part in system_content if part.get('type') == 'text'])
                else:
                    system_text = system_content
                
                if system_text.strip():
                    payload["system"] = [{"text": system_text}]
            
            # Use converse API
            cmd = [
                'aws', 'bedrock-runtime', 'converse',
                '--cli-input-json', json.dumps(payload),
                '--region', self.options.get('region', os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
            ]
            
            # Add profile if specified
            if 'profile' in self.options and self.options['profile']:
                cmd.extend(['--profile', self.options['profile']])
            
            result = subprocess_run_compat(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                error_msg = result.stderr
                # Handle specific error cases
                if "isn't supported" in error_msg and "inference profile" in error_msg:
                    yield {'type': 'assistant', 'content': 'Model {} requires an inference profile. Try using amazon.nova-micro-v1:0 or amazon.nova-lite-v1:0 instead.'.format(model_id)}
                else:
                    yield {'type': 'assistant', 'content': 'Bedrock error: {}'.format(error_msg)}
                return
            
            # Parse response
            try:
                response = json.loads(result.stdout)
            except json.JSONDecodeError as e:
                yield {'type': 'assistant', 'content': 'Error parsing Bedrock response: {}'.format(str(e))}
                return
            
            # Extract content from converse API response
            content = ""
            if 'output' in response and 'message' in response['output']:
                message = response['output']['message']
                if 'content' in message and len(message['content']) > 0:
                    content = message['content'][0].get('text', '')
            
            if content:
                yield {'type': 'assistant', 'content': content}
            else:
                yield {'type': 'assistant', 'content': 'No response content from Bedrock'}
                
        except subprocess.TimeoutExpired:
            yield {'type': 'assistant', 'content': 'Bedrock request timed out. The model may be processing a complex query.'}
        except Exception as e:
            yield {'type': 'assistant', 'content': 'Error connecting to Bedrock: {}'.format(str(e))}

    def _format_messages_for_converse(self, messages):
        """Convert vim-ai messages to Bedrock converse format"""
        converse_messages = []
        
        for msg in messages:
            role = msg['role']
            if role == 'system':
                # System messages are handled separately in converse API
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
                converse_messages.append({
                    'role': 'user' if role == 'user' else 'assistant',
                    'content': [{'text': content_text}]
                })
        
        return converse_messages

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
