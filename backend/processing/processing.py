import re
import unicodedata

def lexical_analysis(text: str) -> str:
    # Análisis léxico
    if not isinstance(text, str):
        return ""

    # Normalización Unicode
    text = unicodedata.normalize("NFKC", text)

    # Minúsculas
    text = text.lower()

    # Mantener solo letras (incluyendo tildes), números y espacios
    text = re.sub(r"[^a-záéíóúüñ0-9\s]", " ", text)

    # Quitar espacios múltiples
    text = re.sub(r"\s+", " ", text).strip()

    return text

def tokenize(text: str) -> list:
    # Tokenización.
    if not isinstance(text, str):
        return []
    
    tokens = text.split()

    return tokens