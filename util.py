def is_lexing_error(e: Exception) -> bool:
    return type(e).__name__ == 'LexingError'
