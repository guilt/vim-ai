import os
import sys
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from vim_ai.utils import (
    is_image_path, parse_include_paths, KnownError, AIProviderUtils,
    make_options
)

def test_load_token_from_env_variable():
    """Test loading token from environment variable"""
    from vim_ai.utils import load_token_from_env_variable
    os.environ['TEST_TOKEN'] = 'test_value'
    try:
        token = load_token_from_env_variable('TEST_TOKEN')
        assert token == 'test_value'
    finally:
        del os.environ['TEST_TOKEN']

def test_load_token_from_file_path():
    """Test loading token from file"""
    from vim_ai.utils import load_token_from_file_path
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
    from vim_ai.utils import load_token_from_file_path
    token = load_token_from_file_path('')
    assert token is None

def test_load_token_from_fn_empty():
    """Test loading token from empty function"""
    from vim_ai.utils import load_token_from_fn
    token = load_token_from_fn('')
    assert token is None

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

def test_make_options_no_prompt():
    """Test make_options without initial_prompt"""
    options = {'other': 'value'}
    result = make_options(options)
    assert result['other'] == 'value'

def test_is_image_path_jpg():
    """Test image detection for jpg"""
    assert is_image_path('test.jpg') == True

def test_is_image_path_png():
    """Test image detection for png"""
    assert is_image_path('test.png') == True

def test_is_image_path_text():
    """Test image detection for text file"""
    assert is_image_path('test.txt') == False

def test_parse_include_paths_single():
    """Test parsing single file path"""
    paths = parse_include_paths('test.txt')
    assert isinstance(paths, list)

def test_encode_image_missing():
    """Test encoding missing image"""
    from vim_ai.utils import encode_image
    try:
        encode_image('/nonexistent/image.jpg')
        assert False, "Should raise exception"
    except:
        pass  # Expected to fail

def test_known_error():
    """Test KnownError exception"""
    error = KnownError('test message')
    assert str(error) == 'test message'

def test_ai_provider_utils():
    """Test AIProviderUtils class"""
    utils = AIProviderUtils()
    
    # Test make_known_error
    error = utils.make_known_error('test error')
    assert isinstance(error, KnownError)
    assert str(error) == 'test error'
