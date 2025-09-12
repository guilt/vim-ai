import vim

complete_py_imported = True

def run_ai_completition(context):
    update_thread_shared_variables()
    command_type = context['command_type']
    prompt = context['prompt']
    config = make_config(context['config'])
    config_options = config['options']
    config_ui = config['ui']
    roles = context['roles']

    try:
        if 'engine' in config and config['engine'] == 'complete':
            raise KnownError('complete engine is no longer supported')

        if prompt or roles:
            print('Completing...')
            vim.command("redraw")

            initial_prompt = config_options.get('initial_prompt', [])
            initial_prompt = '\n'.join(initial_prompt)
            chat_content = "{}\n\n>>> user\n\n{}".format(initial_prompt, prompt).strip()
            messages = parse_chat_messages(chat_content)
            print_debug("[{}] text:\n".format(command_type) + chat_content)

            provider_class = load_provider(config['provider'])
            provider = provider_class(command_type, config_options, ai_provider_utils)
            response_chunks = provider.request(messages)

            text_chunks = map(
                lambda c: c.get("content"),
                filter(lambda c: c['type'] == 'assistant', response_chunks), # omit `thinking` section
            )

            render_text_chunks(text_chunks, append_to_eol=command_type == 'complete')

            clear_echo_message()
    except BaseException as error:
        handle_completion_error(config['provider'], error)
        print_debug("[{}] error: {}", command_type, traceback.format_exc())
