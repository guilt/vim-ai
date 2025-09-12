let s:plugin_root = expand('<sfile>:p:h:h')

" Global provider setting - defaults to openai if not specified
if !exists("g:vim_ai_provider")
  let g:vim_ai_provider = exists('$VIM_AI_PROVIDER') ? $VIM_AI_PROVIDER : "openai"
endif

" Load provider-specific configurations
source <sfile>:p:h/vim_ai_config/openai.vim
source <sfile>:p:h/vim_ai_config/bedrock.vim
source <sfile>:p:h/vim_ai_config/amazonq.vim

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

let g:vim_ai_complete_default = {
\  "provider": g:vim_ai_provider,
\  "prompt": "",
\  "options": {
\    "selection_boundary": "#####",
\    "initial_prompt": s:initial_complete_prompt,
\  },
\  "ui": {
\    "paste_mode": 1,
\  },
\}
let g:vim_ai_edit_default = {
\  "provider": g:vim_ai_provider,
\  "prompt": "",
\  "options": {
\    "selection_boundary": "#####",
\    "initial_prompt": s:initial_complete_prompt,
\  },
\  "ui": {
\    "paste_mode": 1,
\  },
\}
let g:vim_ai_chat_default = {
\  "provider": g:vim_ai_provider,
\  "prompt": "",
\  "options": {
\    "selection_boundary": "",
\    "initial_prompt": s:initial_chat_prompt,
\  },
\  "ui": {
\    "open_chat_command": "preset_below",
\    "scratch_buffer_keep_open": 0,
\    "populate_options": 0,
\    "populate_all_options": 0,
\    "force_new_chat": 0,
\    "paste_mode": 1,
\  },
\}
let g:vim_ai_image_default = {
\  "provider": g:vim_ai_provider,
\  "prompt": "",
\  "options": {
\  },
\  "ui": {
\    "download_dir": "",
\  },
\}

if !exists("g:vim_ai_open_chat_presets")
  let g:vim_ai_open_chat_presets = {
  \  "preset_below": "below new",
  \  "preset_tab": "tabnew",
  \  "preset_right": "rightbelow 55vnew | setlocal noequalalways | setlocal winfixwidth",
  \}
endif

if !exists("g:vim_ai_chat_markdown")
  let g:vim_ai_chat_markdown = 0
endif

if !exists("g:vim_ai_debug")
  let g:vim_ai_debug = 0
endif

if !exists("g:vim_ai_debug_log_file")
  let g:vim_ai_debug_log_file = "/tmp/vim_ai_debug.log"
endif
if !exists("g:vim_ai_token_file_path")
  let g:vim_ai_token_file_path = "~/.config/openai.token"
endif
if !exists("g:vim_ai_token_load_fn")
  let g:vim_ai_token_load_fn = ""
endif
if !exists("g:vim_ai_roles_config_file")
  let g:vim_ai_roles_config_file = s:plugin_root . "/roles-example.ini"
endif
if !exists("g:vim_ai_async_chat")
  let g:vim_ai_async_chat = 1
endif

function! vim_ai_config#ExtendDeep(defaults, override) abort
  let l:result = a:defaults
  for [l:key, l:value] in items(a:override)
    if type(get(l:result, l:key)) is v:t_dict && type(l:value) is v:t_dict
      call vim_ai_config#ExtendDeep(l:result[l:key], l:value)
    else
      let l:result[l:key] = l:value
    endif
  endfor
  return l:result
endfunction

function! s:MakeConfig(config_name) abort
  let l:defaults = copy(g:[a:config_name . "_default"])
  let l:override = exists("g:" . a:config_name) ? g:[a:config_name] : {}
  let g:[a:config_name] = vim_ai_config#ExtendDeep(l:defaults, l:override)
endfunction

call s:MakeConfig("vim_ai_chat")
call s:MakeConfig("vim_ai_complete")
call s:MakeConfig("vim_ai_image")
call s:MakeConfig("vim_ai_edit")

function! vim_ai_config#load()
  " nothing to do - triggers autoloading of this file
endfunction
