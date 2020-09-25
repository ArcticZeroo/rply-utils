def is_lexing_error(e: Exception) -> bool:
    return e.__name__ == 'LexingError'
