from collections.abc import Sequence, Mapping, Iterator
from typing import Any
import urllib.request
import os
import json
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

class AmazonQProvider():

    default_options_varname_chat = "g:vim_ai_amazonq_chat"
    default_options_varname_complete = "g:vim_ai_amazonq_complete"
    default_options_varname_edit = "g:vim_ai_amazonq_edit"
    default_options_varname_image = "g:vim_ai_amazonq_image"

    def __init__(self, command_type, raw_options, utils) -> None:
        self.utils = utils
        self.command_type = command_type
        config_varname = getattr(self, "default_options_varname_{}".format(command_type))
        raw_default_options = vim.eval(config_varname) if vim.eval("exists('{}')".format(config_varname)) else {}
        merged_options = raw_default_options.copy()
        merged_options.update(raw_options)
        self.options = self._parse_raw_options(merged_options)

    def request(self, messages):
        """Main request method that routes to appropriate implementation"""
        
        # Check if Q CLI is available
        if not self._is_q_cli_available():
            return iter([{'type': 'assistant', 'content': 'Amazon Q CLI not found. Please install Q CLI and run "q login" to authenticate.'}])
        
        # Check if we're in Q CLI environment
        if self._is_q_cli_environment():
            self.utils.print_debug("amazonq: Using Q CLI environment")
            return self._request_via_q_cli(messages)
        else:
            self.utils.print_debug("amazonq: Q CLI not available")
            return iter([{'type': 'assistant', 'content': 'Amazon Q provider requires Q CLI environment.'}])

    def _is_q_cli_available(self):
        """Check if Q CLI command is available"""
        try:
            result = subprocess_run_compat(['q', '--help'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _is_q_cli_environment(self):
        """Check if we're running in Amazon Q CLI environment"""
        return (os.getenv('AWS_EXECUTION_ENV', '').startswith('AmazonQ-For-CLI') or 
                os.getenv('Q_SET_PARENT_CHECK') == '1')

    def _request_via_q_cli(self, messages):
        """Use Q CLI's chat functionality with streaming support"""
        try:
            # Extract the user's question from the last message
            user_prompt = ""
            for message in reversed(messages):
                if message['role'] == 'user':
                    user_prompt = '\n'.join([c['text'] for c in message['content'] if c['type'] == 'text'])
                    break
            
            if not user_prompt:
                yield {'type': 'assistant', 'content': 'No user prompt found'}
                return
            
            self.utils.print_debug("amazonq: Sending prompt to Q CLI: {}", user_prompt[:50] + "...")
            
            # Stream responses from Q CLI with tools disabled
            process = subprocess.Popen([
                'q', 'chat', '--trust-tools=', '--no-interactive'
            ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
              text=True, bufsize=1, universal_newlines=True)
            
            # Send the prompt
            process.stdin.write(user_prompt)
            process.stdin.close()
            
            # Stream output line by line, yielding incremental deltas
            import re
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                
                # Clean ANSI codes and prompt markers from this line
                clean_line = re.sub(r'\x1b\[[0-9;]*m', '', line)
                clean_line = re.sub(r'^>\s*', '', clean_line)
                
                # Yield the cleaned line as an incremental delta
                if clean_line.strip():
                    yield {'type': 'assistant', 'content': clean_line}
            
            process.wait()
            
            if process.returncode != 0:
                stderr_output = process.stderr.read()
                error_msg = stderr_output.strip() if stderr_output else "Q CLI error"
                yield {'type': 'assistant', 'content': 'Amazon Q error: {}'.format(error_msg)}
                    
        except Exception as e:
            self.utils.print_debug("amazonq: Q CLI request failed: {}", str(e))
            yield {'type': 'assistant', 'content': 'Error connecting to Amazon Q: {}'.format(str(e))}

    def request_image(self, prompt: str):
        raise self.utils.make_known_error("Image generation is not supported by Amazon Q")

    def _parse_raw_options(self, raw_options):
        return raw_options.copy()
