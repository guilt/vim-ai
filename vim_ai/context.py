import vim
import re
import os
import configparser

if "PYTEST_VERSION" in os.environ:
    from .utils import *
else:
    try:
        from utils import DEFAULT_ROLE_NAME, read_role_files, parse_include_paths, enhance_roles_with_custom_function
    except ImportError:
        from .utils import DEFAULT_ROLE_NAME, read_role_files, parse_include_paths, enhance_roles_with_custom_function

context_py_imported = True

def merge_deep_recursive(target, source = {}):
    source = source.copy()
    for key, value in source.items():
        if isinstance(value, dict):
            target_child = target.setdefault(key, {})
            merge_deep_recursive(target_child, value)
        else:
            target[key] = value
    return target

def merge_deep(objects):
    result = {}
    for o in objects:
        merge_deep_recursive(result, o)
    return result

def is_deprecated_role_syntax(roles, role):
    deprecated_sections = [
        'options', 'options-complete', 'options-edit', 'options-chat',
        'ui', 'ui-complete', 'ui-edit', 'ui-chat',
    ]
    for section in deprecated_sections:
        if "{}.{}".format(role, section) in roles:
            return True
    return False

def load_roles_with_deprecated_syntax(roles, role):
    prompt = dict(roles[role]).get('prompt', '')
    return {
        'role_default': {
            'prompt': prompt,
            'options': dict(roles.get("{}.options".format(role), {})),
            'ui': dict(roles.get("{}.ui".format(role), {})),
        },
        'role_complete': {
            'prompt': prompt,
            'options': dict(roles.get("{}.options-complete".format(role), {})),
            'ui': dict(roles.get("{}.ui-complete".format(role), {})),
        },
        'role_edit': {
            'prompt': prompt,
            'options': dict(roles.get("{}.options-edit".format(role), {})),
            'ui': dict(roles.get("{}.ui-edit".format(role), {})),
        },
        'role_chat': {
            'prompt': prompt,
            'options': dict(roles.get("{}.options-chat".format(role), {})),
            'ui': dict(roles.get("{}.ui-chat".format(role), {})),
        },
    }

def parse_role_section(role):
    result = {}
    for key in role.keys():
        parts = key.split('.')
        structure = parts[:-1]
        primitive = parts[-1]
        obj = result
        for path in structure:
            if not path in obj:
                obj[path] = {}
            obj = obj[path]
        obj[primitive] = role.get(key)
    return result

def load_role_config(role):
    roles = read_role_files()
    roles = dict(roles)

    enhance_roles_with_custom_function(roles)

    postfixes = ["", ".complete", ".edit", ".chat", ".image"]
    if not any(["{}{}".format(role, postfix) in roles for postfix in postfixes]):
        raise Exception("Role `{}` not found".format(role))

    if is_deprecated_role_syntax(roles, role):
        return load_roles_with_deprecated_syntax(roles, role)

    return {
        'role_default': parse_role_section(roles.get(role, {})),
        'role_complete': parse_role_section(roles.get("{}.complete".format(role), {})),
        'role_edit': parse_role_section(roles.get("{}.edit".format(role), {})),
        'role_chat': parse_role_section(roles.get("{}.chat".format(role), {})),
        'role_image': parse_role_section(roles.get("{}.image".format(role), {})),
    }

def parse_role_names(prompt):
    chunks = re.split(r'[ :]+', prompt)
    roles = []
    for chunk in chunks:
        if not chunk.startswith("/"):
            break
        roles.append(chunk)
    return [raw_role[1:] for raw_role in roles]

def parse_prompt_and_role_config(user_instruction, command_type):
    user_instruction = user_instruction.strip()
    roles = parse_role_names(user_instruction)

    last_role = roles[-1] if roles else ''
    user_prompt = user_instruction[user_instruction.index(last_role) + len(last_role):].strip() # strip roles
    role_results = [load_role_config(role) for role in [DEFAULT_ROLE_NAME] + roles]
    parsed_role = merge_deep(role_results)
    config = merge_deep([
        parsed_role.get('role_default', {}),
        parsed_role.get('role_' + command_type, {}),
    ])
    role_prompt = config.get('prompt', '')
    return user_prompt, config, roles

def make_selection_boundary(user_selection, selection_boundary):
    if selection_boundary != '```':
        return selection_boundary, selection_boundary
    filetype = vim.eval('&filetype')
    if filetype and filetype != 'aichat':
        return selection_boundary + filetype, selection_boundary
    return selection_boundary, selection_boundary

def make_selection_prompt(user_selection, user_prompt, config_prompt, selection_boundary):
    if not user_prompt and not config_prompt:
        return user_selection
    elif user_selection:
        if selection_boundary and selection_boundary not in user_selection:
            left_boundary, right_boundary = make_selection_boundary(user_selection, selection_boundary)
            return "{}\n{}\n{}".format(left_boundary, user_selection, right_boundary)
        else:
            return user_selection
    return ''

def make_prompt(config_prompt, user_prompt, user_selection, selection_boundary):
    user_prompt = user_prompt.strip()
    delimiter = ":\n" if user_prompt and user_selection else ""
    user_selection = make_selection_prompt(user_selection, user_prompt, config_prompt, selection_boundary)
    prompt = "{}{}{}".format(user_prompt, delimiter, user_selection)
    if not config_prompt:
        return prompt
    delimiter = '' if prompt.startswith(':') else ':\n'
    prompt = "{}{}{}".format(config_prompt, delimiter, prompt)
    return prompt

def make_ai_context(params):
    config_default = params['config_default']
    config_extension = params['config_extension']
    user_instruction = params['user_instruction']
    user_selection = params['user_selection']
    command_type = params['command_type']

    user_prompt, role_config, roles = parse_prompt_and_role_config(user_instruction, command_type)
    final_config = merge_deep([config_default, config_extension, role_config])
    selection_boundary = final_config['options'].get('selection_boundary', '')
    config_prompt = final_config.get('prompt', '')
    prompt = make_prompt(config_prompt, user_prompt, user_selection, selection_boundary)

    return {
        'command_type': command_type,
        'config': final_config,
        'prompt': prompt,
        'roles': roles,
    }
