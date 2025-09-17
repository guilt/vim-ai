from vim_ai.roles import load_ai_role_names

def test_role_completion():
    role_names = load_ai_role_names('complete')
    assert set(role_names) == {
        'test-role-simple',
        'test-role',
        'deprecated-test-role-simple',
        'deprecated-test-role',
        # context-aware roles
        'codebase',
        'refactor',
        'debug',
        'review',
        'architect',
        'test',
        'docs',
        'git',
        'project',
    }

def test_role_chat_only():
    role_names = load_ai_role_names('chat')
    assert set(role_names) == {
        'test-role-simple',
        'test-role',
        'chat-only-role',
        'deprecated-test-role-simple',
        'deprecated-test-role',
        'all_params',
        # default roles
        'right',
        'below',
        'tab',
        'populate',
        'populate-all',
        # context-aware roles
        'codebase',
        'refactor',
        'debug',
        'review',
        'architect',
        'test',
        'docs',
        'git',
        'project',
    }

def test_explicit_image_roles():
    role_names = load_ai_role_names('image')
    assert set(role_names) == { 'hd-image', 'hd', 'natural' }
