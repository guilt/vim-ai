" Bedrock provider configuration
let g:vim_ai_bedrock_text_model = exists('$BEDROCK_MODEL') ? $BEDROCK_MODEL : 'amazon.nova-micro-v1:0'
let g:vim_ai_bedrock_image_model = exists('$BEDROCK_IMAGE_MODEL') ? $BEDROCK_IMAGE_MODEL : 'amazon.nova-canvas-v1:0'
let g:vim_ai_bedrock_region = exists('$AWS_DEFAULT_REGION') ? $AWS_DEFAULT_REGION : 'us-east-1'
let g:vim_ai_bedrock_profile = exists('$AWS_PROFILE') ? $AWS_PROFILE : ''
let g:vim_ai_bedrock_max_tokens = exists('$BEDROCK_MAX_TOKENS') ? $BEDROCK_MAX_TOKENS : (exists('$MAX_TOKENS') ? $MAX_TOKENS : 4000)

let s:bedrock_complete_prompt =<< trim END
>>> system

You are a general assistant. Answer shortly, concisely and only what you are asked. Do not provide any explanation or comments if not requested. If you answer in a code, do not wrap it in markdown code block.
END

let s:bedrock_chat_prompt =<< trim END
>>> system

You are a general assistant. Answer shortly, concisely and only what you are asked. Do not provide any explanation or comments if not requested. If you attach a code block add syntax type after ``` to enable syntax highlighting.
END

let g:vim_ai_bedrock_complete = {
\  "model": g:vim_ai_bedrock_text_model,
\  "max_tokens": g:vim_ai_bedrock_max_tokens,
\  "temperature": 0.1,
\  "region": g:vim_ai_bedrock_region,
\  "profile": g:vim_ai_bedrock_profile,
\  "request_timeout": 30,
\  "initial_prompt": s:bedrock_complete_prompt,
\}
let g:vim_ai_bedrock_edit = g:vim_ai_bedrock_complete
let g:vim_ai_bedrock_chat = {
\  "model": g:vim_ai_bedrock_text_model,
\  "max_tokens": g:vim_ai_bedrock_max_tokens,
\  "temperature": 0.7,
\  "region": g:vim_ai_bedrock_region,
\  "profile": g:vim_ai_bedrock_profile,
\  "request_timeout": 30,
\  "initial_prompt": s:bedrock_chat_prompt,
\}
let g:vim_ai_bedrock_image = {
\  "model": g:vim_ai_bedrock_image_model,
\  "region": g:vim_ai_bedrock_region,
\  "profile": g:vim_ai_bedrock_profile,
\  "width": 1024,
\  "height": 1024,
\  "request_timeout": 60,
\}
