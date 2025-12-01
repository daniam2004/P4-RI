import re
import unicodedata
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
import nltk

try:
    stopwords.words("spanish")
except LookupError:
    nltk.download("stopwords")

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

def remove_stopwords(tokens: list) -> list:
    # Eliminar palabras vacías
    if not isinstance(tokens, list):
        return[]
    
    stop_words = set(stopwords.words("spanish"))
    clean_tokens = [t for t in tokens if t not in stop_words]

    return clean_tokens

def meaningful_tokens(tokens: list) -> list:
    # Filtramos tokens con significado
    if not isinstance(tokens, list):
        return[]
    
    clean = []
    for token in tokens:
        if len(token) <= 2:
            continue
        
        clean.append(token)
    
    return clean

stemmer = SnowballStemmer("spanish")
def stem_tokens(tokens: list) -> list:
    if not isinstance(tokens, list):
        return []
    
    stemmed = [stemmer.stem(token) for token in tokens]

    return stemmed