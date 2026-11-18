import unicodedata


def normalize_text(value: str) -> str:
    """Normalise pour comparaison insensible à la casse et aux accents."""
    if not value:
        return ""
    decomposed = unicodedata.normalize("NFD", value)
    without_accents = "".join(
        char for char in decomposed if unicodedata.category(char) != "Mn"
    )
    return without_accents.casefold()
