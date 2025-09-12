" Amazon Q provider configuration
let g:vim_ai_amazonq_complete = {
\  "model": "amazon.q-developer-agent-20240719-dev",
\  "endpoint_url": "https://q.amazonaws.com/api/v1/chat/completions",
\  "max_tokens": 4000,
\  "temperature": 0.1,
\  "request_timeout": 30,
\  "stream": 1,
\  "auth_type": "bearer",
\  "token_file_path": "~/.config/amazonq.token",
\  "token_load_fn": "",
\}
let g:vim_ai_amazonq_edit = g:vim_ai_amazonq_complete
let g:vim_ai_amazonq_chat = {
\  "model": "amazon.q-developer-agent-20240719-dev",
\  "endpoint_url": "https://q.amazonaws.com/api/v1/chat/completions",
\  "max_tokens": 4000,
\  "temperature": 0.7,
\  "request_timeout": 30,
\  "stream": 1,
\  "auth_type": "bearer",
\  "token_file_path": "~/.config/amazonq.token",
\  "token_load_fn": "",
\}
