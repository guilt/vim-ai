import tempfile
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from vim_ai.utils import print_debug, _vimai_thread_is_debug_active, _vimai_thread_log_file_path

def test_print_debug():
    """Test that print_debug doesn't crash with syntax errors"""
    # Enable debug mode temporarily
    import vim_ai.utils
    original_debug = vim_ai.utils._vimai_thread_is_debug_active
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        vim_ai.utils._vimai_thread_is_debug_active = True
        vim_ai.utils._vimai_thread_log_file_path = f.name
        
        try:
            # This should not crash
            print_debug("test message")
        finally:
            vim_ai.utils._vimai_thread_is_debug_active = original_debug
            os.unlink(f.name)
