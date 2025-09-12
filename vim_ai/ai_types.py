import sys
from typing import Union, List, Tuple, Any, Dict

if sys.version_info >= (3, 9):
    from collections.abc import Sequence, Mapping, Iterator
else:
    from typing import Sequence, Mapping, Iterator

try:
    from typing import Protocol
except ImportError:
    # Fallback for Python < 3.8
    class Protocol:
        pass

try:
    from typing import Literal
except ImportError:
    # Fallback for Python < 3.8
    def Literal(*args):
        return str

try:
    from typing import TypedDict
except ImportError:
    # Fallback for Python < 3.8
    class TypedDict(dict):
        def __init_subclass__(cls, **kwargs):
            if sys.version_info >= (3, 6):
                super().__init_subclass__()

types_py_imported = True

# Use simple dict types for Python 3.5 compatibility
AITextContent = dict
AIImageUrlContent = dict
AIMessage = dict
AIResponseChunk = dict
AIImageResponseChunk = dict

AIMessageContent = Union[AITextContent, AIImageUrlContent]

class AIUtils(Protocol):
    def print_debug(self, text, *args):
        pass
    def make_known_error(self, message):
        pass
    def load_api_key(self, env_variable, token_file_path="", token_load_fn=""):
        pass

# Type aliases for compatibility
AICommandType = str  # Literal('chat', 'edit', 'complete', 'image')

class AIProvider(Protocol):

    # optional config variable names (used to populate all options)
    default_options_varname_chat = ""
    default_options_varname_complete = ""
    default_options_varname_edit = ""

    def __init__(self, command_type, raw_options, utils):
        pass

    def request(self, messages):
        pass

    def request_image(self, prompt):
        pass

    def _parse_raw_options(self, raw_options):
        pass
