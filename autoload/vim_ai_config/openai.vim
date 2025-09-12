" OpenAI provider configuration
let g:vim_ai_endpoint_url = exists('$OPENAI_ENDPOINT_URL') ? $OPENAI_ENDPOINT_URL : 'https://api.openai.com/v1'
let g:vim_ai_default_text_model = exists('$OPENAI_MODEL') ? $OPENAI_MODEL : 'gpt-4o'
let g:vim_ai_default_image_model = exists('$OPENAI_IMAGE_MODEL') ? $OPENAI_IMAGE_MODEL : 'dall-e-3'
let g:vim_ai_max_tokens = exists('$OPENAI_MAX_TOKENS') ? $OPENAI_MAX_TOKENS : 0

let s:initial_complete_prompt =<< trim END
>>> system

You are a general assistant.
Answer shortly, consisely and only what you are asked.
Do not provide any explanantion or comments if not requested.
If you answer in a code, do not wrap it in markdown code block.
END
let s:initial_chat_prompt =<< trim END
>>> system

You are a general assistant.
If you attach a code block add syntax type after ``` to enable syntax highlighting.
END

let g:vim_ai_openai_complete = {
\  "model": g:vim_ai_default_text_model,
\  "endpoint_url": g:vim_ai_endpoint_url."/chat/completions",
\  "max_tokens": g:vim_ai_max_tokens,
\  "max_completion_tokens": g:vim_ai_max_tokens,
\  "temperature": 0.1,
\  "request_timeout": 20,
\  "stream": 1,
\  "auth_type": "bearer",
\  "token_file_path": "",
\  "token_load_fn": "",
\  "selection_boundary": "#####",
\  "initial_prompt": s:initial_complete_prompt,
\  "frequency_penalty": "",
\  "logit_bias": "",
\  "logprobs": "",
\  "presence_penalty": "",
\  "reasoning_effort": "",
\  "seed": "",
\  "stop": "",
\  "top_logprobs": "",
\  "top_p": "",
\}
let g:vim_ai_openai_edit = g:vim_ai_openai_complete
let g:vim_ai_openai_chat = {
\  "model": g:vim_ai_default_text_model,
\  "endpoint_url": g:vim_ai_endpoint_url."/chat/completions",
\  "max_tokens": g:vim_ai_max_tokens,
\  "max_completion_tokens": g:vim_ai_max_tokens,
\  "temperature": 1,
\  "request_timeout": 20,
\  "stream": 1,
\  "auth_type": "bearer",
\  "token_file_path": "",
\  "token_load_fn": "",
\  "selection_boundary": "",
\  "initial_prompt": s:initial_chat_prompt,
\  "frequency_penalty": "",
\  "logit_bias": "",
\  "logprobs": "",
\  "presence_penalty": "",
\  "reasoning_effort": "",
\  "seed": "",
\  "stop": "",
\  "top_logprobs": "",
\  "top_p": "",
\}
let g:vim_ai_openai_image = {
\  "model": g:vim_ai_default_image_model,
\  "endpoint_url": g:vim_ai_endpoint_url."/images/generations",
\  "quality": "standard",
\  "size": "1024x1024",
\  "style": "vivid",
\  "request_timeout": 40,
\  "auth_type": "bearer",
\  "token_file_path": "",
\  "token_load_fn": "",
\}
