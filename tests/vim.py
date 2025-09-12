import os

dirname = os.path.dirname(__file__)

def eval(cmd):
    if cmd == 'g:vim_ai_debug_log_file':
        return '/tmp/vim_ai_debug.log'
    elif cmd == 'g:vim_ai_roles_config_file':
        return os.path.join(dirname, 'resources/roles.ini')
    elif cmd == 's:plugin_root':
        return os.path.abspath(os.path.join(dirname, '..'))
    elif cmd == 'getcwd()':
        return os.path.abspath(os.path.join(dirname, '..'))
    elif cmd == 'g:LoadToken()':
        return 'fn.secret'
    else:
        return None

def command(cmd):
    pass
