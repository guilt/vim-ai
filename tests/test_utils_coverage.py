import os
import sys
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from vim_ai.utils import (
    load_module_compat, handle_completion_error, KnownError, 
    make_options, parse_include_paths, is_image_path
)

def test_load_module_compat():
    """Test module loading functionality"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write('test_var = "hello"')
        f.flush()
        
        try:
            module = load_module_compat('test_module', f.name)
            assert module.test_var == "hello"
        finally:
            os.unlink(f.name)

def test_handle_completion_error():
    """Test error handling"""
    try:
        handle_completion_error('test_provider', Exception('test error'))
        assert False, "Should have raised exception"
    except Exception as e:
        assert str(e) == 'test error'

def test_make_options():
    """Test options creation"""
    opts = make_options({"key": "value"})
    assert opts["key"] == "value"

def test_parse_include_paths():
    """Test file path parsing"""
    paths = parse_include_paths("test.txt")
    assert isinstance(paths, list)

def test_is_image_path():
    """Test image detection"""
    assert is_image_path("test.jpg") == True
    assert is_image_path("test.txt") == False
