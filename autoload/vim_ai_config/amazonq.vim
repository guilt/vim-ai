" Amazon Q provider configuration
let g:vim_ai_amazonq_max_tokens = exists('$AMAZONQ_MAX_TOKENS') ? $AMAZONQ_MAX_TOKENS : (exists('$MAX_TOKENS') ? $MAX_TOKENS : 0)

let s:amazonq_complete_prompt =<< trim END
>>> system

You are a general assistant. Answer shortly, concisely and only what you are asked. Do not provide any explanation or comments if not requested. If you answer in a code, do not wrap it in markdown code block.
END

let s:amazonq_chat_prompt =<< trim END
>>> system

You are a general assistant. Answer shortly, concisely and only what you are asked. Do not provide any explanation or comments if not requested. If you attach a code block add syntax type after ``` to enable syntax highlighting.
END

let g:vim_ai_amazonq_complete = {
\  "model": "amazon.q-developer-agent-20240719-dev",
\  "endpoint_url": "https://q.amazonaws.com/api/v1/chat/completions",
\  "max_tokens": g:vim_ai_amazonq_max_tokens,
\  "temperature": 0.1,
\  "request_timeout": 30,
\  "stream": 1,
\  "auth_type": "bearer",
\  "token_file_path": expand("~/.config/amazonq.token"),
\  "token_load_fn": "",
\  "initial_prompt": s:amazonq_complete_prompt,
\}
let g:vim_ai_amazonq_edit = g:vim_ai_amazonq_complete
let g:vim_ai_amazonq_chat = {
\  "model": "amazon.q-developer-agent-20240719-dev",
\  "endpoint_url": "https://q.amazonaws.com/api/v1/chat/completions",
\  "max_tokens": g:vim_ai_amazonq_max_tokens,
\  "temperature": 0.7,
\  "request_timeout": 30,
\  "stream": 1,
\  "auth_type": "bearer",
\  "token_file_path": expand("~/.config/amazonq.token"),
\  "token_load_fn": "",
\  "initial_prompt": s:amazonq_chat_prompt,
\}
