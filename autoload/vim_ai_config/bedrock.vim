" Bedrock provider configuration
let g:vim_ai_bedrock_text_model = exists('$BEDROCK_MODEL') ? $BEDROCK_MODEL : 'anthropic.claude-4-sonnet-20250109-v1:0'
let g:vim_ai_bedrock_image_model = exists('$BEDROCK_IMAGE_MODEL') ? $BEDROCK_IMAGE_MODEL : 'amazon.nova-canvas-v1:0'
let g:vim_ai_bedrock_region = exists('$AWS_DEFAULT_REGION') ? $AWS_DEFAULT_REGION : 'us-east-1'
let g:vim_ai_bedrock_profile = exists('$AWS_PROFILE') ? $AWS_PROFILE : ''

let g:vim_ai_bedrock_complete = {
\  "model": g:vim_ai_bedrock_text_model,
\  "max_tokens": 4000,
\  "temperature": 0.1,
\  "region": g:vim_ai_bedrock_region,
\  "profile": g:vim_ai_bedrock_profile,
\  "request_timeout": 30,
\}
let g:vim_ai_bedrock_edit = g:vim_ai_bedrock_complete
let g:vim_ai_bedrock_chat = {
\  "model": g:vim_ai_bedrock_text_model,
\  "max_tokens": 4000,
\  "temperature": 0.7,
\  "region": g:vim_ai_bedrock_region,
\  "profile": g:vim_ai_bedrock_profile,
\  "request_timeout": 30,
\}
let g:vim_ai_bedrock_image = {
\  "model": g:vim_ai_bedrock_image_model,
\  "region": g:vim_ai_bedrock_region,
\  "profile": g:vim_ai_bedrock_profile,
\  "width": 1024,
\  "height": 1024,
\  "request_timeout": 60,
\}
