from vim_ai.utils import parse_chat_messages
import os

dirname = os.path.dirname(__file__)
root_dir = os.path.abspath(os.path.join(dirname, '..'))

def strip_text(txt):
    txt = txt.strip()
    lines = txt.splitlines()
    return "\n".join([line.lstrip() for line in lines])

def test_parse_user_message():
    chat_content = strip_text(
    """
    >>> user

    generate lorem ipsum
    """)
    actual_messages = parse_chat_messages(chat_content)
    assert [
        {
            'role': 'user',
            'content': [
                {
                    'type': 'text',
                    'text': 'generate lorem ipsum',
                },
            ],
        },
    ] == actual_messages


def test_parse_system_message():
    chat_content = strip_text("""
    >>> system

    you are general assystant

    >>> user

    generate lorem ipsum
    """)
    actual_messages = parse_chat_messages(chat_content)
    assert [
        {
            'role': 'system',
            'content': [
                {
                    'type': 'text',
                    'text': 'you are general assystant',
                },
            ],
        },
        {
            'role': 'user',
            'content': [
                {
                    'type': 'text',
                    'text': 'generate lorem ipsum',
                },
            ],
        },
    ] == actual_messages


def test_parse_two_user_messages():
    chat_content = strip_text(
    """
    >>> user

    generate lorem ipsum

    >>> user

    in english
    """)
    actual_messages = parse_chat_messages(chat_content)
    assert [
        {
            'role': 'user',
            'content': [
                {
                    'type': 'text',
                    'text': 'generate lorem ipsum',
                },
                {
                    'type': 'text',
                    'text': 'in english',
                },
            ],
        },
    ] == actual_messages

def test_parse_assistant_message():
    chat_content = strip_text("""
    >>> user

    generate lorem ipsum

    <<< assistant

    bla bla bla

    >>> user

    again
    """)
    actual_messages = parse_chat_messages(chat_content)
    assert [
        {
            'role': 'user',
            'content': [
                {
                    'type': 'text',
                    'text': 'generate lorem ipsum',
                },
            ],
        },
        {
            'role': 'assistant',
            'content': [
                {
                    'type': 'text',
                    'text': 'bla bla bla',
                },
            ],
        },
        {
            'role': 'user',
            'content': [
                {
                    'type': 'text',
                    'text': 'again',
                },
            ],
        },
    ] == actual_messages

def test_parse_omits_thinking_message():
    chat_content = strip_text("""
    >>> user

    generate lorem ipsum

    <<< thinking

    thinking...

    <<< assistant

    bla bla bla

    >>> user

    again
    """)
    actual_messages = parse_chat_messages(chat_content)
    assert [
        {
            'role': 'user',
            'content': [
                {
                    'type': 'text',
                    'text': 'generate lorem ipsum',
                },
            ],
        },
        {
            'role': 'assistant',
            'content': [
                {
                    'type': 'text',
                    'text': 'bla bla bla',
                },
            ],
        },
        {
            'role': 'user',
            'content': [
                {
                    'type': 'text',
                    'text': 'again',
                },
            ],
        },
    ] == actual_messages

def test_parse_include_single_file_message():
    chat_content = strip_text("""
    >>> user

    translate to human language

    >>> include

    {}/tests/resources/test1.include.txt

    <<< assistant

    it already is in human language

    >>> user

    try harder
    """.format(root_dir))
    messages = parse_chat_messages(chat_content)
    actual_messages = parse_chat_messages(chat_content)
    assert [
        {
            'role': 'user',
            'content': [
                {
                    'type': 'text',
                    'text': 'translate to human language',
                },
                {
                    'type': 'text',
                    'text': '==> {}/tests/resources/test1.include.txt <==\nhello world'.format(root_dir),
                },
            ],
        },
        {
            'role': 'assistant',
            'content': [
                {
                    'type': 'text',
                    'text': 'it already is in human language',
                },
            ],
        },
        {
            'role': 'user',
            'content': [
                {
                    'type': 'text',
                    'text': 'try harder',
                },
            ],
        },
    ] == actual_messages

def test_parse_include_multiple_files_message():
    chat_content = strip_text("""
    >>> user

    translate to human language

    >>> include

    {}/tests/resources/test1.include.txt
    tests/resources/test2.include.txt
    """.format(root_dir))
    messages = parse_chat_messages(chat_content)
    actual_messages = parse_chat_messages(chat_content)
    assert [
        {
            'role': 'user',
            'content': [
                {
                    'type': 'text',
                    'text': 'translate to human language',
                },
                {
                    'type': 'text',
                    'text': '==> {}/tests/resources/test1.include.txt <==\nhello world'.format(root_dir),
                },
                {
                    'type': 'text',
                    'text': '==> tests/resources/test2.include.txt <==\nvim is awesome',
                },
            ],
        },
    ] == actual_messages

def test_parse_include_glob_files_message():
    chat_content = strip_text("""
    >>> user

    translate to human language

    >>> include

    {}/tests/**/*.include.txt
    """.format(root_dir))
    actual_messages = parse_chat_messages(chat_content)
    assert [
        {
            'role': 'user',
            'content': [
                {
                    'type': 'text',
                    'text': 'translate to human language',
                },
                {
                    'type': 'text',
                    'text': '==> {}/tests/resources/test1.include.txt <==\nhello world'.format(root_dir),
                },
                {
                    'type': 'text',
                    'text': '==> {}/tests/resources/test2.include.txt <==\nvim is awesome'.format(root_dir),
                },
            ],
        },
    ] == actual_messages

def test_parse_include_image_message():
    chat_content = strip_text("""
    >>> user

    what is on the image?

    >>> include

    {}/tests/**/*.jpg
    """.format(root_dir))
    actual_messages = parse_chat_messages(chat_content)
    assert [
        {
            'role': 'user',
            'content': [
                {
                    'type': 'text',
                    'text': 'what is on the image?',
                },
                {
                    'type': 'image_url',
                    'image_url': {
                        'url': 'data:image/jpg;base64,aW1hZ2UgZGF0YQo='
                    },
                },
            ],
        },
    ] == actual_messages

def test_parse_include_image_with_files_message():
    chat_content = strip_text("""
    >>> include

    {}/tests/resources/test1.include.txt
    {}/tests/resources/image_file.jpg
    {}/tests/resources/test2.include.txt
    """.format(root_dir, root_dir, root_dir))
    actual_messages = parse_chat_messages(chat_content)
    assert [
        {
            'role': 'user',
            'content': [
                {
                    'type': 'text',
                    'text': '==> {}/tests/resources/test1.include.txt <==\nhello world'.format(root_dir),
                },
                {
                    'type': 'image_url',
                    'image_url': {
                        'url': 'data:image/jpg;base64,aW1hZ2UgZGF0YQo='
                    },
                },
                {
                    'type': 'text',
                    'text': '==> {}/tests/resources/test2.include.txt <==\nvim is awesome'.format(root_dir),
                },
            ],
        },
    ] == actual_messages

def test_parse_include_unsupported_binary_file():
    chat_content = strip_text("""
    >>> include

    {}/tests/resources/binary_file.bin
    {}/tests/resources/test1.include.txt
    """.format(root_dir, root_dir))
    actual_messages = parse_chat_messages(chat_content)
    assert [
        {
            'role': 'user',
            'content': [
                {
                    'type': 'text',
                    'text': '==> {}/tests/resources/binary_file.bin <==\nBinary file, cannot display'.format(root_dir),
                },
                {
                    'type': 'text',
                    'text': '==> {}/tests/resources/test1.include.txt <==\nhello world'.format(root_dir),
                },
            ],
        },
    ] == actual_messages
