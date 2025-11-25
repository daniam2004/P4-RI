import re
import unicodedata


def lexical_analysis(text: str) -> str:
    # Hacemos análisis léxico básico

    if not isinstance(text, str):
        return ""
    
    text = unicodedata.normalize("NFKC", text)
    text = text.lower()

    text = re.sub(r"[â-záéíóú0-9\s]", " ", text)

    text = re.sub(r"\s+", " ", text).strip()

    return text

