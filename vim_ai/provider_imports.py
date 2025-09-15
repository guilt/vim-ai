import os
import sys

def setup_provider_imports():
    """Common import setup for all providers"""
    if "VIMAI_DUMMY_IMPORT" in os.environ:
        from vim_ai.ai_typing import AIMessage, AIResponseChunk, AIUtils, AIProvider, AICommandType, AIImageResponseChunk, Any, Sequence, Mapping, Iterator
        
        # Load utils module
        utils_path = os.path.join(os.path.dirname(__file__), 'utils.py')
        exec(open(utils_path).read(), globals())
        
        ai_typing_path = os.path.join(os.path.dirname(__file__), 'ai_typing.py')
        vim_ai_typing = load_module_compat('vim_ai_typing', ai_typing_path)
        
        return {
            'AIMessage': vim_ai_typing.AIMessage,
            'AIResponseChunk': vim_ai_typing.AIResponseChunk,
            'AIUtils': vim_ai_typing.AIUtils,
            'AIProvider': vim_ai_typing.AIProvider,
            'AICommandType': vim_ai_typing.AICommandType,
            'AIImageResponseChunk': vim_ai_typing.AIImageResponseChunk,
            'Any': Any,
            'Sequence': Sequence,
            'Mapping': Mapping,
            'Iterator': Iterator,
            'subprocess_run_compat': globals().get('subprocess_run_compat')
        }
    else:
        from vim_ai.ai_typing import Any, Sequence, Mapping, Iterator
        from vim_ai.utils import subprocess_run_compat
        
        # Load utils module
        utils_path = os.path.join(os.path.dirname(__file__), 'utils.py')
        exec(open(utils_path).read(), globals())
        
        ai_typing_path = os.path.join(os.path.dirname(__file__), 'ai_typing.py')
        vim_ai_typing = load_module_compat('vim_ai_typing', ai_typing_path)
        
        return {
            'AIMessage': vim_ai_typing.AIMessage,
            'AIResponseChunk': vim_ai_typing.AIResponseChunk,
            'AIUtils': vim_ai_typing.AIUtils,
            'AIProvider': vim_ai_typing.AIProvider,
            'AICommandType': vim_ai_typing.AICommandType,
            'AIImageResponseChunk': vim_ai_typing.AIImageResponseChunk,
            'Any': Any,
            'Sequence': Sequence,
            'Mapping': Mapping,
            'Iterator': Iterator,
            'subprocess_run_compat': subprocess_run_compat
        }
