import urllib.request
import os
import json
import vim
import subprocess
import sys

from vim_ai.provider_imports import setup_provider_imports
_imports = setup_provider_imports()
globals().update(_imports)
from vim_ai.ai_typing import Any, Sequence, Mapping, Iterator

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
        
        self.utils.print_debug("amazonq: Using Q CLI")
        return self._request_via_q_cli(messages)

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
            
            # Use q chat command with proper arguments
            cmd = ['q', 'chat', '--no-interactive']
            
            # Stream responses from Q CLI
            process = subprocess.Popen(cmd + [user_prompt], 
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                     text=True, bufsize=1, universal_newlines=True)
            
            # Stream output line by line, yielding incremental deltas
            import re
            response_content = ""
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                
                # Clean ANSI codes and prompt markers from this line
                clean_line = re.sub(r'\x1b\[[0-9;]*m', '', line)
                clean_line = re.sub(r'^>\s*', '', clean_line)
                
                # Accumulate response content
                response_content += clean_line
                
                # Yield the cleaned line as an incremental delta
                if clean_line.strip():
                    yield {'type': 'assistant', 'content': clean_line}
            
            process.wait()
            
            if process.returncode != 0:
                stderr_output = process.stderr.read()
                error_msg = stderr_output.strip() if stderr_output else "Unknown Q CLI error"
                self.utils.print_debug("amazonq: Q CLI error (code {}): {}", process.returncode, error_msg)
                
                # If we got no response content, yield the error
                if not response_content.strip():
                    yield {'type': 'assistant', 'content': 'Q Error: {}'.format(error_msg)}
                    
        except Exception as e:
            self.utils.print_debug("amazonq: Q CLI request failed: {}", str(e))
            yield {'type': 'assistant', 'content': 'Error connecting to Amazon Q: {}'.format(str(e))}

    def request_image(self, prompt: str):
        raise self.utils.make_known_error("Image generation is not supported by Amazon Q")

    def _parse_raw_options(self, raw_options):
        return raw_options.copy()
