import re


def is_lexing_error(e: Exception) -> bool:
    return type(e).__name__ == 'LexingError'


def _get_exception_message_regex(e: Exception) -> re.Pattern:
    return re.compile(rf'(?:{type(e).__name__}(?:[:]\s+)?)?(.*)')


def get_exception_message(e: Exception) -> str:
    if hasattr(e, 'message'):
        return e.message
    pattern = _get_exception_message_regex(e)
    default_message = str(e)
    match = pattern.match(default_message)
    return match.group(1) or default_message
