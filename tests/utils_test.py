import os
import sys
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from vim_ai.utils import (
    load_module_compat, handle_completion_error, KnownError, 
    make_options, parse_include_paths, is_image_path, print_debug,
    load_token_from_env_variable, load_token_from_file_path, 
    load_token_from_fn, encode_image, AIProviderUtils, subprocess_run_compat
)

# Debug tests
def test_print_debug():
    """Test that print_debug doesn't crash with syntax errors"""
    import vim_ai.utils
    original_debug = vim_ai.utils._vimai_thread_is_debug_active
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        vim_ai.utils._vimai_thread_is_debug_active = True
        vim_ai.utils._vimai_thread_log_file_path = f.name
        
        try:
            print_debug("test message")
        finally:
            vim_ai.utils._vimai_thread_is_debug_active = original_debug
            os.unlink(f.name)

# Compatibility tests
def test_load_module_compat():
    """Test module loading functionality"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write('test_var = "loaded"')
        f.flush()
        
        try:
            module = load_module_compat('test_module', f.name)
            assert module.test_var == "loaded"
        finally:
            os.unlink(f.name)

def test_subprocess_run_compat_exists():
    """Test that subprocess compatibility function exists and works"""
    result = subprocess_run_compat(['echo', 'test'])
    assert hasattr(result, 'returncode')
    assert hasattr(result, 'stdout')

# Token loading tests
def test_load_token_from_env_variable():
    """Test loading token from environment variable"""
    os.environ['TEST_TOKEN'] = 'test_value'
    try:
        token = load_token_from_env_variable('TEST_TOKEN')
        assert token == 'test_value'
    finally:
        del os.environ['TEST_TOKEN']

def test_load_token_from_file_path():
    """Test loading token from file"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write('file_token_value')
        f.flush()
        
        try:
            token = load_token_from_file_path(f.name)
            assert token == 'file_token_value'
        finally:
            os.unlink(f.name)

def test_load_token_from_file_path_empty():
    """Test loading from empty path"""
    token = load_token_from_file_path('')
    assert token is None

def test_load_token_from_fn_empty():
    """Test loading token from empty function"""
    token = load_token_from_fn('')
    assert token is None

# Options tests
def test_make_options():
    """Test options creation"""
    opts = make_options({"key": "value"})
    assert opts["key"] == "value"

def test_make_options_string_prompt():
    """Test make_options with string initial_prompt"""
    options = {'initial_prompt': 'line1\nline2'}
    result = make_options(options)
    assert result['initial_prompt'] == ['line1', 'line2']

def test_make_options_list_prompt():
    """Test make_options with list initial_prompt"""
    options = {'initial_prompt': ['line1', 'line2']}
    result = make_options(options)
    assert result['initial_prompt'] == ['line1', 'line2']

# File handling tests
def test_parse_include_paths():
    """Test file path parsing"""
    paths = parse_include_paths("test.txt")
    assert isinstance(paths, list)

def test_is_image_path():
    """Test image detection"""
    assert is_image_path("test.jpg") == True
    assert is_image_path("test.png") == True
    assert is_image_path("test.txt") == False

def test_encode_image_missing():
    """Test encoding missing image"""
    try:
        encode_image('/nonexistent/image.jpg')
        assert False, "Should raise exception"
    except:
        pass  # Expected to fail

# Error handling tests
def test_handle_completion_error():
    """Test error handling"""
    try:
        handle_completion_error('test_provider', Exception('test error'))
        assert False, "Should have raised exception"
    except Exception as e:
        assert str(e) == 'test error'

def test_known_error():
    """Test KnownError exception"""
    error = KnownError('test message')
    assert str(error) == 'test message'

def test_ai_provider_utils():
    """Test AIProviderUtils class"""
    utils = AIProviderUtils()
    error = utils.make_known_error('test error')
    assert isinstance(error, KnownError)
    assert str(error) == 'test error'
