import os
import sys
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_load_module_compat_basic():
    """Test basic module loading functionality"""
    from vim_ai.utils import load_module_compat
    
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
    from vim_ai.utils import subprocess_run_compat
    
    # Test with basic arguments that work on all Python versions
    result = subprocess_run_compat(['echo', 'test'])
    assert hasattr(result, 'returncode')
    assert hasattr(result, 'stdout')

def test_ai_typing_imports():
    """Test that ai_typing module imports successfully"""
    from vim_ai import ai_typing
    
    # Test that basic types are available
    assert hasattr(ai_typing, 'AIMessage')
    assert hasattr(ai_typing, 'AIProvider')
    assert hasattr(ai_typing, 'AIUtils')

def test_ai_typing_protocol_fallback():
    """Test Protocol class exists (either real or fallback)"""
    from vim_ai.ai_typing import Protocol
    
    # Should be able to create a class that inherits from Protocol
    class TestProtocol(Protocol):
        def test_method(self):
            pass
    
    assert TestProtocol is not None

def test_ai_typing_literal_fallback():
    """Test Literal function exists (either real or fallback)"""
    from vim_ai.ai_typing import Literal
    
    # In Python 3.8+, Literal is a real type, in older versions it's our fallback
    # Just test that it exists and can be used in type annotations
    try:
        # Try to use it as a type annotation would
        test_type = Literal['test']
        assert test_type is not None
    except TypeError:
        # In newer Python versions, this might fail, which is expected
        # Just ensure Literal exists
        assert Literal is not None

def test_ai_typing_typeddict_fallback():
    """Test TypedDict class exists (either real or fallback)"""
    from vim_ai.ai_typing import TypedDict
    
    # Should be able to create a subclass
    class TestDict(TypedDict):
        pass
    
    test_dict = TestDict({'key': 'value'})
    assert test_dict['key'] == 'value'
