from django.core.exceptions import ValidationError


def contains_error_code(exception: ValidationError, code: str) -> bool:
    """Return True if the given exception contains an error with the given error code."""
    if hasattr(exception, "code"):
        if exception.code == code:
            return True

    if hasattr(exception, "error_dict"):
        for errors_field in exception.error_dict.values():
            for error in errors_field:
                if error.code == code:
                    return True

    return False


def extract_error_messages(exception: ValidationError) -> list[str]:
    """Returns the error messages in the given object as a list of strings."""
    messages = []
    for message in exception:
        if isinstance(message, tuple):
            non_empty = [m for m in message[1] if m != "None"]
            messages.extend(non_empty)
        else:
            if message != "None":
                messages.append(message)
    return messages
