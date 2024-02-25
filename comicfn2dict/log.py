"""Print log header."""


def print_log_header(label: str) -> None:
    """Print log header."""
    prefix = "-" * 3 + label
    suffix_len = 80 - len(prefix)
    suffix = "-" * suffix_len
    print(prefix + suffix)  # noqa: T201
